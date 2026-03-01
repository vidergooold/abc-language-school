<template>
  <div class="org-section">
    <h2 class="section-title">Образование</h2>

    <h3>Языки, на которых осуществляется образование</h3>
    <p>Английский; Русский;</p>

    <h3>Уровни образования</h3>
    <p>
      <strong>Дополнительное образование</strong> (подвиды дополнительного
      образования)<br />
      дополнительное образование детей и взрослых
    </p>

    <h3>Реализуемые образовательные программы</h3>

    <div class="programs-list">
      <details class="program-item">
        <summary class="program-title">
          Рабочая программа по английскому языку "Academy Stars 1"
        </summary>
        <div class="program-details">
          <p>
            <strong>Учебный предмет, курс, дисциплина (модуль):</strong><br />
            Не указаны
          </p>
          <p>
            <strong>Практика:</strong><br />
            Не указана
          </p>
          <p>
            <strong>Электронное обучение и дистанционные технологии:</strong
            ><br />
            Не используются
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образовательная программа</a>
          </p>
        </div>
      </details>

      <details class="program-item">
        <summary class="program-title">
          Рабочая программа по английскому языку "Academy Stars 2"
        </summary>
        <div class="program-details">
          <p>
            <strong>Учебный предмет, курс, дисциплина (модуль):</strong><br />
            Не указаны
          </p>
          <p>
            <strong>Практика:</strong><br />
            Не указана
          </p>
          <p>
            <strong>Электронное обучение и дистанционные технологии:</strong
            ><br />
            Не используются
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образовательная программа</a>
          </p>
        </div>
      </details>

      <details class="program-item">
        <summary class="program-title">
          Рабочая программа по английскому языку "Academy Stars 3"
        </summary>
        <div class="program-details">
          <p>
            <strong>Учебный предмет, курс, дисциплина (модуль):</strong><br />
            Не указаны
          </p>
          <p>
            <strong>Практика:</strong><br />
            Не указана
          </p>
          <p>
            <strong>Электронное обучение и дистанционные технологии:</strong
            ><br />
            Не используются
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образовательная программа</a>
          </p>
        </div>
      </details>

      <details class="program-item">
        <summary class="program-title">
          Рабочая программа по английскому языку "Gateway A1+"
        </summary>
        <div class="program-details">
          <p>
            <strong>Учебный предмет, курс, дисциплина (модуль):</strong><br />
            Не указаны
          </p>
          <p>
            <strong>Практика:</strong><br />
            Не указана
          </p>
          <p>
            <strong>Электронное обучение и дистанционные технологии:</strong
            ><br />
            Не используются
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образовательная программа</a>
          </p>
        </div>
      </details>

      <details class="program-item">
        <summary class="program-title">
          Рабочая программа по английскому языку "Gateway B1"
        </summary>
        <div class="program-details">
          <p>
            <strong>Учебный предмет, курс, дисциплина (модуль):</strong><br />
            Не указаны
          </p>
          <p>
            <strong>Практика:</strong><br />
            Не указана
          </p>
          <p>
            <strong>Электронное обучение и дистанционные технологии:</strong
            ><br />
            Не используются
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образовательная программа</a>
          </p>
        </div>
      </details>

      <details class="program-item">
        <summary class="program-title">
          Рабочая программа по английскому языку "FlyHigh 1"
        </summary>
        <div class="program-details">
          <p>
            <strong>Учебный предмет, курс, дисциплина (модуль):</strong><br />
            Не указаны
          </p>
          <p>
            <strong>Практика:</strong><br />
            Не указана
          </p>
          <p>
            <strong>Электронное обучение и дистанционные технологии:</strong
            ><br />
            Не используются
          </p>
          <p class="doc-link">
            📄 <a href="#" target="_blank">Образовательная программа</a>
          </p>
        </div>
      </details>
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
  margin-top: 24px;
  margin-bottom: 12px;
}

p {
  margin-bottom: 16px;
}

.programs-list {
  margin-top: 20px;
}

.program-item {
  background: #ffe3cf;
  padding: 16px;
  border-radius: 10px;
  margin-bottom: 12px;
}

.program-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--brand-purple);
  cursor: pointer;
  list-style: none;
  display: flex;
  align-items: center;
}

.program-title::-webkit-details-marker {
  display: none;
}

.program-title::before {
  content: '▶';
  margin-right: 10px;
  transition: transform 0.2s;
  color: var(--brand-orange);
}

details[open] .program-title::before {
  transform: rotate(90deg);
}

.program-details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 2px solid var(--brand-orange);
  font-size: 15px;
}

.program-details p {
  margin-bottom: 12px;
}

.doc-link a {
  color: var(--brand-orange);
  text-decoration: none;
}

.doc-link a:hover {
  text-decoration: underline;
}
</style>
