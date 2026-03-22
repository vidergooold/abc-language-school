<template>
  <div class="org-section">
    <h2 class="section-title">Доступная среда</h2>

    <p class="notice">
      ЧУДО Лингвоцентр «Эй Би Си» обеспечивает условия доступности для лиц с ограниченными возможностями здоровья (ОВЗ) в соответствии с законодательством Российской Федерации.
    </p>

    <div class="info-block">
      <h3>Условия доступности здания</h3>
      <ul>
        <li>Вход в здание адаптирован для передвижения маломобильных групп.</li>
        <li>На входе имеется поручень для подъема колясок.</li>
        <li>Туалеты адаптированы для лиц с ОВЗ.</li>
        <li>При необходимости возможно сопровождение обучающегося помощником или сурдопереводчиком.</li>
      </ul>
    </div>

    <div class="info-block">
      <h3>Специальные условия обучения</h3>
      <ul>
        <li>Обучение лиц с ОВЗ осуществляется в индивидуальном формате с учётом особенностей состояния здоровья.</li>
        <li>Учебные материалы предоставляются в доступных форматах (печатный, аудиовизуальный).</li>
        <li>При необходимости обучение может проводиться в дистанционном формате.</li>
      </ul>
    </div>

    <div class="info-block">
      <h3>Контакты для обращения</h3>
      <p class="info-text">
        По вопросам обучения лиц с ОВЗ обращайтесь по телефону:
        <a href="tel:+73832091990">(383) 209-19-90</a>
        или на электронную почту:
        <a href="mailto:school.abc@mail.ru">school.abc@mail.ru</a>
      </p>
    </div>
  </div>
</template>

<style scoped>
.org-section {
  font-size: 17px;
  line-height: 1.6;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 20px;
}

.notice {
  background: #ffe3cf;
  padding: 16px;
  border-radius: 10px;
  border-left: 4px solid var(--brand-orange);
  font-weight: 600;
  margin-bottom: 24px;
}

.info-block {
  margin-bottom: 24px;
}

.info-block h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-orange);
  margin-bottom: 10px;
}

.info-block ul {
  padding-left: 20px;
}

.info-block ul li {
  margin-bottom: 6px;
}

.info-text a {
  color: var(--brand-orange);
  text-decoration: none;
}

.info-text a:hover {
  text-decoration: underline;
}
</style>
