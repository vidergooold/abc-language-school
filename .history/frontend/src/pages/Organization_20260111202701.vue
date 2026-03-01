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

          <!-- Программа 5 -->
          <details class="program-item">
            <summary class="program-title">
              Рабочая программа по английскому языку "Gateway B1"
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

          <!-- Программа 6 -->
          <details class="program-item">
            <summary class="program-title">
              Рабочая программа по английскому языку "FlyHigh 1"
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
        </div>
      </div>
    </section>

    <!-- Руководство -->
    <section id="management" class="section">
      <h2 class="section-title">Руководство</h2>
      <div class="section-content">
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
    </section>

    <!-- Педагогический состав -->
    <section id="staff" class="section">
      <h2 class="section-title">Педагогический состав</h2>
      <div class="section-content">
        <h3>Персональный состав педагогических работников</h3>
        <p><strong>Дополнительное образование детей и взрослых</strong></p>

        <div class="teachers-list">
          <!-- Преподаватель 1 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Белова Александра Анатольевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong
                  >Преподаваемые учебные предметы, курсы, дисциплины
                  (модули):</strong
                >
                английский язык
              </p>
              <p><strong>Ученая степень:</strong> Не указано</p>
              <p><strong>Ученое звание:</strong> Не указано</p>
              <p><strong>Стаж работы по специальности:</strong> Не указан</p>
              <p>
                <strong
                  >Сведения о продолжительности опыта (лет) работы в
                  профессиональной сфере, соответствующей образовательной
                  деятельности:</strong
                >
                10
              </p>
              <p>
                <strong
                  >Уровень профессионального образования с указанием наименования
                  направления подготовки:</strong
                >
              </p>
              <ul>
                <li><strong>Уровень образования:</strong> Высшее</li>
                <li>
                  <strong>Направление подготовки и/или специальность:</strong>
                  учитель английского и немецкого языка
                </li>
                <li><strong>Квалификация:</strong> Бакалавр</li>
              </ul>
              <p>
                <strong>Сведения о повышении квалификации:</strong> Не указано
              </p>
              <p>
                <strong>Сведения о профессиональной переподготовке:</strong> Не
                указано
              </p>
              <p>
                <strong
                  >Наименование программ, в реализации которых участвует
                  педагогический работник:</strong
                >
                Не указано
              </p>
            </div>
          </details>

          <!-- Преподаватель 2 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Григорьева Дарья Дмитриевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 3 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Данилова Мария Анатольевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 4 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Евдокимова Полина Евгеньевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 5 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Колесник Любовь Николаевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 6 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Куцых Марина Евгеньевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 7 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Кривилева Галина Александровна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 8 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Лукьянова Светлана Ярославовна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 9 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Митина Ольга Сергеевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 10 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Осинина Светлана Николаевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 11 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Пасикан Ангелина Сергеевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 12 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Переведенцева Александра Андреевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 13 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Позднякова Виктория Сергеевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 14 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Рубе Дарья Васильевна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 15 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Стафеева Яна Викторовна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский яз
                             <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 16 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Темлякова Анна Михайловна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 17 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Федорова Анфиса Вячеславовна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>

          <!-- Преподаватель 18 -->
          <details class="teacher-item">
            <summary class="teacher-title">
              Фомина Снежанна Олеговна (преподаватель)
            </summary>
            <div class="teacher-details">
              <p><strong>Занимаемая должность:</strong> преподаватель</p>
              <p>
                <strong>Преподаваемые предметы:</strong> английский язык
              </p>
            </div>
          </details>
        </div>
      </div>
    </section>

    <!-- Материально-техническое обеспечение -->
    <section id="facilities" class="section">
      <h2 class="section-title">
        Материально-техническое обеспечение и оснащенность образовательного
        процесса. Доступная среда
      </h2>
      <div class="section-content">
        <h3>
          О наличии у образовательной организации на праве собственности или ином
          законном основании зданий, строений, сооружений, территорий
        </h3>

        <div class="facility-card">
          <h4>Офис</h4>
          <p>
            <strong>Адрес объекта:</strong> г. Новосибирск, ул.Бориса Богаткова
            260/2
          </p>
          <p><strong>Назначение объекта:</strong> Нежилое</p>
          <p><strong>Площадь:</strong> 86.7 м²</p>
          <p class="doc-link">
            📄
            <a href="#" target="_blank"
              >Свидетельство о государственной регистрации права (PDF; 4.6
              Мб)</a
            >
          </p>
        </div>

        <h3>
          О наличии оборудованных учебных кабинетов, объектов для проведения
          практических занятий
        </h3>

        <div class="facility-card">
          <h4>ОБОРУДОВАННЫЕ УЧЕБНЫЕ КАБИНЕТЫ</h4>
          <p>
            <strong>Адрес:</strong> г.Новосибирск, ул. Бориса Богаткова, д.
            208/2, офис 4 и 5
          </p>
          <p>
            <strong>Общее количество оборудованных учебных кабинетов:</strong> 4
          </p>
        </div>

        <div class="facility-card">
          <h4>ОБЪЕКТЫ ДЛЯ ПРОВЕДЕНИЯ ПРАКТИЧЕСКИХ ЗАНЯТИЙ</h4>
          <p>
            <strong>Адрес:</strong> г.Новосибирск, ул. Бориса Богаткова, д.
            208/2, офис 4 и 5
          </p>
          <p>
            <strong>Общее количество объектов для практических занятий:</strong>
            4
          </p>
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
          <p>
            <strong>Адрес:</strong> г. Новосибирск, ул. Бориса Богаткова, д.
            208/2
          </p>
          <p><strong>Количество мест:</strong> 5</p>
          <p>
            <strong
              >Приспособленность для использования инвалидами и лицами с
              ОВЗ:</strong
            >
            -
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
    </section>

    <!-- Платные образовательные услуги -->
    <section id="services" class="section">
      <h2 class="section-title">Платные образовательные услуги</h2>
      <div class="section-content">
        <h3>О порядке оказания платных образовательных услуг</h3>

        <div class="services-list">
          <!-- Услуга 1 -->
          <div class="service-item">
            <h4>Дошкольники (45 минут) (2025-2026 год)</h4>
            <div class="service-docs">
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образец договора об оказании платных образовательных услуг
                  (DOCX; 33.28 Кб)</a
                >
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Документ об утверждении стоимости (прайс-лист) (PDF; 101.58
                  Кб)</a
                >
              </p>
            </div>
          </div>

          <!-- Услуга 2 -->
          <div class="service-item">
            <h4>FH1, AS1 (50 минут) (2025-2026 год)</h4>
            <div class="service-docs">
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образец договора об оказании платных образовательных услуг
                  (DOCX; 33.28 Кб)</a
                >
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Документ об утверждении стоимости (прайс-лист) (PDF; 101.58
                  Кб)</a
                >
              </p>
            </div>
          </div>

          <!-- Услуга 3 -->
          <div class="service-item">
            <h4>AS2, AS3, AS4 (60 минут) (2025-2026 год)</h4>
            <div class="service-docs">
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образец договора об оказании платных образовательных услуг
                  (DOCX; 33.28 Кб)</a
                >
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Документ об утверждении стоимости (прайс-лист) (PDF; 101.58
                  Кб)</a
                >
              </p>
            </div>
          </div>

          <!-- Услуга 4 -->
          <div class="service-item">
            <h4>GWA1+, GWA2 (75 минут) (2025-2026 год)</h4>
            <div class="service-docs">
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образец договора об оказании платных образовательных услуг
                  (DOCX; 33.28 Кб)</a
                >
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Документ об утверждении стоимости (прайс-лист) (PDF; 101.58
                  Кб)</a
                >
              </p>
            </div>
          </div>

          <!-- Услуга 5 -->
          <div class="service-item">
            <h4>GWB1, GWB1+, GWB2, GWB2+, GWC1 (90 минут) (2025-2026 год)</h4>
            <div class="service-docs">
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образец договора об оказании платных образовательных услуг
                  (DOCX; 33.28 Кб)</a
                >
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Документ об утверждении стоимости (прайс-лист) (PDF; 101.58
                  Кб)</a
                >
              </p>
            </div>
          </div>

          <!-- Услуга 6 -->
          <div class="service-item">
            <h4>Взрослые (2025-2026 год)</h4>
            <div class="service-docs">
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образец договора об оказании платных образовательных услуг
                  (DOCX; 33.28 Кб)</a
                >
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Документ об утверждении стоимости (прайс-лист) (PDF; 101.58
                  Кб)</a
                >
              </p>
            </div>
          </div>

          <!-- Услуга 7 -->
          <div class="service-item">
            <h4>Мини-группа (2 человека) (45 минут) (2025-2026 год)</h4>
            <div class="service-docs">
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образец договора об оказании платных образовательных услуг
                  (DOCX; 33.28 Кб)</a
                >
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Документ об утверждении стоимости (прайс-лист) (PDF; 101.58
                  Кб)</a
                >
              </p>
            </div>
          </div>

          <!-- Услуга 8 -->
          <div class="service-item">
            <h4>Индивидуальные занятия (45 мин) (2025-2026 год)</h4>
            <div class="service-docs">
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образец договора об оказании платных образовательных услуг
                  (DOCX; 33.28 Кб)</a
                >
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Документ об утверждении стоимости (прайс-лист) (PDF; 101.58
                  Кб)</a
                >
              </p>
            </div>
          </div>

          <!-- Услуга 9 -->
          <div class="service-item">
            <h4>Китайский язык (45 мин) (2025-2026 год)</h4>
            <div class="service-docs">
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Образец договора об оказании платных образовательных услуг
                  (DOCX; 33.28 Кб)</a
                >
              </p>
              <p class="doc-link">
                📄
                <a href="#" target="_blank"
                  >Документ об утверждении стоимости (прайс-лист) (PDF; 101.58
                  Кб)</a
                >
              </p>
            </div>
          </div>
        </div>

        <h3>
          Об установлении размера платы, взимаемой с родителей (
                <h3>
          Об установлении размера платы, взимаемой с родителей (законных
          представителей)
        </h3>
        <p class="notice">
          Организация не взимает платы с родителей (законных представителей)
        </p>
      </div>
    </section>

    <!-- Финансово-хозяйственная деятельность -->
    <section id="finance" class="section">
      <h2 class="section-title">Финансово-хозяйственная деятельность</h2>
      <div class="section-content">
        <h3>
          Информация о поступлении и расходовании финансовых и материальных
          средств по итогам финансового года
        </h3>
        <p class="doc-link">
          📊
          <a href="#" target="_blank" download>ОН0002 (2024 год) (XLSX)</a>
        </p>
      </div>
    </section>

    <!-- Вакантные места -->
    <section id="vacancies" class="section">
      <h2 class="section-title">
        Вакантные места для приема (перевода) обучающихся
      </h2>
      <div class="section-content">
        <p class="placeholder">
          Информация о наличии вакантных мест уточняется по телефону
          <a href="tel:+73832091990">(383) 209-19-90</a>
        </p>
      </div>
    </section>

    <!-- Международное сотрудничество -->
    <section id="international" class="section">
      <h2 class="section-title">Международное сотрудничество</h2>
      <div class="section-content">
        <p class="notice">
          ЧУДО Лингвоцентр "Эй Би Си" не участвует в международной
          образовательной деятельности.
        </p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const branches = ref(
