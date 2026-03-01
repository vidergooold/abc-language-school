<template>
  <div class="org-section">
    <h2 class="section-title">Структура и филиалы</h2>

    <div class="branches-list">
      <div v-for="branch in branches" :key="branch.id" class="branch-card">
        <h3>{{ branch.name }}</h3>
        <p>
          <strong>Руководитель:</strong> {{ branch.director }}<br />
          <strong>Должность:</strong> {{ branch.position }}
        </p>
        <p><strong>Адрес:</strong> {{ branch.address }}</p>
        <p>
          <strong>Телефон:</strong>
          <a :href="`tel:${branch.phone}`">{{ branch.phoneDisplay }}</a>
        </p>
        <p><strong>Режим работы:</strong> {{ branch.schedule }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const branches = ref([
  {
    id: 1,
    name: 'Офис',
    director: 'Андрюнина Марина Викторовна',
    position: 'Директор',
    address: 'г. Новосибирск, ул. Бориса Богаткова, 208/2, офис 4, 5',
    phone: '+79139121809',
    phoneDisplay: '(913) 912-18-09',
    schedule: 'Пн-Пт с 9.00 до 20.00 без обеда',
  },
  {
    id: 2,
    name: 'Филиал в МАОУ Гимназия 11 «Гармония»',
    director: 'Андрюнина Марина Викторовна',
    position: 'Директор',
    address: 'г. Новосибирск, ул. Федосеева, д. 38',
    phone: '+79139121809',
    phoneDisplay: '(913) 912-18-09',
    schedule: 'Пн-Пт с 9.50 до 18.30 без обеда',
  },
  {
    id: 3,
    name: 'Филиал в МБОУ СОШ №56',
    director: 'Андрюнина Марина Викторовна',
    position: 'Директор',
    address: 'г. Новосибирск, ул. Планировочная, д. 7',
    phone: '+79139121809',
    phoneDisplay: '(913) 912-18-09',
    schedule: 'Пн/Чт с 11.30 до 15.30 без обеда',
  },
  // ... остальные филиалы (всего 22) — можешь скопировать из старого Organization.vue
])
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

.branches-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.branch-card {
  background: #ffe3cf;
  padding: 20px;
  border-radius: 12px;
}

.branch-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 12px;
}

.branch-card p {
  font-size: 15px;
  margin-bottom: 8px;
}

.branch-card a {
  color: var(--brand-orange);
  text-decoration: none;
}

.branch-card a:hover {
  text-decoration: underline;
}
</style>
