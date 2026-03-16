<template>
  <div class="testing-page">
    <!-- Выбор теста -->
    <template v-if="!activeTest && !result">
      <h1 class="page-title">Узнай свой уровень английского языка!</h1>
      <p class="page-subtitle">
        Определение уровня владения английским языком необходимо для подбора подходящей программы обучения.
        Наш бесплатный онлайн-тест поможет оценить уровень всего за 10–20 минут. Выбирайте нужную возрастную ступень!
      </p>
      <div class="test-grid">
        <button class="test-card" @click="startTest('grade12')">Тест для школьников 1–2 класса</button>
        <button class="test-card" @click="startTest('grade34')">Тест для школьников 3–4 класса</button>
        <button class="test-card" @click="startTest('grade57')">Тест для школьников 5–7 класса</button>
        <button class="test-card" @click="startTest('grade811')">Тест для школьников 8–11 класса</button>
        <button class="test-card test-card--center" @click="startTest('adult')">Тест для взрослых</button>
      </div>
    </template>

    <!-- Сам тест -->
    <template v-else-if="activeTest && !result">
      <div class="test-header">
        <h2 class="test-title">{{ testTitles[activeTest] }}</h2>
        <span class="test-progress">Вопрос {{ currentQ + 1 }}/{{ questions.length }}</span>
      </div>

      <div class="question-block">
        <p class="question-text" v-html="questions[currentQ].q"></p>
        <div class="options">
          <label
            v-for="(opt, i) in questions[currentQ].options"
            :key="i"
            class="option"
            :class="{ selected: answers[currentQ] === i }"
          >
            <input type="radio" :name="'q' + currentQ" :value="i" v-model="answers[currentQ]" hidden />
            {{ opt }}
          </label>
        </div>
      </div>

      <div class="test-nav">
        <button class="btn-back" @click="prevQ" :disabled="currentQ === 0">Назад</button>
        <button
          class="btn-next"
          @click="nextQ"
          :disabled="answers[currentQ] === undefined"
        >
          {{ currentQ === questions.length - 1 ? 'Узнать результат' : 'Next' }}
        </button>
      </div>
    </template>

    <!-- Результат -->
    <template v-else-if="result">
      <div class="result-block">
        <h2 class="result-title">Ваш результат</h2>
        <div class="result-level">{{ result.level }}</div>
        <p class="result-desc">{{ result.desc }}</p>
        <div class="result-actions">
          <RouterLink to="/enroll" class="btn-enroll">Записаться на курс</RouterLink>
          <button class="btn-restart" @click="restart">Пройти ещё раз</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'

type TestKey = 'grade12' | 'grade34' | 'grade57' | 'grade811' | 'adult'

const activeTest = ref<TestKey | null>(null)
const currentQ = ref(0)
const answers = ref<(number | undefined)[]>([])
const result = ref<{ level: string; desc: string } | null>(null)

const testTitles: Record<TestKey, string> = {
  grade12: 'Тест 1–2 класс',
  grade34: 'Тест 3–4 класс',
  grade57: 'Тест 5–7 класс',
  grade811: 'Тест 8–11 класс',
  adult: 'Тест для взрослых',
}

