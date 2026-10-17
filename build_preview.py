#!/usr/bin/env python3
"""Render README.md as a GitHub-profile-like page for previewing in the chat.

Usage: python3 build_preview.py            # writes preview.html from README.md
Supports the markdown subset the profile README actually uses: headings,
paragraphs, bullets, ordered items, bold, inline code, links, images, rules.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "preview.html"


def inline(text: str) -> str:
    """Escape, then apply the inline markdown this README uses."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    # images before links, and neither inside the other's match
    text = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        r'<img src="\2" alt="\1">',
        text,
    )
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    return text


def render(md: str) -> str:
    out: list[str] = []
    para: list[str] = []
    items: list[str] = []
    ordered = False

    def flush_para() -> None:
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
            para.clear()

    def flush_list() -> None:
        nonlocal ordered
        if items:
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{i}</li>" for i in items) + f"</{tag}>")
            items.clear()
            ordered = False

    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush_para()
            flush_list()
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_para()
            flush_list()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            continue
        if re.match(r"^---+$", line.strip()):
            flush_para()
            flush_list()
            out.append("<hr>")
            continue
        m = re.match(r"^\s*[-*]\s+(.*)$", line)
        if m:
            flush_para()
            if ordered:
                flush_list()
            items.append(inline(m.group(1)))
            continue
        m = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if m:
            flush_para()
            if items and not ordered:
                flush_list()
            ordered = True
            items.append(inline(m.group(1)))
            continue
        para.append(line.strip())
    flush_para()
    flush_list()
    return "\n".join(out)


PAGE = """<!doctype html>
<meta charset="utf-8">
<style>
  :root {{
    --bg: #0d1117; --panel: #161b22; --border: #30363d;
    --fg: #e6edf3; --muted: #8b949e; --link: #58a6ff; --chip: #21262d;
  }}
  body {{
    margin: 0; background: var(--bg); color: var(--fg);
    font: 14px/1.6 -apple-system, "SF Pro Text", "Segoe UI", sans-serif;
    width: 880px;
  }}
  .wrap {{ width: 880px; padding: 0 0 8px; }}
  .top {{ display: flex; align-items: center; gap: 18px; padding: 6px 0 16px;
          border-bottom: 1px solid var(--border); }}
  .avatar {{ width: 108px; height: 108px; border-radius: 50%; flex: 0 0 108px;
             border: 1px solid var(--border); background: var(--chip); object-fit: cover; }}
  h1.name {{ font-size: 26px; font-weight: 600; margin: 0 0 2px; }}
  .login {{ color: var(--muted); font-size: 20px; font-weight: 300; }}
  .bio {{ margin: 6px 0 0; color: var(--fg); }}
  .meta {{ margin-top: 8px; color: var(--muted); font-size: 13px; display: flex; gap: 14px; flex-wrap: wrap; }}
  .body {{ padding: 18px 0 0; }}
  .body h1 {{ font-size: 22px; font-weight: 600; margin: 18px 0 10px; padding-bottom: 6px;
              border-bottom: 1px solid var(--border); }}
  .body h2 {{ font-size: 18px; font-weight: 600; margin: 20px 0 10px; padding-bottom: 6px;
              border-bottom: 1px solid var(--border); }}
  .body h3 {{ font-size: 15px; font-weight: 600; margin: 16px 0 8px; }}
  .body p {{ margin: 10px 0; }}
  .body ul, .body ol {{ margin: 8px 0; padding-left: 22px; }}
  .body li {{ margin: 5px 0; }}
  .body a {{ color: var(--link); text-decoration: none; }}
  .body a:hover {{ text-decoration: underline; }}
  .body code {{ background: rgba(110,118,129,0.25); padding: 1px 5px; border-radius: 6px;
                font: 12px ui-monospace, SFMono-Regular, monospace; }}
  .body img {{ vertical-align: middle; margin: 2px 2px 2px 0; }}
  .body hr {{ border: 0; border-top: 1px solid var(--border); margin: 18px 0; }}
  strong {{ font-weight: 600; }}
</style>
<div class="wrap">
  <div class="top">
    <img class="avatar" src="https://github.com/{login}.png?size=220" alt="avatar">
    <div>
      <h1 class="name">{name} <span class="login">{login}</span></h1>
      <p class="bio">{bio}</p>
      <div class="meta">
        <span>&#9906; {location}</span>
        <span>&#9634; {repos} public repositories</span>
        <span>&#9993; {email}</span>
      </div>
    </div>
  </div>
  <div class="body">{content}</div>
</div>
"""

FIELDS = {
    "login": "GOPNIK64",
    "name": "Ivan Naumann Thostrup",
    "bio": "Full-stack developer &middot; TypeScript, Node, MongoDB, Angular",
    "location": "C&oacute;rdoba, Argentina",
    "repos": "2",
    "email": "naumannthostrupivan@gmail.com",
}


def main() -> None:
    md = (HERE / "README.md").read_text(encoding="utf-8")
    OUT.write_text(PAGE.format(content=render(md), **FIELDS), encoding="utf-8")
    print(f"  wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
