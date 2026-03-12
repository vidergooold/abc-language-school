<template>
  <div class="docs-page">
    <h1>📂 Документы</h1>
    <p class="subtitle">Здесь хранятся документы школы, политики и заполненные анкеты в .доцх-формате.</p>

    <div class="doc-sections">
      <div class="doc-section" v-for="sec in sections" :key="sec.title">
        <h2>{{ sec.icon }} {{ sec.title }}</h2>
        <div class="doc-list">
          <a
            v-for="doc in sec.docs"
            :key="doc.name"
            :href="doc.url"
            target="_blank"
            class="doc-item"
          >
            <span class="doc-icon">📄</span>
            <span class="doc-name">{{ doc.name }}</span>
            <span class="doc-arrow">↓</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const sections = [
  {
    icon: '🔐',
    title: 'Политики и согласия',
    docs: [
      { name: 'Политика обработки персональных данных', url: '/docs/Politika_obrabotki_personalnykh_dannykh.docx' },
      { name: 'Согласие пользователя на обработку перс. данных', url: '/docs/Soglasie_polzovatelia_saita_na_obrabotku_personalnykh_dannykh.docx' },
    ],
  },
  {
    icon: '📅',
    title: 'Расписание',
    docs: [
      { name: 'Расписание занятий по школам', url: '/docs/raspisanie-dlia-saita.docx' },
    ],
  },
  {
    icon: '📝',
    title: 'Бланки анкет',
    docs: [
      { name: 'Анкета школьника (бланк)', url: '/docs/anketa-shkolnik.docx' },
      { name: 'Анкета взрослого (бланк)', url: '/docs/anketa-vzrosly.docx' },
      { name: 'Анкета дошкольника (бланк)', url: '/docs/anketa-doshkolnik.docx' },
    ],
  },
]
</script>

<style scoped>
.docs-page h1 { font-size: 28px; font-weight: 700; color: var(--brand-purple); margin-bottom: 6px; }
.subtitle { font-size: 15px; color: #888; margin-bottom: 28px; }
.doc-sections { display: flex; flex-direction: column; gap: 28px; }
.doc-section h2 { font-size: 19px; font-weight: 700; color: var(--brand-purple); margin-bottom: 12px; }
.doc-list { display: flex; flex-direction: column; gap: 10px; }
.doc-item { display: flex; align-items: center; gap: 12px; background: #fff7f0; border-radius: 12px; padding: 14px 18px; text-decoration: none; color: #333; border: 1.5px solid #ffe3cf; transition: box-shadow 0.2s, border-color 0.2s; }
.doc-item:hover { box-shadow: 0 4px 14px rgba(255,107,45,0.15); border-color: var(--brand-orange); }
.doc-icon { font-size: 20px; }
.doc-name { flex: 1; font-size: 15px; font-weight: 500; }
.doc-arrow { font-size: 18px; color: var(--brand-orange); }
</style>