const allTests: Record<TestKey, { q: string; options: string[]; answer: number }[]> = {
  grade12: [
    { q: 'Fill in the gaps:<br><strong>A B C D __ F G H I J K L M N O P Q R __ T U V W X Y Z</strong>', options: ['S / L', 'E / S', 'H / K', 'O / Y'], answer: 1 },
    { q: 'What colour is the sky?', options: ['Green', 'Blue', 'Red', 'Yellow'], answer: 1 },
    { q: 'Choose the correct word: I __ a student.', options: ['am', 'is', 'are', 'be'], answer: 0 },
    { q: 'How many legs does a dog have?', options: ['2', '4', '6', '8'], answer: 1 },
    { q: 'What is this? 🍎', options: ['A banana', 'An apple', 'An orange', 'A grape'], answer: 1 },
    { q: 'Choose the correct word: She __ a cat.', options: ['have', 'has', 'had', 'is have'], answer: 1 },
    { q: 'What number comes after 9?', options: ['8', '11', '10', '7'], answer: 2 },
    { q: 'What day comes after Monday?', options: ['Sunday', 'Wednesday', 'Saturday', 'Tuesday'], answer: 3 },
    { q: 'Choose: The cat is __ the box. 📦🐱', options: ['under', 'in', 'on', 'behind'], answer: 1 },
    { q: 'What is the opposite of "big"?', options: ['tall', 'small', 'fast', 'old'], answer: 1 },
    { q: 'Choose: I __ to school every day.', options: ['go', 'goes', 'going', 'went'], answer: 0 },
    { q: 'What season comes after summer?', options: ['Spring', 'Winter', 'Autumn', 'Summer again'], answer: 2 },
    { q: 'Choose the correct sentence:', options: ['He are happy.', 'She is happy.', 'They is happy.', 'I are happy.'], answer: 1 },
    { q: 'What is 3 + 4 in English?', options: ['Six', 'Eight', 'Seven', 'Nine'], answer: 2 },
    { q: 'Choose: My name __ Anna.', options: ['am', 'are', 'is', 'be'], answer: 2 },
    { q: 'What animal says "Woof"?', options: ['Cat', 'Dog', 'Cow', 'Bird'], answer: 1 },
    { q: 'Choose: Look! It __ raining.', options: ['am', 'is', 'are', 'be'], answer: 1 },
    { q: 'What colour is a banana?', options: ['Red', 'Blue', 'Yellow', 'Green'], answer: 2 },
    { q: 'Choose: There __ two books on the table.', options: ['is', 'are', 'am', 'be'], answer: 1 },
    { q: 'Choose the correct question: __ you like pizza?', options: ['Is', 'Are', 'Do', 'Does'], answer: 2 },
    { q: 'What is the plural of "child"?', options: ['Childs', 'Childes', 'Children', 'Childrens'], answer: 2 },
    { q: 'Choose: I __ breakfast at 7 o\'clock yesterday.', options: ['eat', 'eats', 'ate', 'eating'], answer: 2 },
    { q: 'What month comes after January?', options: ['March', 'December', 'February', 'April'], answer: 2 },
    { q: 'Choose: Can you __ English?', options: ['speaks', 'speaking', 'speak', 'spoke'], answer: 2 },
  ],
  grade34: [
    { q: 'Choose: She __ her homework every evening.', options: ['do', 'does', 'did', 'done'], answer: 1 },
    { q: 'What is the past tense of "go"?', options: ['Goed', 'Goes', 'Went', 'Gone'], answer: 2 },
    { q: 'Choose: There __ a lot of children in the park.', options: ['is', 'are', 'was', 'be'], answer: 1 },
    { q: 'Choose the correct translation: «большой»', options: ['small', 'tall', 'big', 'fat'], answer: 2 },
    { q: 'Choose: I __ TV when mum came home.', options: ['watch', 'watched', 'was watching', 'am watching'], answer: 2 },
    { q: 'What is the plural of "mouse"?', options: ['Mouses', 'Mouse', 'Mice', 'Mices'], answer: 2 },
    { q: 'Choose: He __ never been to London.', options: ['is', 'has', 'have', 'had'], answer: 1 },
    { q: 'Choose: It\'s the __ building in the city.', options: ['tall', 'taller', 'most tall', 'tallest'], answer: 3 },
    { q: 'Choose: We __ pizza for dinner yesterday.', options: ['eat', 'eats', 'ate', 'eating'], answer: 2 },
    { q: 'Choose the correct question tag: It\'s cold, __?', options: ['isn\'t it', 'is it', 'wasn\'t it', 'doesn\'t it'], answer: 0 },
    { q: 'Choose: She can __ very fast.', options: ['runs', 'running', 'run', 'ran'], answer: 2 },
    { q: 'What is the opposite of "early"?', options: ['Fast', 'Late', 'Slow', 'Never'], answer: 1 },
    { q: 'Choose: I __ to the cinema last week.', options: ['go', 'goes', 'went', 'gone'], answer: 2 },
    { q: 'Choose: __ you ever tried sushi?', options: ['Do', 'Did', 'Have', 'Are'], answer: 2 },
    { q: 'Choose the correct spelling:', options: ['Recieve', 'Receive', 'Receve', 'Receeve'], answer: 1 },
    { q: 'Choose: My brother is __ than me.', options: ['old', 'more old', 'older', 'oldest'], answer: 2 },
    { q: 'Choose: She __ in Moscow since 2015.', options: ['lives', 'lived', 'has lived', 'is living'], answer: 2 },
    { q: 'Choose: We __ if it rains.', options: ['stay home', 'will stay home', 'stayed home', 'are staying'], answer: 1 },
    { q: 'Choose: The book __ written in 1900.', options: ['is', 'was', 'were', 'has'], answer: 1 },
    { q: 'Choose: I wish I __ more time.', options: ['have', 'had', 'has', 'having'], answer: 1 },
    { q: 'Choose: By the time he arrived, she __ already left.', options: ['has', 'have', 'had', 'was'], answer: 2 },
    { q: 'Choose: The film __ for two hours.', options: ['lasted', 'lasts', 'lasting', 'has last'], answer: 0 },
    { q: 'Choose: He speaks English __.', options: ['good', 'goodly', 'well', 'better good'], answer: 2 },
    { q: 'Choose: If I were rich, I __ travel the world.', options: ['will', 'would', 'can', 'shall'], answer: 1 },
  ],
  grade57: [
    { q: 'Choose: She __ to Paris three times.', options: ['went', 'has been', 'goes', 'is going'], answer: 1 },
    { q: 'Choose: I wish I __ harder at school.', options: ['study', 'studied', 'had studied', 'have studied'], answer: 2 },
    { q: 'Choose the correct passive: The letter __ yesterday.', options: ['sent', 'was sent', 'is sent', 'has sent'], answer: 1 },
    { q: 'Choose: By 2030, scientists __ a cure for cancer.', options: ['find', 'will find', 'will have found', 'found'], answer: 2 },
    { q: 'Choose: She asked me where I __.', options: ['live', 'lived', 'was living', 'am living'], answer: 1 },
    { q: 'Choose: Despite __ hard, he failed the exam.', options: ['study', 'studied', 'studying', 'to study'], answer: 2 },
    { q: 'Choose the correct form: He __ in London when the war started.', options: ['lived', 'was living', 'has lived', 'lives'], answer: 1 },
    { q: 'Choose: __ I been waiting here for an hour!', options: ['Have', 'Did', 'Was', 'Am'], answer: 0 },
    { q: 'Choose: The manager, __ phoned yesterday, wants a meeting.', options: ['who', 'which', 'that', 'whose'], answer: 0 },
    { q: 'Choose: She __  to New York next month.', options: ['will fly', 'is flying', 'flies', 'fly'], answer: 1 },
    { q: 'What does "inevitable" mean?', options: ['невероятный', 'неизбежный', 'невидимый', 'неважный'], answer: 1 },
    { q: 'Choose: I\'d rather you __ smoking.', options: ['stop', 'stopped', 'to stop', 'stopping'], answer: 1 },
    { q: 'Choose: It\'s high time we __ a decision.', options: ['make', 'made', 'will make', 'making'], answer: 1 },
    { q: 'Choose: __ the fact that it rained, we enjoyed the trip.', options: ['Despite', 'Although', 'However', 'In spite'], answer: 0 },
    { q: 'Choose: He denied __ the money.', options: ['to steal', 'steal', 'stealing', 'stolen'], answer: 2 },
    { q: 'Choose: No sooner __ I sat down than the phone rang.', options: ['had', 'have', 'did', 'was'], answer: 0 },
    { q: 'Choose the correct conditional: If you __ me earlier, I could have helped.', options: ['tell', 'told', 'had told', 'would tell'], answer: 2 },
    { q: 'Choose: The proposal was __ by the committee.', options: ['turn down', 'turned down', 'turning down', 'turns down'], answer: 1 },
    { q: 'What is a synonym of "eloquent"?', options: ['silent', 'articulate', 'confused', 'brief'], answer: 1 },
    { q: 'Choose: She\'s used to __ early.', options: ['get up', 'got up', 'getting up', 'gets up'], answer: 2 },
    { q: 'Choose: The more you practice, __ you become.', options: ['the better', 'better', 'the best', 'most better'], answer: 0 },
    { q: 'Choose: He must have __ the train.', options: ['miss', 'missed', 'missing', 'to miss'], answer: 1 },
    { q: 'Choose: __ he studied hard, he failed.', options: ['Despite', 'Although', 'Because', 'Since'], answer: 1 },
    { q: 'Choose: She suggested __ to the cinema.', options: ['to go', 'go', 'going', 'gone'], answer: 2 },
  ],
  grade811: [
    { q: 'Choose: By the time she arrived, the meeting __.', options: ['ended', 'has ended', 'had ended', 'was ending'], answer: 2 },
    { q: 'Choose the correct passive: The project __ completed by next Friday.', options: ['will be', 'is', 'was', 'has been'], answer: 0 },
    { q: 'Choose: She spoke so quietly that I __ hear her.', options: ['couldn\'t', 'can\'t', 'won\'t', 'shouldn\'t'], answer: 0 },
    { q: 'Choose: I regret __ that opportunity.', options: ['to miss', 'missing', 'miss', 'missed'], answer: 1 },
    { q: 'Choose: Were it not for his help, we __ failed.', options: ['would have', 'will have', 'would', 'had'], answer: 0 },
    { q: 'What does "ambiguous" mean?', options: ['однозначный', 'неоднозначный', 'скучный', 'точный'], answer: 1 },
    { q: 'Choose: He is known __ three languages.', options: ['to speak', 'speaking', 'speak', 'spoken'], answer: 0 },
    { q: 'Choose: Scarcely __ arrived when problems began.', options: ['had he', 'he had', 'has he', 'he has'], answer: 0 },
    { q: 'Choose: The scientist __ discovered the cure won a Nobel Prize.', options: ['who', 'which', 'whose', 'whom'], answer: 0 },
    { q: 'Choose: She\'d sooner __ abroad than stay here.', options: ['to go', 'going', 'go', 'gone'], answer: 2 },
    { q: 'Choose: The results __ interpreted carefully.', options: ['must be', 'must', 'should', 'need'], answer: 0 },
    { q: 'What is the meaning of "pragmatic"?', options: ['теоретический', 'практичный', 'пассивный', 'агрессивный'], answer: 1 },
    { q: 'Choose: Not only __ he rude, but also aggressive.', options: ['was', 'is', 'were', 'had'], answer: 0 },
    { q: 'Choose: I would rather you __ tell anyone.', options: ['don\'t', 'won\'t', 'didn\'t', 'hadn\'t'], answer: 2 },
    { q: 'Choose: She is said __ a brilliant scientist.', options: ['being', 'to be', 'be', 'been'], answer: 1 },
    { q: 'Choose: Had I known, I __ differently.', options: ['would act', 'will have acted', 'would have acted', 'acted'], answer: 2 },
    { q: 'Choose: The phenomenon __ extensively in the 1990s.', options: ['studied', 'was studied', 'has studied', 'is studied'], answer: 1 },
    { q: 'What is an antonym of "verbose"?', options: ['chatty', 'talkative', 'concise', 'fluent'], answer: 2 },
    { q: 'Choose: Little __ that his plan would fail.', options: ['he knew', 'did he know', 'he did know', 'knew he'], answer: 1 },
    { q: 'Choose: The report needs __.', options: ['revise', 'to revise', 'revising', 'revised'], answer: 2 },
    { q: 'Choose: __ as it may seem, the results were positive.', options: ['Strangely', 'Strange', 'Stranger', 'Most strange'], answer: 1 },
    { q: 'Choose: The delegation arrived, __ by journalists.', options: ['accompany', 'accompanied', 'accompanying', 'to accompany'], answer: 1 },
    { q: 'Choose: She can\'t help __ about the future.', options: ['worry', 'to worry', 'worried', 'worrying'], answer: 3 },
    { q: 'Choose: The new law __ effect from January.', options: ['takes', 'is taking', 'took', 'will take'], answer: 3 },
  ],
  adult: [
    { q: 'Choose: By the time she arrived, the meeting __.', options: ['ended', 'has ended', 'had ended', 'was ending'], answer: 2 },
    { q: 'What does "eloquent" mean?', options: ['молчаливый', 'красноречивый', 'запутанный', 'скромный'], answer: 1 },
    { q: 'Choose: Were it not for his support, we __ the project.', options: ['would not finish', 'will not finish', 'would not have finished', 'did not finish'], answer: 2 },
    { q: 'Choose: Not until he retired __ how much he had achieved.', options: ['he realised', 'did he realise', 'he did realise', 'realised he'], answer: 1 },
    { q: 'Choose: The proposal is said __ rejected.', options: ['to have been', 'to be', 'being', 'have been'], answer: 0 },
    { q: 'Choose: She\'d sooner __ abroad than stay here.', options: ['to go', 'going', 'go', 'gone'], answer: 2 },
    { q: 'Choose: I\'d rather you __ tell anyone about this.', options: ['don\'t', 'won\'t', 'didn\'t', 'wouldn\'t'], answer: 2 },
    { q: 'What is a synonym of "meticulous"?', options: ['careless', 'precise', 'hasty', 'vague'], answer: 1 },
    { q: 'Choose: Scarcely __ sat down when the alarm went off.', options: ['I had', 'had I', 'I have', 'have I'], answer: 1 },
    { q: 'Choose: The results are open to __.', options: ['interpret', 'interpretation', 'interpreted', 'interpreting'], answer: 1 },
    { q: 'Choose: She kept putting __ the decision.', options: ['off', 'out', 'away', 'down'], answer: 0 },
    { q: 'Choose: The project must __ by the deadline.', options: ['complete', 'be completing', 'be completed', 'have complete'], answer: 2 },
    { q: 'Choose: He is believed __ the country last week.', options: ['to leave', 'leaving', 'to have left', 'left'], answer: 2 },
    { q: 'What does "ephemeral" mean?', options: ['вечный', 'кратковременный', 'глубокий', 'срочный'], answer: 1 },
    { q: 'Choose: No sooner __ the door than the phone rang.', options: ['I opened', 'had I opened', 'I had opened', 'did I open'], answer: 1 },
    { q: 'Choose: The phenomenon __ extensively in recent decades.', options: ['studied', 'has been studied', 'is studying', 'studies'], answer: 1 },
    { q: 'Choose: Little __ about the consequences.', options: ['she cared', 'did she care', 'she did care', 'cared she'], answer: 1 },
    { q: 'Choose: The economy is on the verge __ collapse.', options: ['for', 'of', 'to', 'at'], answer: 1 },
    { q: 'Choose: __ as the situation was, they managed to cope.', options: ['Difficult', 'Difficultly', 'Difficulty', 'More difficult'], answer: 0 },
    { q: 'Choose: She can\'t help __ about the results.', options: ['worry', 'to worry', 'worried', 'worrying'], answer: 3 },
    { q: 'What is an antonym of "taciturn"?', options: ['quiet', 'reserved', 'talkative', 'thoughtful'], answer: 2 },
    { q: 'Choose: The delegation __, accompanied by journalists, arrived at noon.', options: ['who', 'which', 'that', ','], answer: 1 },
    { q: 'Choose: Had the report been submitted on time, we __ the contract.', options: ['would win', 'will have won', 'would have won', 'had won'], answer: 2 },
    { q: 'Choose: The policy __ effect from the beginning of next year.', options: ['takes', 'is taking', 'will take', 'took'], answer: 2 },
  ],
}

