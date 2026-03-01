<template>
  <div class="org-section">
    <h2 class="section-title">Руководство</h2>

    <h3>О руководителе образовательной организации</h3>
    <div class="director-info">
      <p class="director-name">Андрюнина Марина Викторовна</p>
      <p><strong>Должность:</strong> Директор</p>
      <p>
        <strong>Тел.:</strong>
        <a href="tel:+73832091990">(383) 209-19-90</a>
      </p>
      <p>
        <strong>E-Mail:</strong>
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

h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
}

.director-info {
  background: #ffe3cf;
  padding: 20px;
  border-radius: 12px;
  max-width: 500px;
}

.director-name {
  font-size: 20px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 12px;
}

.director-info p {
  margin-bottom: 8px;
}

.director-info a {
  color: var(--brand-orange);
  text-decoration: none;
}

.director-info a:hover {
  text-decoration: underline;
}
</style>
