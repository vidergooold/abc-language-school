<template>
  <section class="news-section">
    <h2 class="news-title">📣 Новости</h2>
    <div class="news-list">
      <article class="news-card" v-for="item in news" :key="item.id">
        <div class="news-card__header">
          <span class="news-card__date">{{ item.date }}</span>
          <span class="news-card__tag">{{ item.tag }}</span>
        </div>
        <h3 class="news-card__title">{{ item.title }}</h3>
        <div class="news-card__body" v-html="item.body"></div>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const news = ref([
  {
    id: 1,
    date: '03 апреля 2026',
    tag: 'Лагерь',
    title: '🏕 Лагерь-заезд выходного дня 03–05 апреля 2026',
    body: `
      <p>Приглашаем ребят с 1 по 6 класс в лагерь-заезд выходного дня!</p>
      <ul>
        <li>🔹 Выезд: 03.04.2026 в 10:00</li>
        <li>🔹 Возвращение: 05.04.2026 в 12:00</li>
        <li>🏘 Место: Детский оздоровительный лагерь <strong>ПИОНЕР</strong></li>
      </ul>
      <p><strong>В поездку входит:</strong></p>
      <ul>
        <li>✅ Транспорт в обе стороны 🚌</li>
        <li>✅ 5-разовое питание 🥘🍪</li>
        <li>✅ Программа на английском языке с играми и мастер-классами 🖼🪄</li>
        <li>✅ Денежная эстафета 💵🤸</li>
        <li>✅ Игры на свежем воздухе в эко-зоне 🌳🏡</li>
        <li>✅ Зажигательная дискотека 🪩🕺💃</li>
        <li>✅ Отрядные яркие выступления 👯🎷</li>
        <li>✅ Гадалка на предсказание будущего 🧿🔮📿</li>
        <li>✅ Тату-салон и стойка с аквагримом 🎨</li>
        <li>✅ Йога и медитации для достижения дзена 🔆🎎🪬</li>
      </ul>
      <p>👶 <strong>Возраст:</strong> с 1 по 6 класс</p>
    `,
  },
])
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
.news-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.news-card {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  border-left: 5px solid var(--brand-orange);
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  transition: box-shadow 0.2s, transform 0.2s;
}
.news-card:hover {
  box-shadow: 0 6px 20px rgba(255,107,45,0.15);
  transform: translateY(-2px);
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
</style>
