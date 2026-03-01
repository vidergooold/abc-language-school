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
      <p class="doc-link">
        📄
        <a href="#" target="_blank">
          Свидетельство о государственной регистрации права
        </a>
      </p>
    </div>

    <h3>О наличии оборудованных учебных кабинетов</h3>
    <div class="facility-card">
      <h4>ОБОРУДОВАННЫЕ УЧЕБНЫЕ КАБИНЕТЫ</h4>
      <p>
        <strong>Адрес:</strong> г.Новосибирск, ул. Бориса Богаткова, д. 208/2,
        офис 4 и 5
      </p>
      <p><strong>Общее количество:</strong> 4</p>
    </div>

    <div class="facility-card">
      <h4>ОБЪЕКТЫ ДЛЯ ПРОВЕДЕНИЯ ПРАКТИЧЕСКИХ ЗАНЯТИЙ</h4>
      <p>
        <strong>Адрес:</strong> г.Новосибирск, ул. Бориса Богаткова, д. 208/2,
        офис 4 и 5
      </p>
      <p><strong>Общее количество:</strong> 4</p>
    </div>

    <div class="classrooms-gallery">
      <div class="classroom-item">
        <div class="classroom-image">
          <img
            src="https://via.placeholder.com/400x300/ffe3cf/333?text=Кабинет+2"
            alt="Кабинет №2"
          />
        </div>
        <p class="classroom-caption">Кабинет №2</p>
      </div>

      <div class="classroom-item">
        <div class="classroom-image">
          <img
            src="https://via.placeholder.com/400x300/ffe3cf/333?text=Кабинет+3"
            alt="Кабинет №3"
          />
        </div>
        <p class="classroom-caption">Кабинет №3</p>
      </div>

      <div class="classroom-item">
        <div class="classroom-image">
          <img
            src="https://via.placeholder.com/400x300/ffe3cf/333?text=Кабинет+4"
            alt="Кабинет №4"
          />
        </div>
        <p class="classroom-caption">Кабинет №4</p>
      </div>

      <div class="classroom-item">
        <div class="classroom-image">
          <img
            src="https://via.placeholder.com/400x300/ffe3cf/333?text=Кабинет+5"
            alt="Кабинет №5"
          />
        </div>
        <p class="classroom-caption">Кабинет №5</p>
      </div>
    </div>

    <h3>О наличии оборудованных библиотек</h3>
    <div class="facility-card">
      <h4>ЧУДО Лингвоцентр "Эй Би Си"</h4>
      <p><strong>Адрес:</strong> г. Новосибирск, ул. Бориса Богаткова, д. 208/2</p>
      <p><strong>Количество мест:</strong> 5</p>
      <p>
        <strong>Приспособленность для инвалидов и лиц с ОВЗ:</strong> -
      </p>
    </div>

    <div class="library-image">
      <img
        src="https://via.placeholder.com/600x400/ffe3cf/333?text=Библиотека"
        alt="Библиотека"
      />
      <p class="image-caption">Библиотека</p>
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

.doc-link a {
  color: var(--brand-orange);
  text-decoration: none;
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

.library-image {
  margin-top: 24px;
  text-align: center;
}

.library-image img {
  max-width: 600px;
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.image-caption {
  margin-top: 12px;
  font-weight: 600;
  color: var(--brand-purple);
}
</style>
