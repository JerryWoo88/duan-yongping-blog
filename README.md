# 段永平博客文章合集 2006-2018

这个仓库把 PDF 内容整理为可维护的 Markdown + VitePress 静态网站。

## 结构

- `docs/`: VitePress 文档源文件
- `docs/years/YYYY/MM.md`: 按年、月拆分的文章正文页
- `docs/toc.md`: 自动生成的全量目录
- `docs/.vitepress/`: VitePress 配置、侧边栏和主题样式
- `scripts/generate_vitepress.py`: 从结构化文章数据生成 Markdown
- `scripts/build_site.py`: 从原始 PDF 抽取结构化文章数据
- `data/articles.json`: 结构化文章数据源

## 本地开发

```bash
npm install
npm run generate
npm run docs:dev
```

## 构建

```bash
npm run docs:build
```

部署到 GitHub Pages 时，GitHub Actions 会从 Markdown 源码构建站点。
