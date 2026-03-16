<template>
  <div class="org-section">
    <h2 class="section-title">Платные образовательные услуги</h2>

    <h3>О порядке оказания платных образовательных услуг</h3>

    <div class="docs-block">
      <a href="/docs/obrazets-dogovora.docx" download class="doc-card">
        <span class="doc-icon">📄</span>
        <span class="doc-name">Образец договора</span>
        <span class="doc-ext">.docx</span>
      </a>
      <a href="/docs/stoimost-obucheniia-2024-2025.docx" download class="doc-card">
        <span class="doc-icon">📄</span>
        <span class="doc-name">Прайс-лист 2024–2025</span>
        <span class="doc-ext">.docx</span>
      </a>
    </div>

    <div class="services-list">
      <div class="service-item">
        <h4>Дошкольники (45 минут) (2025-2026 год)</h4>
      </div>
      <div class="service-item">
        <h4>FH1, AS1 (50 минут) (2025-2026 год)</h4>
      </div>
      <div class="service-item">
        <h4>AS2, AS3, AS4 (60 минут) (2025-2026 год)</h4>
      </div>
      <div class="service-item">
        <h4>GWA1+, GWA2 (75 минут) (2025-2026 год)</h4>
      </div>
      <div class="service-item">
        <h4>GWB1, GWB1+, GWB2, GWB2+, GWC1 (90 минут) (2025-2026 год)</h4>
      </div>
      <div class="service-item">
        <h4>Взрослые (2025-2026 год)</h4>
      </div>
      <div class="service-item">
        <h4>Мини-группа (2 человека) (45 минут) (2025-2026 год)</h4>
      </div>
      <div class="service-item">
        <h4>Индивидуальные занятия (45 мин) (2025-2026 год)</h4>
      </div>
      <div class="service-item">
        <h4>Китайский язык (45 мин) (2025-2026 год)</h4>
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

.docs-block {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin: 20px 0;
}

.doc-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px 28px;
  background: #fff7f0;
  border: 2px solid #ffe3cf;
  border-radius: 14px;
  text-decoration: none;
  color: var(--brand-purple);
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
  min-width: 160px;
}

.doc-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  border-color: var(--brand-orange);
}

.doc-icon { font-size: 36px; }

.doc-name {
  font-size: 15px;
  font-weight: 600;
  text-align: center;
}

.doc-ext {
  font-size: 12px;
  color: #888;
}

.services-list {
  margin-top: 20px;
}

.service-item {
  background: #ffe3cf;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 12px;
}

.service-item h4 {
  font-size: 17px;
  font-weight: 700;
  color: var(--brand-purple);
  margin: 0;
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
