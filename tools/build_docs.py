# -*- coding: UTF-8 -*-
"""Generate HTML documentation from Markdown for NVDA add-on."""

import html
import re
from pathlib import Path

def md_to_html(md_text: str, title: str, lang: str = "id") -> str:
    lines = md_text.splitlines()
    html_lines = [
        "<!DOCTYPE html>",
        f'<html lang="{lang}">',
        "<head>",
        '  <meta charset="UTF-8">',
        f"  <title>{html.escape(title)}</title>",
        "  <style>",
        "    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 20px auto; padding: 0 15px; color: #1a1a1a; }",
        "    h1, h2, h3 { color: #0d47a1; margin-top: 1.2em; }",
        "    code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; }",
        "    pre { background: #f0f0f0; padding: 10px; border-radius: 5px; overflow-x: auto; }",
        "    ul, ol { padding-left: 25px; }",
        "    li { margin-bottom: 6px; }",
        "  </style>",
        "</head>",
        "<body>",
    ]
    in_ul = False
    in_ol = False
    in_p = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_ul:
                html_lines.append("</ul>")
                in_ul = False
            if in_ol:
                html_lines.append("</ol>")
                in_ol = False
            if in_p:
                html_lines.append("</p>")
                in_p = False
            continue

        if stripped.startswith("### "):
            if in_ul: html_lines.append("</ul>"); in_ul = False
            if in_ol: html_lines.append("</ol>"); in_ol = False
            if in_p: html_lines.append("</p>"); in_p = False
            html_lines.append(f"<h3>{html.escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            if in_ul: html_lines.append("</ul>"); in_ul = False
            if in_ol: html_lines.append("</ol>"); in_ol = False
            if in_p: html_lines.append("</p>"); in_p = False
            html_lines.append(f"<h2>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            if in_ul: html_lines.append("</ul>"); in_ul = False
            if in_ol: html_lines.append("</ol>"); in_ol = False
            if in_p: html_lines.append("</p>"); in_p = False
            html_lines.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            if in_p: html_lines.append("</p>"); in_p = False
            if in_ol: html_lines.append("</ol>"); in_ol = False
            if not in_ul:
                html_lines.append("<ul>")
                in_ul = True
            content = html.escape(stripped[2:])
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            html_lines.append(f"  <li>{content}</li>")
        elif re.match(r"^\d+\.\s", stripped):
            if in_p: html_lines.append("</p>"); in_p = False
            if in_ul: html_lines.append("</ul>"); in_ul = False
            if not in_ol:
                html_lines.append("<ol>")
                in_ol = True
            raw = re.sub(r"^\d+\.\s+", "", stripped)
            content = html.escape(raw)
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            html_lines.append(f"  <li>{content}</li>")
        else:
            if in_ul: html_lines.append("</ul>"); in_ul = False
            if in_ol: html_lines.append("</ol>"); in_ol = False
            content = html.escape(stripped)
            content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
            if not in_p:
                html_lines.append(f"<p>{content}")
                in_p = True
            else:
                html_lines.append(f"<br>{content}")

    if in_ul: html_lines.append("</ul>")
    if in_ol: html_lines.append("</ol>")
    if in_p: html_lines.append("</p>")
    html_lines.extend(["</body>", "</html>"])
    return "\n".join(html_lines)


def main():
    root = Path(__file__).resolve().parent.parent
    configs = [
        ("id", "Emoji ID - Dokumentasi Add-on", "id"),
        ("en", "Emoji ID - Add-on Documentation", "en"),
    ]
    for folder, title, lang in configs:
        src = root / "addon" / "doc" / folder / "readme.md"
        dst = root / "addon" / "doc" / folder / "readme.html"
        if src.exists():
            html_content = md_to_html(src.read_text(encoding="utf-8"), title, lang)
            dst.write_text(html_content, encoding="utf-8")
            print(f"Generated {dst}")

if __name__ == "__main__":
    main()
