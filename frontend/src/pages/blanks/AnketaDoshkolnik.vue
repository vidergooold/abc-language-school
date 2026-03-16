<template>
  <div class="anketa-page">
    <div class="anketa-toolbar no-print">
      <button @click="print">🖨 Распечатать / Сохранить PDF</button>
      <button @click="$router.back()">← Назад</button>
    </div>

    <div class="anketa" id="anketa">
      <div class="anketa__header">
        <div class="anketa__logo">ЧУДО Лингвоцентр «Эй Би Си»</div>
        <h1>АНКЕТА ДОШКОЛЬНИКА</h1>
        <p class="anketa__subtitle">Заполняется родителем (законным представителем)</p>
      </div>

      <table class="anketa__table">
        <tr><td class="label">ФИО ребёнка</td><td class="value"></td></tr>
        <tr><td class="label">Дата рождения</td><td class="value"></td></tr>
        <tr><td class="label">Детский сад / группа</td><td class="value"></td></tr>
        <tr><td class="label">Домашний адрес</td><td class="value"></td></tr>
        <tr><td class="label">ФИО родителя</td><td class="value"></td></tr>
        <tr><td class="label">Телефон родителя</td><td class="value"></td></tr>
        <tr><td class="label">Email родителя</td><td class="value"></td></tr>
        <tr><td class="label">Знает ли ребёнок английский</td><td class="value"></td></tr>
        <tr><td class="label">Откуда узнали о центре</td><td class="value"></td></tr>
        <tr><td class="label">Пожелания / примечания</td><td class="value tall"></td></tr>
      </table>

      <div class="anketa__consent">
        <p>Я, нижеподписавшийся, даю согласие на обработку персональных данных в соответствии с Федеральным законом № 152-ФЗ.</p>
        <div class="anketa__sign">
          <div class="sign-line"><span>Дата:</span><span class="line"></span></div>
          <div class="sign-line"><span>Подпись:</span><span class="line"></span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
function print() { window.print() }
</script>

<style scoped>
.anketa-page { max-width: 800px; margin: 0 auto; padding: 24px; }
.anketa-toolbar { display: flex; gap: 12px; margin-bottom: 24px; }
.anketa-toolbar button { padding: 9px 18px; border-radius: 10px; border: none; font-size: 14px; font-weight: 600; cursor: pointer; background: var(--brand-orange); color: #fff; }
.anketa-toolbar button:last-child { background: #eee; color: #333; }
.anketa { background: #fff; border: 1px solid #ddd; border-radius: 12px; padding: 40px; }
.anketa__header { text-align: center; margin-bottom: 28px; }
.anketa__logo { font-size: 13px; color: #888; margin-bottom: 4px; }
.anketa__header h1 { font-size: 22px; font-weight: 800; letter-spacing: 1px; margin-bottom: 4px; }
.anketa__subtitle { font-size: 13px; color: #888; }
.anketa__table { width: 100%; border-collapse: collapse; margin-bottom: 28px; }
.anketa__table td { padding: 10px 12px; border: 1px solid #ccc; font-size: 14px; }
.label { width: 220px; background: #f9f9f9; font-weight: 600; color: #333; white-space: nowrap; }
.value { min-height: 28px; }
.value.tall { height: 60px; }
.anketa__consent { font-size: 12px; color: #555; border-top: 1px solid #eee; padding-top: 16px; }
.anketa__sign { display: flex; gap: 40px; margin-top: 16px; }
.sign-line { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; }
.sign-line .line { flex: 1; border-bottom: 1px solid #333; min-width: 120px; height: 20px; }
@media print {
  .no-print { display: none !important; }
  .anketa { border: none; padding: 0; box-shadow: none; border-radius: 0; }
  .anketa-page { padding: 0; max-width: 100%; }
}
</style>
