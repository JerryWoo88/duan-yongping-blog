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
    outline: {
      level: [2, 2],
      label: '文章目录'
    },
    search: {
      provider: 'local',
      options: {
        translations: {
          button: {
            buttonText: '搜索文章',
            buttonAriaLabel: '搜索文章'
          },
          modal: {
            noResultsText: '没有找到结果',
            resetButtonTitle: '清除查询',
            footer: {
              selectText: '选择',
              navigateText: '切换',
              closeText: '关闭'
            }
          }
        }
      }
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com/JerryWoo88/duan-yongping-blog' }
    ],
    footer: {
      message: '内容整理自 PDF，仅供学习阅读。',
      copyright: '著作权归原作者所有'
    }
  }
})
