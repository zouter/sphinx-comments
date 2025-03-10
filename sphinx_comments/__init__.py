"""Add a hypothes.is overlay to your Sphinx site."""

import os
from textwrap import dedent

__version__ = "0.0.3"


def shp_static_path(app):
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "_static"))
    app.config.html_static_path.append(static_path)


def activate_comments(app, config):
    """Activate commenting on each page."""
    # Grab config instances
    com_config = app.config.comments_config.copy()
    if not isinstance(com_config, (dict, type(None))):
        raise ValueError("Comments configuration must be a dictionary.")

    ut_config = com_config.get("utterances")
    dk_config = com_config.get("dokieli")
    ht_config = com_config.get("hypothesis")
    gi_config = com_config.get("giscus")

    extra_config = {"async": "async"}

    # Hypothesis config
    if ht_config:
        # If hypothesis, we just need to load the js library
        app.add_js_file(
            "https://hypothes.is/embed.js", kind="hypothesis", **extra_config
        )

    # Dokieli config
    if dk_config:
        app.add_js_file(
            "https://dokie.li/scripts/dokieli.js", kind="dokieli", **extra_config
        )
        app.add_css_file("https://dokie.li/media/css/dokieli.css", media="all")

    # utterances config
    if ut_config:
        if "repo" not in ut_config:
            raise ValueError("To use utterances, you must provide a repository.")
        repo = ut_config["repo"]

        # Utterances requires a script + config in a specific place, so do this w/ JS
        dom = """
            var commentsRunWhenDOMLoaded = cb => {
            if (document.readyState != 'loading') {
                cb()
            } else if (document.addEventListener) {
                document.addEventListener('DOMContentLoaded', cb)
            } else {
                document.attachEvent('onreadystatechange', function() {
                if (document.readyState == 'complete') cb()
                })
            }
        }
        """
        issue_term = ut_config.get("issue-term", "pathname")
        theme = ut_config.get("theme", "github-light")
        label = ut_config.get("label", "💬 comment")
        crossorigin = ut_config.get("crossorigin", "anonymous")
        js = dedent(
            f"""
        {dom}
        var addUtterances = () => {{
            var script = document.createElement("script");
            script.type = "text/javascript";
            script.src = "https://utteranc.es/client.js";
            script.async = "async";

            script.setAttribute("repo", "{repo}");
            script.setAttribute("issue-term", "{issue_term}");
            script.setAttribute("theme", "{theme}");
            script.setAttribute("label", "{label}");
            script.setAttribute("crossorigin", "{crossorigin}");

            sections = document.querySelectorAll("div.section");
            if (sections !== null) {{
                section = sections[sections.length-1];
                section.appendChild(script);
            }}
        }}
        commentsRunWhenDOMLoaded(addUtterances);
        """
        )
        app.add_js_file(None, body=js, kind="utterances")

    app.add_js_file(
        "https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/js/bootstrap.bundle.min.js",
        kind="bootstrap",
    )

    # giscus config
    if gi_config:
        if "repo" not in gi_config:
            raise ValueError("To use giscus, you must provide a repository.")
        repo = gi_config["repo"]
        repo_id = gi_config["repo-id"]
        category = gi_config["category"]
        category_id = gi_config["category-id"]

        # Giscus requires a script + config in a specific place, so do this w/ JS
        dom = """
            var commentsRunWhenDOMLoaded = cb => {
            if (document.readyState != 'loading') {
                cb()
            } else if (document.addEventListener) {
                document.addEventListener('DOMContentLoaded', cb)
            } else {
                document.attachEvent('onreadystatechange', function() {
                if (document.readyState == 'complete') cb()
                })
            }
        }
        """

        issue_term = gi_config.get("issue-term", "pathname")
        theme = gi_config.get("theme", "light")
        crossorigin = gi_config.get("crossorigin", "anonymous")
        reactions = gi_config.get("reactions-enabled", "1")
        js = dedent(
            f"""
        {dom}
        var addGiscus = () => {{
            var script = document.createElement("script");
            script.type = "text/javascript";
            script.src = "https://giscus.app/client.js";
            script.async = "async";

            script.setAttribute("data-repo", "{repo}");
            script.setAttribute("data-repo-id", "{repo_id}MDEwOlJlcG9zaXRvcnkyOTEwNjgxODg=");
            script.setAttribute("data-theme", "{theme}");
            script.setAttribute("data-category", "{category}");
            script.setAttribute("data-category-id", "{category_id}");
            script.setAttribute("data-mapping", "pathname");
            script.setAttribute("data-reactions-enabled", "{reactions}");
            script.setAttribute("crossorigin", "{crossorigin}");

            sections = document.querySelectorAll("div.prev-next-bottom");
            if (sections !== null) {{
                section = sections[sections.length-1];
                section.parentNode.appendChild(script);
            }}
        }}
        commentsRunWhenDOMLoaded(addGiscus);
        """
        )
        app.add_js_file(None, body=js, kind="giscuss")


def setup(app):
    app.add_config_value("comments_config", {}, "html")

    # Add our static path
    app.connect("builder-inited", shp_static_path)
    app.connect("config-inited", activate_comments)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
