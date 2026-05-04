<script setup lang="ts">
import { ref } from 'vue'
import { withBase } from 'vitepress'

const props = defineProps<{ src: string }>()
const comments = ref<Array<{ meta: string; body: string }> | null>(null)
const loading = ref(false)
const error = ref('')

async function loadComments() {
  if (comments.value || loading.value) return
  loading.value = true
  error.value = ''
  try {
    const response = await fetch(withBase(props.src))
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    comments.value = await response.json()
  } catch {
    error.value = '评论加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="comments-loader">
    <button type="button" class="comments-toggle" @click="loadComments">
      {{ comments ? '评论已展开' : loading ? '加载评论中...' : '展开评论' }}
    </button>
    <p v-if="error" class="comments-error">{{ error }}</p>
    <div v-if="comments" class="comments-list">
      <p v-if="comments.length === 0" class="comments-empty">无评论内容。</p>
      <article v-for="(comment, index) in comments" :key="index" class="comment-card">
        <div class="comment-meta">{{ comment.meta }}</div>
        <p v-if="comment.body">{{ comment.body }}</p>
      </article>
    </div>
  </section>
</template>
