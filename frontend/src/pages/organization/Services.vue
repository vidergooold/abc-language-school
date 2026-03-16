<template>
  <div class="org-section">
    <h2 class="section-title">Платные образовательные услуги</h2>

    <p class="intro">
      ЧУДО Лингвоцентр «Эй Би Си» оказывает платные образовательные услуги по реализации образовательных программ дополнительного образования детей и взрослых.
    </p>

    <!-- Прайс-лист -->
    <h3>Стоимость обучения</h3>

    <div class="price-cards">
      <div v-for="item in prices" :key="item.label" class="price-card">
        <div class="price-card__header">
          <span class="price-card__duration">{{ item.duration }}</span>
          <span class="price-card__label">{{ item.label }}</span>
        </div>
        <div class="price-card__body">
          <div class="price-card__col">
            <div class="price-card__year">2023–2024</div>
            <div class="price-card__amount">{{ item.price2324 }} ₽</div>
            <div class="price-card__per">{{ item.per }}</div>
          </div>
          <div class="price-card__divider"></div>
          <div class="price-card__col price-card__col--new">
            <div class="price-card__year">2024–2025</div>
            <div class="price-card__amount">{{ item.price2425 }} ₽</div>
            <div class="price-card__per">{{ item.per }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Доп. условия -->
    <h3>Порядок оплаты</h3>
    <div class="info-cards">
      <div class="info-card">
        <div class="info-card__icon">📅</div>
        <div class="info-card__text">
          <strong>Ежемесячная оплата</strong>
          <p>Оплата производится до 10-го числа каждого месяца</p>
        </div>
      </div>
      <div class="info-card">
        <div class="info-card__icon">💳</div>
        <div class="info-card__text">
          <strong>Способы оплаты</strong>
          <p>Наличными, банковской картой или через онлайн-перевод</p>
        </div>
      </div>
      <div class="info-card">
        <div class="info-card__icon">📜</div>
        <div class="info-card__text">
          <strong>Договор</strong>
          <p>Обучение осуществляется на основании договора об оказании платных услуг</p>
        </div>
      </div>
      <div class="info-card">
        <div class="info-card__icon">ℹ️</div>
        <div class="info-card__text">
          <strong>Налоговый вычет</strong>
          <p>Вы можете оформить социальный налоговый вычет за обучение</p>
        </div>
      </div>
    </div>

    <p class="notice">
      Организация не взимает платы с родителей (законных представителей) за подготовку документов.
    </p>
  </div>
</template>

<script setup lang="ts">
const prices = [
  {
    duration: '45 мин',
    label: 'Дошкольники',
    price2324: '2 550',
    price2425: '2 700',
    per: 'в месяц',
  },
  {
    duration: '50 мин',
    label: 'FH1, AS1',
    price2324: '2 800',
    price2425: '3 100',
    per: 'в месяц',
  },
  {
    duration: '60 мин',
    label: 'AS2, AS3, AS4',
    price2324: '3 250',
    price2425: '3 500',
    per: 'в месяц',
  },
  {
    duration: '75 мин',
    label: 'GWA1+, GWA2',
    price2324: '4 000',
    price2425: '4 250',
    per: 'в месяц',
  },
  {
    duration: '90 мин',
    label: 'GWB1, GWB1+, GWB2, GWB2+, GWC1',
    price2324: '4 650',
    price2425: '4 900',
    per: 'в месяц',
  },
  {
    duration: 'Взрослые',
    label: 'Групповые занятия',
    price2324: '6 200',
    price2425: '6 500',
    per: 'в месяц',
  },
  {
    duration: '45 мин',
    label: 'Мини-группа (2 чел.)',
    price2324: '6 300',
    price2425: '6 600',
    per: 'в месяц',
  },
  {
    duration: '45 мин',
    label: 'Индивидуальные занятия',
    price2324: '1 050',
    price2425: '1 100',
    per: 'за занятие',
  },
  {
    duration: '45 мин',
    label: 'Китайский язык',
    price2324: '1 100',
    price2425: '1 200',
    per: 'за занятие',
  },
]
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
  margin-bottom: 16px;
}

h3 {
  font-size: 20px;
  font-weight: 700;
  margin-top: 32px;
  margin-bottom: 16px;
  color: var(--brand-purple);
}

.intro {
  color: #555;
  margin-bottom: 8px;
}

/* Price cards */
.price-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-top: 8px;
}

.price-card {
  border-radius: 16px;
  overflow: hidden;
  border: 2px solid #ffe3cf;
  background: #fff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}

.price-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

.price-card__header {
  background: linear-gradient(135deg, var(--brand-purple), #6b3fa0);
  color: #fff;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.price-card__duration {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.price-card__label {
  font-size: 13px;
  opacity: 0.85;
  font-weight: 500;
}

.price-card__body {
  display: flex;
  align-items: stretch;
}

.price-card__col {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.price-card__col--new {
  background: #fff7f0;
}

.price-card__divider {
  width: 1px;
  background: #ffe3cf;
  margin: 12px 0;
}

.price-card__year {
  font-size: 12px;
  color: #888;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.price-card__amount {
  font-size: 24px;
  font-weight: 800;
  color: var(--brand-orange);
  line-height: 1.1;
}

.price-card__per {
  font-size: 12px;
  color: #aaa;
}

/* Info cards */
.info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
  margin-top: 8px;
}

.info-card {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  background: #f5f0ff;
  border-radius: 14px;
  padding: 16px 18px;
  border: 1.5px solid #e8deff;
}

.info-card__icon {
  font-size: 28px;
  line-height: 1;
  flex-shrink: 0;
}

.info-card__text strong {
  font-size: 15px;
  color: var(--brand-purple);
  display: block;
  margin-bottom: 4px;
}

.info-card__text p {
  font-size: 14px;
  color: #555;
  margin: 0;
}

.notice {
  background: #fff7f0;
  border-left: 4px solid var(--brand-orange);
  padding: 14px 18px;
  border-radius: 10px;
  font-size: 15px;
  color: #555;
  margin-top: 28px;
}
</style>
