from __future__ import annotations

import json
import re
import shutil
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "articles.json"
DOCS = ROOT / "docs"
YEARS = DOCS / "years"
SIDEBAR = DOCS / ".vitepress" / "sidebar.ts"
TOC = DOCS / "toc.md"


def md_escape(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\u2028", "\n").strip()


def slug_for(article: dict) -> str:
    return f"article-{article['number']:03d}"


def split_paragraphs(text: str) -> list[str]:
    text = md_escape(text)
    if not text:
        return []
    parts = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if len(parts) == 1:
        parts = [part.strip() for part in text.splitlines() if part.strip()]
    return parts


def comment_blocks(text: str) -> list[list[str]]:
    lines = [line.strip() for line in md_escape(text).splitlines() if line.strip()]
    if not lines:
        return []

    blocks: list[list[str]] = []
    current: list[str] = []
    marker = re.compile(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}")
    for line in lines:
        if marker.search(line) and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return blocks


def render_article(article: dict) -> str:
    lines = [
        f"## 第 {article['number']} 篇 {md_escape(article['title'])} {{#{slug_for(article)}}}",
        "",
        f'<div class="article-meta">{article["date"]}</div>',
        "",
        f'<a class="source-link" href="{article["url"]}" target="_blank" rel="noreferrer">原博客链接</a>',
        "",
    ]

    for paragraph in split_paragraphs(article.get("body", "")):
        lines.extend([paragraph, ""])

    lines.extend(["### 文章评论", ""])
    blocks = comment_blocks(article.get("comments", ""))
    if not blocks:
        lines.extend(["> 无评论内容。", ""])
    else:
        for block in blocks:
            lines.append(f"> **{block[0]}**")
            for line in block[1:]:
                lines.append(f"> {line}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_year(year: str, articles: list[dict]) -> str:
    lines = [
        "---",
        f"title: {year}",
        "---",
        "",
        f"# {year} 年文章合集",
        "",
        f"{year} 年共整理 {len(articles)} 篇博客文章。正文按发布时间排列，右侧文章目录可快速跳转到具体篇目。",
        "",
    ]
    for article in articles:
        lines.append(render_article(article))
    return "\n".join(lines).rstrip() + "\n"


def render_toc(grouped: dict[str, list[dict]]) -> str:
    lines = [
        "# 全部目录",
        "",
        "目录由生成脚本根据结构化文章数据自动维护；文章正文按年份拆分在左侧导航中。",
        "",
    ]
    for year in sorted(grouped):
        lines.extend([f"## {year}", ""])
        for article in grouped[year]:
            lines.append(
                f"- [{article['number']:03d}. {article['date'][:10]} {md_escape(article['title'])}]"
                f"(/years/{year}#{slug_for(article)})"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_sidebar(years: list[str]) -> str:
    items = "\n".join(f"      {{ text: '{year}', link: '/years/{year}' }}," for year in years).rstrip(",")
    return f"""import type {{ DefaultTheme }} from 'vitepress'

export const sidebar: DefaultTheme.Sidebar = [
  {{
    text: '阅读',
    items: [
      {{ text: '全部目录', link: '/toc' }},
{items}
    ]
  }}
]
"""


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source data: {SOURCE}")

    articles = json.loads(SOURCE.read_text(encoding="utf-8"))
    grouped: dict[str, list[dict]] = defaultdict(list)
    for article in articles:
        grouped[article["date"][:4]].append(article)

    if YEARS.exists():
        shutil.rmtree(YEARS)
    YEARS.mkdir(parents=True)

    for year, year_articles in sorted(grouped.items()):
        (YEARS / f"{year}.md").write_text(render_year(year, year_articles), encoding="utf-8")

    TOC.write_text(render_toc(grouped), encoding="utf-8")
    SIDEBAR.write_text(render_sidebar(sorted(grouped)), encoding="utf-8")
    print(f"Generated {len(articles)} articles across {len(grouped)} year pages.")


if __name__ == "__main__":
    main()
