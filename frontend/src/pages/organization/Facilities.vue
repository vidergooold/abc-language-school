<template>
  <div class="org-section">
    <h2 class="section-title">
      Материально-техническое обеспечение и оснащенность образовательного
      процесса. Доступная среда
    </h2>

    <h3>О наличии зданий, строений, сооружений</h3>
    <div class="facility-card">
      <h4>Офис</h4>
      <p><strong>Адрес объекта:</strong> г. Новосибирск, ул.Бориса Богаткова 260/2</p>
      <p><strong>Назначение объекта:</strong> Нежилое</p>
      <p><strong>Площадь:</strong> 86.7 м²</p>
      <div class="doc-link">
        <a href="/docs/contract/reg.pdf" target="_blank">
          Свидетельство о государственной регистрации права
        </a>
      </div>
    </div>

    <h3>О наличии оборудованных учебных кабинетов</h3>
    <div class="facility-card">
      <h4>ОБОРУДОВАННЫЕ УЧЕБНЫЕ КАБИНЕТЫ</h4>
      <p>
        <strong>Адрес:</strong> г.Новосибирск, ул. Бориса Богаткова, д. 208/2,
        офис 4 и 5
      </p>
      <p><strong>Общее количество:</strong> 5</p>
    </div>

    <div class="facility-card">
      <h4>ОБЪЕКТЫ ДЛЯ ПРОВЕДЕНИЯ ПРАКТИЧЕСКИХ ЗАНЯТИЙ</h4>
      <p>
        <strong>Адрес:</strong> г.Новосибирск, ул. Бориса Богаткова, д. 208/2,
        офис 4 и 5
      </p>
      <p><strong>Общее количество:</strong> 5</p>
    </div>

    <div class="classrooms-gallery">
      <div class="classroom-item">
        <div class="classroom-image">
          <img src="/images/classrooms/room1.jpg" alt="Кабинет №1" loading="lazy" />
        </div>
        <p class="classroom-caption">Кабинет №1</p>
      </div>
      <div class="classroom-item">
        <div class="classroom-image">
          <img src="/images/classrooms/room2.jpg" alt="Кабинет №2" loading="lazy" />
        </div>
        <p class="classroom-caption">Кабинет №2</p>
      </div>
      <div class="classroom-item">
        <div class="classroom-image">
          <img src="/images/classrooms/room3.jpg" alt="Кабинет №3" loading="lazy" />
        </div>
        <p class="classroom-caption">Кабинет №3</p>
      </div>
      <div class="classroom-item">
        <div class="classroom-image">
          <img src="/images/classrooms/room4.jpg" alt="Кабинет №4" loading="lazy" />
        </div>
        <p class="classroom-caption">Кабинет №4</p>
      </div>
      <div class="classroom-item">
        <div class="classroom-image">
          <img src="/images/classrooms/room5.jpg" alt="Кабинет №5" loading="lazy" />
        </div>
        <p class="classroom-caption">Кабинет №5</p>
      </div>
    </div>

    <h3>О наличии объектов для проведения практических занятий</h3>
    <div class="facility-card">
      <h4>ПРАКТИЧЕСКИЕ ЗАНЯТИЯ</h4>
      <p>
        <strong>Адрес:</strong> г.Новосибирск, ул. Бориса Богаткова, д. 208/2,
        офис 4 и 5
      </p>
      <p><strong>Общее количество мест:</strong> 5</p>
    </div>

    <h3>Об условиях охраны здоровья</h3>
    <p>Помещения соответствуют санитарным и противопожарным нормам, требованиям охраны труда. Условия для доступности для инвалидов и лиц с ОВЗ: есть.</p>

    <h3>Дополнительные помещения</h3>
    <div class="classrooms-gallery">
      <div class="classroom-item">
        <div class="classroom-image">
          <img src="/images/classrooms/hall.jpg" alt="Холл" loading="lazy" />
        </div>
        <p class="classroom-caption">Холл</p>
      </div>
      <div class="classroom-item">
        <div class="classroom-image">
          <img src="/images/classrooms/wardrobe.jpg" alt="Гардероб" loading="lazy" />
        </div>
        <p class="classroom-caption">Гардероб</p>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>

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
h4 {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-orange);
  margin-bottom: 10px;
}
p {
  margin-bottom: 16px;
}
.facility-card {
  background: #ffe3cf;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 20px;
}
.doc-link {
  margin-top: 8px;
}
.doc-link a {
  color: var(--brand-orange);
  text-decoration: none;
  font-weight: 600;
}
.doc-link a:hover {
  text-decoration: underline;
}
.classrooms-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 24px 0;
}
.classroom-item {
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}
.classroom-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
}
.classroom-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.classroom-caption {
  padding: 12px;
  text-align: center;
  font-weight: 600;
  color: var(--brand-purple);
}
</style>