const questions = computed(() =>
  activeTest.value ? allTests[activeTest.value] : []
)

function startTest(key: TestKey) {
  activeTest.value = key
  currentQ.value = 0
  answers.value = new Array(allTests[key].length).fill(undefined)
  result.value = null
}

function nextQ() {
  if (currentQ.value < questions.value.length - 1) {
    currentQ.value++
  } else {
    calcResult()
  }
}

function prevQ() {
  if (currentQ.value > 0) currentQ.value--
}

function calcResult() {
  const total = questions.value.length
  const correct = answers.value.filter(
    (a, i) => a === questions.value[i].answer
  ).length
  const pct = (correct / total) * 100

  if (activeTest.value === 'grade12') {
    if (pct >= 80) result.value = { level: 'Starter / Elementary', desc: 'Отлично! У вас хорошая база. Рекомендуем группу Elementary.' }
    else result.value = { level: 'Starter', desc: 'Мы начнём с азов. Группа Starter идеально подходит для вас!' }
  } else if (activeTest.value === 'grade34') {
    if (pct >= 80) result.value = { level: 'Pre-Intermediate', desc: 'Хороший уровень! Рекомендуем группу Pre-Intermediate.' }
    else if (pct >= 50) result.value = { level: 'Elementary', desc: 'У вас есть база. Рекомендуем группу Elementary.' }
    else result.value = { level: 'Starter', desc: 'Начнём с начала. Группа Starter подходит лучше всего.' }
  } else if (activeTest.value === 'grade57') {
    if (pct >= 80) result.value = { level: 'Intermediate', desc: 'Отлично! Рекомендуем группу Intermediate.' }
    else if (pct >= 50) result.value = { level: 'Pre-Intermediate', desc: 'Хороший результат! Рекомендуем группу Pre-Intermediate.' }
    else result.value = { level: 'Elementary', desc: 'Рекомендуем группу Elementary для закрепления базы.' }
  } else if (activeTest.value === 'grade811') {
    if (pct >= 80) result.value = { level: 'Upper-Intermediate / Advanced', desc: 'Впечатляюще! Рекомендуем группу Upper-Intermediate или Advanced.' }
    else if (pct >= 50) result.value = { level: 'Intermediate', desc: 'Хороший уровень! Рекомендуем группу Intermediate.' }
    else result.value = { level: 'Pre-Intermediate', desc: 'Рекомендуем группу Pre-Intermediate.' }
  } else {
    if (pct >= 83) result.value = { level: 'Advanced (C1)', desc: 'Отличный уровень! Рекомендуем группу Advanced.' }
    else if (pct >= 65) result.value = { level: 'Upper-Intermediate (B2)', desc: 'Хороший уровень! Рекомендуем группу Upper-Intermediate.' }
    else if (pct >= 45) result.value = { level: 'Intermediate (B1)', desc: 'Хорошая база! Рекомендуем группу Intermediate.' }
    else if (pct >= 25) result.value = { level: 'Pre-Intermediate (A2)', desc: 'Хорошее начало! Рекомендуем группу Pre-Intermediate.' }
    else result.value = { level: 'Elementary (A1)', desc: 'Начнём с основ. Группа Elementary подходит идеально.' }
  }
}

