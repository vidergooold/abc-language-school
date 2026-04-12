<template>
  <section class="news-section">
    <h2 class="news-title">📣 Новости</h2>

    <div v-if="loading" class="news-loading">Загрузка...</div>

    <div v-else-if="news.length === 0" class="news-empty">Новостей пока нет.</div>

    <template v-else>
      <div class="slider">
        <button class="slider__btn slider__btn--prev" @click="prev" aria-label="Назад">&#8592;</button>

        <transition name="slide" mode="out-in">
          <article class="news-card" :key="current">
            <div class="news-card__header">
              <span class="news-card__date">{{ news[current].date }}</span>
              <span class="news-card__tag">{{ news[current].tag }}</span>
            </div>
            <h3 class="news-card__title">{{ news[current].title }}</h3>
            <div class="news-card__body" v-html="news[current].body"></div>
          </article>
        </transition>

        <button class="slider__btn slider__btn--next" @click="next" aria-label="Вперёд">&#8594;</button>
      </div>

      <div class="slider__dots">
        <button
          v-for="(_, i) in news"
          :key="i"
          class="dot"
          :class="{ active: i === current }"
          @click="goTo(i)"
        />
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import http from '@/api/http'

const news = ref<any[]>([])
const loading = ref(true)
const current = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

async function loadNews() {
  try {
    const r = await http.get('/news')
    // API returns a paginated object { total, page, page_size, pages, items }
    news.value = r.data?.items ?? r.data ?? []
  } catch {
    news.value = []
  } finally {
    loading.value = false
  }
}

function next() {
  if (news.value.length === 0) return
  current.value = (current.value + 1) % news.value.length
  resetTimer()
}
function prev() {
  if (news.value.length === 0) return
  current.value = (current.value - 1 + news.value.length) % news.value.length
  resetTimer()
}
function goTo(i: number) {
  current.value = i
  resetTimer()
}
function startTimer() {
  if (news.value.length < 2) return
  timer = setInterval(() => {
    current.value = (current.value + 1) % news.value.length
  }, 5000)
}
function resetTimer() {
  if (timer) clearInterval(timer)
  startTimer()
}

onMounted(async () => {
  await loadNews()
  startTimer()
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.news-section {
  background: #fff7f0;
  border-radius: 20px;
  padding: 28px 24px;
}
.news-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 20px;
}
.news-loading,
.news-empty {
  font-size: 16px;
  color: #888;
  padding: 20px 0;
}
.slider {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}
.slider__btn {
  flex-shrink: 0;
  background: var(--brand-orange);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 20px;
  cursor: pointer;
  margin-top: 16px;
  transition: background 0.2s;
}
.slider__btn:hover {
  background: #e55a10;
}
.news-card {
  flex: 1;
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  border-left: 5px solid var(--brand-orange);
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  min-height: 120px;
}
.news-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.news-card__date {
  font-size: 13px;
  color: var(--text-secondary, #888);
}
.news-card__tag {
  font-size: 12px;
  font-weight: 700;
  background: var(--brand-orange);
  color: #fff;
  padding: 2px 10px;
  border-radius: 999px;
}
.news-card__title {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-purple);
  margin: 0 0 10px;
}
.news-card__body {
  font-size: 15px;
  color: #333;
  line-height: 1.6;
}
.news-card__body ul {
  padding-left: 18px;
  margin: 8px 0;
}
.news-card__body li {
  margin-bottom: 4px;
}
.slider__dots {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: #ddd;
  cursor: pointer;
  transition: background 0.2s;
  padding: 0;
}
.dot.active {
  background: var(--brand-orange);
}
.slide-enter-active,
.slide-leave-leave-active {
  transition: all 0.35s ease;
}
.slide-enter-from {
  opacity: 0;
  transform: translateX(40px);
}
.slide-leave-to {
  opacity: 0;
  transform: translateX(-40px);
}
</style>
