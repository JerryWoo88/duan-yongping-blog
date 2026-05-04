import { defineConfig } from 'vitepress'
import { sidebar } from './sidebar'

export default defineConfig({
  title: '段永平博客文章合集',
  description: '段永平博客 2006-2018 文章合集，Markdown + VitePress 版本。',
  base: '/duan-yongping-blog/',
  lang: 'zh-CN',
  cleanUrls: true,
  lastUpdated: false,
  themeConfig: {
    logo: undefined,
    nav: [
      { text: '首页', link: '/' },
      { text: '目录', link: '/toc' }
    ],
    sidebar,
    outline: false,
    socialLinks: [
      { icon: 'github', link: 'https://github.com/JerryWoo88/duan-yongping-blog' }
    ],
    footer: {
      message: '内容整理自 PDF，仅供学习阅读。',
      copyright: '著作权归原作者所有'
    }
  }
})