function restart() {
  activeTest.value = null
  result.value = null
  currentQ.value = 0
  answers.value = []
}
</script>

<style scoped>
.testing-page {
  max-width: 780px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 12px;
}

.page-subtitle {
  font-size: 17px;
  color: var(--text-secondary);
  margin-bottom: 32px;
  line-height: 1.6;
}

.test-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.test-card {
  background: linear-gradient(135deg, var(--brand-purple), #6a5acd);
  color: #fff;
  border: none;
  border-radius: 999px;
  padding: 18px 24px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.15s, opacity 0.15s;
  text-align: center;
}
.test-card:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}
.test-card--center {
  grid-column: 1 / -1;
  max-width: 320px;
  margin: 0 auto;
  width: 100%;
}

/* Тест */
.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.test-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--brand-purple);
}
.test-progress {
  font-size: 16px;
  color: var(--brand-orange);
  font-weight: 600;
}

.question-block {
  background: #f5f4fb;
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
}
.question-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 20px;
  line-height: 1.5;
}
.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.option {
  display: flex;
  align-items: center;
  padding: 14px 18px;
  border-radius: 12px;
  background: #fff;
  border: 2px solid #e0ddf5;
  font-size: 16px;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}
.option:hover {
  border-color: var(--brand-purple);
  background: #f0eeff;
}
.option.selected {
  border-color: var(--brand-purple);
  background: #e8e4ff;
  font-weight: 600;
}

