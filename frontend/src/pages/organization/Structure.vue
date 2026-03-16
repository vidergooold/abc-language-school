<template>
  <div class="org-section">
    <h2 class="section-title">Структура и филиалы</h2>

    <div class="branches-list">
      <div v-for="branch in branches" :key="branch.id" class="branch-card">
        <h3>{{ branch.name }}</h3>
        <p><strong>Руководитель:</strong> {{ branch.director }}<br /><strong>Должность:</strong> {{ branch.position }}</p>
        <p><strong>Адрес:</strong> {{ branch.address }}</p>
        <p><strong>Телефон:</strong> <a :href="`tel:${branch.phone}`">{{ branch.phoneDisplay }}</a></p>
        <p><strong>Режим работы:</strong> {{ branch.schedule }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const branches = ref([
  { id: 1, name: 'Офис (главный)', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Бориса Богаткова, 208/2, офис 4, 5', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.00 до 20.00 без обеда' },
  { id: 2, name: 'Филиал в МАОУ Гимназия 11 «Гармония»', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Федосеева, д. 38', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 3, name: 'Филиал в МБОУ СОШ №56', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Планировочная, д. 7', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн/Чт с 11.30 до 15.30 без обеда' },
  { id: 4, name: 'Филиал в МБОУ СОШ №188', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Курганская, д. 36а', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 5, name: 'Филиал в МАОУ СОШ №218', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, Красный проспект, д. 320/1', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 6, name: 'Филиал в МАОУ «Гимназия №7 «Сибирская»', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Зорге, д. 42а', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 7, name: 'Филиал в МБОУ СОШ №186', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Бориса Богаткова, д. 189', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 8, name: 'Филиал в МБОУ СОШ №11', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Бориса Богаткова, д. 187', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 9, name: 'Филиал в МБОУ СОШ №2', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Чехова, д. 271', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 10, name: 'Филиал в МБОУ СОШ №199', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Лазурная, д. 27', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 11, name: 'Филиал в МБОУ СОШ №155', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, Ключ-Камышенское Плато, д. 1А', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 12, name: 'Филиал в МАОУ ЛИТ', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Римского-Корсакова, д. 13', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 13, name: 'Филиал в МБОУ СОШ №195', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. В. Высоцкого, д. 1', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 14, name: 'Филиал в МАОУ НГПЛ', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Декабристов, д. 86', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 15, name: 'Филиал в МБОУ Гимназия №9', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Калинина, д. 255', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 16, name: 'Филиал в МАОУ НЭЛ', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Крылова, д. 44', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 17, name: 'Филиал в МАОУ СОШ №216', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Виталия Потылицына, д. 9', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 18, name: 'Филиал в МАОУ СОШ №217', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Виктора Шевелева, д. 3', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 19, name: 'Филиал в МБОУ Гимназия №5', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Академическая, д. 9', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 20, name: 'Филиал в МБОУ СОШ №121 «Академическая»', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Тружеников, д. 10', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 21, name: 'Филиал в МБОУ СОШ №61 им. Н.М. Иванова', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Иванова, д. 9', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
  { id: 22, name: 'Филиал в МАОУ СОШ №222', director: 'Андрюнина Марина Викторовна', position: 'Директор', address: 'г. Новосибирск, ул. Кубовая, д. 100', phone: '+79139121809', phoneDisplay: '(913) 912-18-09', schedule: 'Пн-Пт с 9.50 до 18.30 без обеда' },
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
