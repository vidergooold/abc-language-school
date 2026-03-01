<template>
  <div>
    <h2 class="org-page-title">Основные сведения</h2>
    <div class="card org-card">
      <table class="org-table">
        <tbody>
          <tr v-for="row in info" :key="row.label">
            <td class="org-table-label">{{ row.label }}</td>
            <td class="org-table-value">{{ row.value }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
const info = [
  { label: 'Полное наименование', value: 'Частное образовательное учреждение дополнительного образования «ABC Language School»' },
  { label: 'Сокращённое наименование', value: 'ЧОУ ДО «ABC Language School»' },
  { label: 'Дата создания', value: '15 января 2010 года' },
  { label: 'Учредитель', value: 'Иванов Иван Иванович' },
  { label: 'Место нахождения', value: '630099, г. Новосибирск, ул. Ленина, д. 1, офис 101' },
  { label: 'Телефон', value: '+7 (383) 200-00-00' },
  { label: 'Адрес электронной почты', value: 'info@abc-school.ru' },
  { label: 'Официальный сайт', value: 'https://abc-school.ru' },
  { label: 'ИНН', value: '5400000000' },
  { label: 'ОГРН', value: '1000000000000' },
  { label: 'КПП', value: '540001001' },
  { label: 'Лицензия на образовательную деятельность', value: 'Серия 54Л01 № 0001234, выдана 10.03.2010, бессрочно' },
  { label: 'Форма обучения', value: 'Очная, очно-заочная, заочная (дистанционная)' },
  { label: 'Язык обучения', value: 'Русский, английский' },
  { label: 'Филиалы', value: 'Академгородок: пр. Академика Лаврентьева, д. 6' },
]
</script>

<style scoped>
.org-page-title { font-size: var(--font-size-2xl); font-weight: 800; color: var(--text-main); margin-bottom: var(--spacing-xl); }
.org-card { padding: 0; overflow: hidden; }
.org-table { width: 100%; border-collapse: collapse; }
.org-table tr { border-bottom: 1px solid var(--border-color); transition: background 0.2s; }
.org-table tr:last-child { border-bottom: none; }
.org-table tr:hover td { background: var(--brand-orange-light); cursor: default; }
.org-table-label { padding: 14px 16px; font-size: var(--font-size-sm); font-weight: 600; color: var(--text-main); width: 40%; vertical-align: top; background: var(--bg-main); }
.org-table-value { padding: 14px 16px; font-size: var(--font-size-sm); color: var(--text-secondary); line-height: 1.6; }
@media (max-width: 767px) {
  .org-table, .org-table tbody, .org-table tr, .org-table td { display: block; width: 100%; }
  .org-table-label { background: var(--brand-orange-light); color: var(--brand-orange-hover); font-size: var(--font-size-xs); text-transform: uppercase; letter-spacing: 0.05em; padding: 10px 16px 4px; }
  .org-table-value { padding: 4px 16px 14px; }
}
</style>
