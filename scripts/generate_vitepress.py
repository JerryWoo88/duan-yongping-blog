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
POSTS = DOCS / "posts"
PUBLIC = DOCS / "public"
COMMENTS = PUBLIC / "comments"
SIDEBAR = DOCS / ".vitepress" / "sidebar.ts"
TOC = DOCS / "toc.md"


def md_escape(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\u2028", "\n").strip()


def slug_for(article: dict) -> str:
    return f"article-{article['number']:03d}"


def post_link(article: dict) -> str:
    return f"/posts/{slug_for(article)}"


def split_paragraphs(text: str) -> list[str]:
    text = md_escape(text)
    if not text:
        return []
    parts = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    if len(parts) == 1:
        parts = [part.strip() for part in text.splitlines() if part.strip()]
    return parts


def summary(article: dict, limit: int = 120) -> str:
    body = re.sub(r"\s+", " ", md_escape(article.get("body", ""))).strip()
    if not body:
        return "暂无摘要。"
    return body[:limit].rstrip() + ("..." if len(body) > limit else "")


def comment_blocks(text: str) -> list[dict[str, str]]:
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

    return [{"meta": block[0], "body": "\n".join(block[1:]).strip()} for block in blocks]


def quarter_for(article: dict) -> int:
    month = int(article["date"][5:7])
    return ((month - 1) // 3) + 1


def render_post(article: dict) -> str:
    slug = slug_for(article)
    lines = [
        "---",
        f"title: {json.dumps(article['title'], ensure_ascii=False)}",
        "---",
        "",
        f"# {md_escape(article['title'])}",
        "",
        f'<div class="article-meta">第 {article["number"]} 篇 · {article["date"]}</div>',
        "",
        f'<a class="source-link" href="{article["url"]}" target="_blank" rel="noreferrer">原博客链接</a>',
        "",
    ]
    for paragraph in split_paragraphs(article.get("body", "")):
        lines.extend([paragraph, ""])

    lines.extend(
        [
            f'<CommentsLoader src="/comments/{slug}.json" />',
            "",
            '<div class="post-nav"><a href="/toc">返回全部目录</a></div>',
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def article_card(article: dict) -> str:
    return "\n".join(
        [
            f'<article class="post-card" id="{slug_for(article)}">',
            f'  <div class="post-card-meta">第 {article["number"]} 篇 · {article["date"][:10]}</div>',
            f'  <h2><a href="{post_link(article)}">{md_escape(article["title"])}</a></h2>',
            f'  <p>{summary(article)}</p>',
            f'  <a class="read-more" href="{post_link(article)}">阅读全文</a>',
            "</article>",
            "",
        ]
    )


def render_listing(title: str, intro: str, articles: list[dict]) -> str:
    lines = ["---", f"title: {title}", "outline: false", "---", "", f"# {title}", "", intro, ""]
    for article in articles:
        lines.append(article_card(article))
    return "\n".join(lines).rstrip() + "\n"


def render_2010_index(quarters: dict[int, list[dict]]) -> str:
    lines = [
        "---",
        "title: 2010 年文章合集",
        "outline: false",
        "---",
        "",
        "# 2010 年文章合集",
        "",
        "2010 年文章较多，已按季度拆分，减少手机端单页体积和滚动压力。",
        "",
    ]
    for quarter in range(1, 5):
        articles = quarters.get(quarter, [])
        lines.extend(
            [
                f"## Q{quarter}",
                "",
                f"{len(articles)} 篇文章",
                "",
                f"[阅读 2010 Q{quarter}](/years/2010-q{quarter})",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_toc(grouped: dict[str, list[dict]]) -> str:
    lines = [
        "---",
        "title: 全部目录",
        "outline: false",
        "---",
        "",
        "# 全部目录",
        "",
        "按年份汇总所有文章，点击标题进入单篇正文。评论默认折叠，进入文章页后可按需加载。",
        "",
    ]
    for year in sorted(grouped):
        lines.extend([f"## {year}", ""])
        for article in grouped[year]:
            lines.append(f"- [{article['number']:03d}. {article['date'][:10]} {md_escape(article['title'])}]({post_link(article)})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_sidebar(years: list[str]) -> str:
    items: list[str] = ["      { text: '全部目录', link: '/toc' },"]
    for year in years:
        if year == "2010":
            items.append("      {")
            items.append("        text: '2010',")
            items.append("        link: '/years/2010',")
            items.append("        collapsed: false,")
            items.append("        items: [")
            for quarter in range(1, 5):
                items.append(f"          {{ text: '2010 Q{quarter}', link: '/years/2010-q{quarter}' }},")
            items.append("        ]")
            items.append("      },")
        else:
            items.append(f"      {{ text: '{year}', link: '/years/{year}' }},")
    return f"""import type {{ DefaultTheme }} from 'vitepress'

export const sidebar: DefaultTheme.Sidebar = [
  {{
    text: '阅读',
    items: [
{chr(10).join(items).rstrip(',')}
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

    for path in (YEARS, POSTS, COMMENTS):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)

    for article in articles:
        slug = slug_for(article)
        (POSTS / f"{slug}.md").write_text(render_post(article), encoding="utf-8")
        (COMMENTS / f"{slug}.json").write_text(
            json.dumps(comment_blocks(article.get("comments", "")), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    for year, year_articles in sorted(grouped.items()):
        if year == "2010":
            quarters: dict[int, list[dict]] = defaultdict(list)
            for article in year_articles:
                quarters[quarter_for(article)].append(article)
            (YEARS / "2010.md").write_text(render_2010_index(quarters), encoding="utf-8")
            for quarter in range(1, 5):
                q_articles = quarters.get(quarter, [])
                (YEARS / f"2010-q{quarter}.md").write_text(
                    render_listing(
                        f"2010 年 Q{quarter} 文章合集",
                        f"2010 年第 {quarter} 季度共整理 {len(q_articles)} 篇文章。列表页只保留标题、摘要和阅读链接，正文进入单篇页面。",
                        q_articles,
                    ),
                    encoding="utf-8",
                )
        else:
            (YEARS / f"{year}.md").write_text(
                render_listing(
                    f"{year} 年文章合集",
                    f"{year} 年共整理 {len(year_articles)} 篇博客文章。列表页只保留标题、摘要和阅读链接，方便手机端快速浏览。",
                    year_articles,
                ),
                encoding="utf-8",
            )

    TOC.write_text(render_toc(grouped), encoding="utf-8")
    SIDEBAR.write_text(render_sidebar(sorted(grouped)), encoding="utf-8")
    print(f"Generated {len(articles)} posts, {len(grouped)} year indexes, and lazy comment JSON.")


if __name__ == "__main__":
    main()
