<template>
  <div class="org-section">
    <h2 class="section-title">Платные образовательные услуги</h2>

    <h3>О порядке оказания платных образовательных услуг</h3>

    <div class="services-list">
      <div class="service-item">
        <h4>Дошкольники (45 минут) (2025-2026 год)</h4>
        <div class="service-docs">
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образец договора</a>
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Прайс-лист</a>
          </p>
        </div>
      </div>

      <div class="service-item">
        <h4>FH1, AS1 (50 минут) (2025-2026 год)</h4>
        <div class="service-docs">
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образец договора</a>
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Прайс-лист</a>
          </p>
        </div>
      </div>

      <div class="service-item">
        <h4>AS2, AS3, AS4 (60 минут) (2025-2026 год)</h4>
        <div class="service-docs">
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образец договора</a>
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Прайс-лист</a>
          </p>
        </div>
      </div>

      <div class="service-item">
        <h4>GWA1+, GWA2 (75 минут) (2025-2026 год)</h4>
        <div class="service-docs">
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образец договора</a>
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Прайс-лист</a>
          </p>
        </div>
      </div>

      <div class="service-item">
        <h4>GWB1, GWB1+, GWB2, GWB2+, GWC1 (90 минут) (2025-2026 год)</h4>
        <div class="service-docs">
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образец договора</a>
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Прайс-лист</a>
          </p>
        </div>
      </div>

      <div class="service-item">
        <h4>Взрослые (2025-2026 год)</h4>
        <div class="service-docs">
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образец договора</a>
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Прайс-лист</a>
          </p>
        </div>
      </div>

      <div class="service-item">
        <h4>Мини-группа (2 человека) (45 минут) (2025-2026 год)</h4>
        <div class="service-docs">
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образец договора</a>
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Прайс-лист</a>
          </p>
        </div>
      </div>

      <div class="service-item">
        <h4>Индивидуальные занятия (45 мин) (2025-2026 год)</h4>
        <div class="service-docs">
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образец договора</a>
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Прайс-лист</a>
          </p>
        </div>
      </div>

      <div class="service-item">
        <h4>Китайский язык (45 мин) (2025-2026 год)</h4>
        <div class="service-docs">
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образец договора</a>
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Прайс-лист</a>
          </p>
        </div>
      </div>
    </div>

    <h3>Об установлении размера платы</h3>
    <p class="notice">
      Организация не взимает платы с родителей (законных представителей)
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

.services-list {
  margin-top: 20px;
}

.service-item {
  background: #ffe3cf;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 16px;
}

.service-item h4 {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 12px;
}

.service-docs {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.doc-link {
  margin-bottom: 0;
}

.doc-link a {
  color: var(--brand-orange);
  text-decoration: none;
}

.doc-link a:hover {
  text-decoration: underline;
}

.notice {
  background: #ffe3cf;
  padding: 16px;
  border-radius: 10px;
  border-left: 4px solid var(--brand-orange);
  font-weight: 600;
  margin-top: 16px;
}
</style>
