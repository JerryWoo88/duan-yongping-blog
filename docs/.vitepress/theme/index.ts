import DefaultTheme from 'vitepress/theme'
import CommentsLoader from './CommentsLoader.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('CommentsLoader', CommentsLoader)
  }
}
