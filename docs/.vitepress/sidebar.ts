import type { DefaultTheme } from 'vitepress'

export const sidebar: DefaultTheme.Sidebar = [
  {
    text: '阅读',
    items: [
      { text: '全部目录', link: '/toc' },
      { text: '2006', link: '/years/2006' },
      { text: '2007', link: '/years/2007' },
      {
        text: '2010',
        link: '/years/2010',
        collapsed: false,
        items: [
          { text: '2010 Q1', link: '/years/2010-q1' },
          { text: '2010 Q2', link: '/years/2010-q2' },
          { text: '2010 Q3', link: '/years/2010-q3' },
          { text: '2010 Q4', link: '/years/2010-q4' },
        ]
      },
      { text: '2011', link: '/years/2011' },
      { text: '2012', link: '/years/2012' },
      { text: '2013', link: '/years/2013' },
      { text: '2014', link: '/years/2014' },
      { text: '2015', link: '/years/2015' },
      { text: '2016', link: '/years/2016' },
      { text: '2017', link: '/years/2017' },
      { text: '2018', link: '/years/2018' }
    ]
  }
]
