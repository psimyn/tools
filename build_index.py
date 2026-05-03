#!/usr/bin/env python3
"""Generate index.html from {name}.html + {name}.docs.md pairs in the repo root.

Convention (borrowed from simonw/tools):

    spirit-level.html       # the app itself
    spirit-level.docs.md    # markdown: first H1 is the title, rest is description

The generator walks the repo root, pairs each {name}.html with its
{name}.docs.md (if present), and writes a single index.html listing every app.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

import markdown  # type: ignore[import-not-found]

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "index.html"

# HTML files that are outputs or infrastructure, not apps.
EXCLUDE_HTML = {"index.html"}


@dataclass
class App:
    slug: str
    html_path: Path
    docs_path: Path | None
    title: str
    summary_html: str
    prompt: str | None


def _extract_title_from_html(path: Path) -> str:
    """Fallback: pull <title> out of an HTML file."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return path.stem
    m = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip() or path.stem
    return path.stem


def _parse_docs(path: Path) -> tuple[str | None, str, str | None]:
    """Return (title, summary_html, prompt) from a .docs.md file.

    - title: first H1 (`# ...`) if present, otherwise None
    - summary_html: rendered markdown of the lead paragraph(s) — everything
      between the H1 and the first H2. The deeper "Notes" / "Implementation"
      / "Caveats" sections are intentionally dropped so the index stays a
      list of one-paragraph descriptions.
    - prompt: the text of a blockquote immediately under a `## Prompt` heading,
      if present — used to show the original prompt prominently on the index.
    """
    src = path.read_text(encoding="utf-8", errors="replace")

    title: str | None = None
    lines = src.splitlines()
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        body = "\n".join(lines[1:]).lstrip("\n")
    else:
        body = src

    # Extract the first blockquote under a "## Prompt" section, if any.
    prompt: str | None = None
    m = re.search(
        r"(?mi)^##\s+Prompt\s*\n+((?:>\s?.*(?:\n|$))+)",
        body,
    )
    if m:
        block = m.group(1)
        prompt_lines = [re.sub(r"^>\s?", "", ln) for ln in block.splitlines()]
        prompt = "\n".join(prompt_lines).strip() or None

    # Lead = body up to (but not including) the first H2.
    lead = re.split(r"(?m)^##\s", body, maxsplit=1)[0].strip()
    summary_html = markdown.markdown(
        lead,
        extensions=["fenced_code", "tables"],
        output_format="html5",
    )
    return title, summary_html, prompt


def _slug_to_title(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").strip().title()


def discover_apps() -> list[App]:
    apps: list[App] = []
    for html_path in sorted(ROOT.glob("*.html")):
        if html_path.name in EXCLUDE_HTML:
            continue
        slug = html_path.stem
        docs_path = ROOT / f"{slug}.docs.md"
        if docs_path.exists():
            title, summary_html, prompt = _parse_docs(docs_path)
        else:
            title, summary_html, prompt = None, "", None
            docs_path = None
        if not title:
            title = _extract_title_from_html(html_path)
            if title == slug:
                title = _slug_to_title(slug)
        apps.append(
            App(
                slug=slug,
                html_path=html_path,
                docs_path=docs_path,
                title=title,
                summary_html=summary_html,
                prompt=prompt,
            )
        )
    return apps


PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Apps</title>
<style>
  :root {{
    --bg: #0f1115;
    --panel: #171a21;
    --ink: #e9edf5;
    --muted: #8993a7;
    --accent: #ffd84d;
    --line: rgba(255, 255, 255, 0.08);
  }}
  * {{ box-sizing: border-box; }}
  html, body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    line-height: 1.55;
  }}
  main {{ max-width: 760px; margin: 0 auto; padding: 48px 20px 80px; }}
  h1 {{
    font-size: 28px;
    margin: 0 0 6px;
    letter-spacing: -0.01em;
  }}
  header p {{ color: var(--muted); margin: 0 0 24px; }}
  .app {{
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 12px;
    margin: 8px 0;
  }}
  .app > summary {{
    list-style: none;
    cursor: pointer;
    padding: 12px 18px;
    display: flex;
    align-items: baseline;
    gap: 12px;
    -webkit-tap-highlight-color: transparent;
  }}
  .app > summary::-webkit-details-marker {{ display: none; }}
  .app > summary::before {{
    content: "";
    display: inline-block;
    width: 0;
    height: 0;
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
    border-left: 5px solid var(--muted);
    transition: transform 120ms ease;
    flex: 0 0 auto;
    transform: translateY(-1px);
  }}
  .app[open] > summary::before {{ transform: rotate(90deg) translateX(-1px); }}
  .app > summary .title {{
    color: var(--accent);
    text-decoration: none;
    font-size: 17px;
    font-weight: 600;
  }}
  .app > summary .title:hover {{ text-decoration: underline; }}
  .app > summary .slug {{
    color: var(--muted);
    font-size: 12px;
    font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    margin-left: auto;
  }}
  .app .body {{ padding: 0 18px 16px 36px; }}
  .app .summary {{ color: var(--ink); }}
  .app .summary p:first-child {{ margin-top: 0; }}
  .app .summary p:last-child {{ margin-bottom: 0; }}
  .app .prompt {{
    margin: 0 0 12px;
    padding: 10px 14px;
    border-left: 3px solid var(--accent);
    background: rgba(255, 216, 77, 0.06);
    color: var(--ink);
    font-style: italic;
    border-radius: 6px;
  }}
  .app .prompt::before {{
    content: "prompt";
    display: block;
    font-style: normal;
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
  }}
  code {{
    background: rgba(255, 255, 255, 0.06);
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 0.92em;
  }}
  pre {{
    background: #0b0d13;
    border: 1px solid var(--line);
    padding: 12px 14px;
    border-radius: 8px;
    overflow-x: auto;
  }}
  a {{ color: var(--accent); }}
  footer {{
    margin-top: 48px;
    color: var(--muted);
    font-size: 13px;
  }}
</style>
</head>
<body>
  <main>
    <header>
      <h1>Apps</h1>
      <p>A collection of small, single-file web apps, each built from a prompt.</p>
    </header>
    {cards}
    <footer>
      Source: <a href="https://github.com/psimyn/apps">psimyn/apps</a>
    </footer>
  </main>
</body>
</html>
"""

CARD_TEMPLATE = """    <details class="app">
      <summary>
        <a class="title" href="{href}">{title}</a>
        <span class="slug">{slug}.html</span>
      </summary>
      <div class="body">
        {prompt_block}
        <div class="summary">{summary}</div>
      </div>
    </details>"""


def render(apps: list[App]) -> str:
    if not apps:
        cards = '    <p class="app">No apps yet.</p>'
    else:
        cards = "\n".join(
            CARD_TEMPLATE.format(
                href=html.escape(app.slug),
                title=html.escape(app.title),
                slug=html.escape(app.slug),
                prompt_block=(
                    f'<blockquote class="prompt">{html.escape(app.prompt)}</blockquote>'
                    if app.prompt
                    else ""
                ),
                summary=app.summary_html or "",
            )
            for app in apps
        )
    return PAGE_TEMPLATE.format(cards=cards)


def main() -> None:
    apps = discover_apps()
    OUTPUT.write_text(render(apps), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(apps)} app(s).")


if __name__ == "__main__":
    main()
