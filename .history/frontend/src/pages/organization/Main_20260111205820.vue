<template>
  <div class="org-section">
    <h2 class="section-title">Основные сведения</h2>

    <h3>Об образовательной организации</h3>
    <p>
      <strong>Полное и сокращенное наименование:</strong><br />
      Частное учреждение дополнительного образования Лингвоцентр "Эй Би Си"
      (ЧУДО Лингвоцентр "Эй Би Си")
    </p>
    <p>
      <strong>Дата создания:</strong><br />
      08.06.2005
    </p>

    <h3>Учредители образовательной организации</h3>
    <p><strong>Министерство образования Новосибирской области</strong></p>
    <p>
      <strong>Адрес:</strong> 630007, Новосибирская область, город Новосибирск,
      Красный пр-кт, д. 18<br />
      <strong>Телефон:</strong>
      <a href="tel:+73832387320">(383) 238-73-20</a> (приемная)<br />
      <strong>Сайт:</strong>
      <a href="https://minobr.nso.ru/" target="_blank">https://minobr.nso.ru/</a>
    </p>

    <h3>Место нахождения образовательной организации</h3>
    <p>
      <strong>Юридический адрес:</strong><br />
      630089, Российская Федерация, Сибирский федеральный округ, Новосибирская
      обл., г. Новосибирск, ул. Бориса Богаткова, дом 208, корпус 2
    </p>

    <div class="map-container">
      <iframe
        src="https://yandex.ru/map-widget/v1/?um=constructor%3A2176bde44a3a0278af824b3d4e41f7e66ef0d049a83924a08779f616ec73ade1&amp;source=constructor"
        width="100%"
        height="400"
        frameborder="0"
      ></iframe>
    </div>

    <h3>Режим и график работы</h3>
    <p>
      <strong>Режим работы:</strong><br />
      ПН - ПТ: с 09:00 до 20:00<br />
      СБ: с 10:00 до 15:00<br />
      ВС: выходной
    </p>

    <h3>Контакты</h3>
    <p>
      <strong>Контактный телефон:</strong><br />
      <a href="tel:+73832091990">(383) 209-19-90</a><br />
      <a href="tel:2141809">214-18-09</a>
    </p>
    <p>
      <strong>Адрес электронной почты:</strong><br />
      <a href="mailto:school.abc@mail.ru">school.abc@mail.ru</a>
    </p>
    <p>
      <strong>Адрес официального сайта:</strong><br />
      <a href="http://abc-school.ru/" target="_blank">http://abc-school.ru/</a>
    </p>

    <h3>Лицензия на осуществление образовательной деятельности</h3>
    <p>
      Лицензия на осуществление образовательной деятельности ЧУДО Лингвоцентр
      "Эй Би Си"
    </p>
    <p class="doc-link">
      📄 <a href="#" target="_blank">Лицензия</a>
    </p>

    <h3>Государственная аккредитация</h3>
    <p>Государственная аккредитация не требуется.</p>
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

a {
  color: var(--brand-orange);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.map-container {
  margin: 24px 0;
  border-radius: 16px;
  overflow: hidden;
}

.doc-link {
  font-size: 16px;
}
</style>
