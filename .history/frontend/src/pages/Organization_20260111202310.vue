<template>
  <div class="organization-page">
    <h1 class="page-title">Сведения об образовательной организации</h1>

    <!-- Навигация по разделам -->
    <nav class="sections-nav">
      <a href="#main" class="nav-link">Основные сведения</a>
      <a href="#structure" class="nav-link">Структура и филиалы</a>
      <a href="#docs" class="nav-link">Документы</a>
      <a href="#education" class="nav-link">Образование</a>
      <a href="#management" class="nav-link">Руководство</a>
      <a href="#staff" class="nav-link">Педагогический состав</a>
      <a href="#facilities" class="nav-link">Материально-техническое обеспечение</a>
      <a href="#services" class="nav-link">Платные услуги</a>
      <a href="#finance" class="nav-link">Финансы</a>
      <a href="#vacancies" class="nav-link">Вакантные места</a>
      <a href="#international" class="nav-link">Международное сотрудничество</a>
    </nav>

    <!-- Основные сведения -->
    <section id="main" class="section">
      <h2 class="section-title">Основные сведения</h2>
      <div class="section-content">
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
          <strong>Адрес:</strong> 630007, Новосибирская область, город
          Новосибирск, Красный пр-кт, д. 18<br />
          <strong>Телефон:</strong>
          <a href="tel:+73832387320">(383) 238-73-20</a> (приемная)<br />
          <strong>Сайт:</strong>
          <a href="https://minobr.nso.ru/" target="_blank"
            >https://minobr.nso.ru/</a
          >
        </p>

        <h3>Место нахождения образовательной организации</h3>
        <p>
          <strong>Юридический адрес:</strong><br />
          630089, Российская Федерация, Сибирский федеральный округ,
          Новосибирская обл., г. Новосибирск, ул. Бориса Богаткова, дом 208,
          корпус 2
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
          Лицензия на осуществление образовательной деятельности ЧУДО
          Лингвоцентр "Эй Би Си"
        </p>
        <p class="doc-link">
          📄 <a href="#" target="_blank">Лицензия (PDF; 776.32 Кб)</a>
        </p>

        <h3>Государственная аккредитация</h3>
        <p>Государственная аккредитация не требуется.</p>
      </div>
    </section>

    <!-- Структура и филиалы -->
    <section id="structure" class="section">
      <h2 class="section-title">Структура и филиалы</h2>
      <div class="section-content">
        <div class="branches-list">
          <div v-for="branch in branches" :key="branch.id" class="branch-card">
            <h3>{{ branch.name }}</h3>
            <p>
              <strong>Руководитель:</strong> {{ branch.director }}<br />
              <strong>Должность:</strong> {{ branch.position }}
            </p>
            <p>
              <strong>Адрес:</strong> {{ branch.address }}
            </p>
            <p>
              <strong>Телефон:</strong>
              <a :href="`tel:${branch.phone}`">{{ branch.phoneDisplay }}</a>
            </p>
            <p>
              <strong>Режим работы:</strong> {{ branch.schedule }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Документы -->
    <section id="docs" class="section">
      <h2 class="section-title">Документы</h2>
      <div class="section-content">
        <h3>Иные документы</h3>
        <p class="doc-link">
          📄
          <a href="#" target="_blank"
            >Свидетельство о государственной регистрации некоммерческой
            организации (PDF; 4.95 Мб)</a
          >
        </p>
        <p class="doc-info">
          Выдан: Инспекция ФНС по Октябрьскому району, г.Новосибирска,
          17.06.2021.
        </p>
      </div>
    </section>

    <!-- Образование -->
    <section id="education" class="section">
      <h2 class="section-title">Образование</h2>
      <div class="section-content">
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
          <!-- Программа 1 -->
          <details class="program-item">
            <summary class="program-title">
              Рабочая программа по английскому языку "Academy Stars 1"
            </summary>
            <div class="program-details">
              <p>
                <strong
                  >Учебный предмет, курс, дисциплина (модуль), предусмотренные
                  соответствующей образовательной программой:</strong
                ><br />
                Не указаны
              </p>
              <p>
                <strong
                  >Практика, предусмотренная образовательной программой:</strong
                ><br />
                Не указана
              </p>
              <p>
                <strong
                  >Об использовании при реализации образовательной программы
                  электронного обучения и дистанционных образовательных
                  технологий:</strong
                ><br />
                Не используются электронное обучение и дистанционные
                образовательные технологии
              </p>
              <p>
                <strong>Уровень образования:</strong> Не указан<br />
                <strong
                  >Код профессии, специальности, направления подготовки, научной
                  специальности:</strong
                >
                Не указан<br />
                <strong
                  >Наименование профессии, специальности, направления подготовки,
                  научной специальности:</strong
                >
                Не указано
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образовательная программа (PDF; 487.48 Кб)</a
                >
              </p>
            </div>
          </details>

          <!-- Программа 2 -->
          <details class="program-item">
            <summary class="program-title">
              Рабочая программа по английскому языку "Academy Stars 2"
            </summary>
            <div class="program-details">
              <p>
                <strong
                  >Учебный предмет, курс, дисциплина (модуль), предусмотренные
                  соответствующей образовательной программой:</strong
                ><br />
                Не указаны
              </p>
              <p>
                <strong
                  >Практика, предусмотренная образовательной программой:</strong
                ><br />
                Не указана
              </p>
              <p>
                <strong
                  >Об использовании при реализации образовательной программы
                  электронного обучения и дистанционных образовательных
                  технологий:</strong
                ><br />
                Не используются электронное обучение и дистанционные
                образовательные технологии
              </p>
              <p>
                <strong>Уровень образования:</strong> Не указан<br />
                <strong
                  >Код профессии, специальности, направления подготовки, научной
                  специальности:</strong
                >
                Не указан<br />
                <strong
                  >Наименование профессии, специальности, направления подготовки,
                  научной специальности:</strong
                >
                Не указано
              </p>
              <p class="doc-link">
                📄 <a href="#" target="_blank">Образовательная программа (PDF)</a>
              </p>
            </div>
          </details>

          <!-- Программа 3 -->
          <details class="program-item">
            <summary class="program-title">
              Рабочая программа по английскому языку "Academy Stars 3"
            </summary>
            <div class="program-details">
              <p>
                <strong
                  >Учебный предмет, курс, дисциплина (модуль), предусмотренные
                  соответствующей образовательной программой:</strong
                ><br />
                Не указаны
              </p>
              <p>
                <strong
                  >Практика, предусмотренная образовательной программой:</strong
                ><br />
                Не указана
              </p>
              <p>
                <strong
                  >Об использовании при реализации образовательной программы
                  электронного обучения и дистанционных образовательных
                  технологий:</strong
                ><br />
                Не используются электронное обучение и дистанционные
                образовательные технологии
              </p>
              <p>
                <strong>Уровень образования:</strong> Не указан<br />
                <strong
                  >Код профессии, специальности, направления подготовки, научной
                  специальности:</strong
                >
                Не указан<br />
                <strong
                  >Наименование профессии, специальности, направления подготовки,
                  научной специальности:</strong
                >
                Не указано
              </p>
              <p class="doc-link">
                📄 <a href="#" target="_blank">Образовательная программа (PDF)</a>
              </p>
            </div>
          </details>

          <!-- Программа 4 -->
          <details class="program-item">
            <summary class="program-title">
              Рабочая программа по английскому языку "Gateway A1+"
            </summary>
            <div class="program-details">
              <p>
                <strong
                  >Учебный предмет, курс, дисциплина (модуль), предусмотренные
                  соответствующей образовательной программой:</strong
                ><br />
                Не указаны
              </p>
              <p>
                <strong
                  >Практика, предусмотренная образовательной программой:</strong
                ><br />
                Не указана
              </p>
              <p>
                <strong
                  >Об использовании при реализации образовательной программы
                  электронного обучения и дистанционных образовательных
                  технологий:</strong
                ><br />
                Не используются электронное обучение и дистанционные
                образовательные технологии
              </p>
              <p>
                <strong>Уровень образования:</strong> Не указан<br />
                <strong
                  >Код
                