.test-nav {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.btn-back {
  padding: 12px 28px;
  border-radius: 999px;
  border: 2px solid var(--brand-purple);
  background: transparent;
  color: var(--brand-purple);
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}
.btn-back:disabled { opacity: 0.3; cursor: default; }
.btn-next {
  padding: 12px 32px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, var(--brand-purple), #6a9ad4);
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
}
.btn-next:disabled { opacity: 0.4; cursor: default; }

/* Результат */
.result-block {
  text-align: center;
  padding: 48px 24px;
}
.result-title {
  font-size: 26px;
  font-weight: 700;
  color: var(--brand-purple);
  margin-bottom: 16px;
}
.result-level {
  font-size: 40px;
  font-weight: 900;
  color: var(--brand-orange);
  margin-bottom: 16px;
}
.result-desc {
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 32px;
  line-height: 1.6;
}
.result-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}
.btn-enroll {
  padding: 14px 32px;
  border-radius: 999px;
  background: var(--brand-orange);
  color: #fff;
  text-decoration: none;
  font-size: 17px;
  font-weight: 600;
  transition: background 0.2s;
}
.btn-enroll:hover { background: var(--brand-red); }
.btn-restart {
  padding: 14px 32px;
  border-radius: 999px;
  border: 2px solid var(--brand-purple);
  background: transparent;
  color: var(--brand-purple);
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
}
</style>
