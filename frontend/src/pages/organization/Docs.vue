<template>
  <div class="org-section">
    <h2 class="section-title">Документы</h2>

    <h3>Иные документы</h3>
    <p class="doc-link">
      📄
      <a href="/docs/contract/reg.pdf" target="_blank">
        Свидетельство о государственной регистрации некоммерческой организации
      </a>
    </p>
    <p class="doc-info">
      Выдан: Инспекция ФНС по Октябрьскому району, г.Новосибирска, 17.06.2021.
    </p>
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
  margin-top: 24px;
  margin-bottom: 12px;
}

p {
  margin-bottom: 16px;
}

.doc-link a {
  color: var(--brand-orange);
  text-decoration: none;
}

.doc-link a:hover {
  text-decoration: underline;
}

.doc-info {
  font-size: 15px;
  color: var(--text-secondary);
  margin-top: 8px;
}
</style>
