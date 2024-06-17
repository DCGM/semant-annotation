<template>
  <q-card class="q-mx-sm row">
    <q-input v-model="selectedDate" label="Date" type="date" class="q-ma-sm" />
    <q-input v-model="timeFrom" label="From" type="time" class="q-ma-sm" />
    <q-input v-model="timeTo" label="To" type="time" class="q-ma-sm" />
    <q-select v-model="selectedProject" :options="projectOptions" label="Project" class="q-ma-sm" />
    <q-input v-model="duration" label="Duration" type="text" class="q-ma-sm" readonly />
    
    <q-btn v-if="!timerRunning" label="Start" color="primary" class="q-ma-sm" @click="startTimer" />
    <q-btn v-if="timerRunning" label="Finish" color="negative" class="q-ma-sm" @click="finish" />
    <q-btn v-if="timerRunning" label="Discard" color="primary" class="q-ma-sm" @click="stopTimer" />
    <q-btn v-if="!timerRunning" type="submit" label="Add" color="primary" class="q-ma-sm" @click="submitForm" :disable="!isValidForm" />
  </q-card>
</template>

<script setup lang="ts">
import { ref, computed, defineProps, defineEmits, onMounted, onBeforeUnmount, watch } from 'vue'
import { useTimerStore } from 'src/stores/timerStore'
import { TimeTrackingItemNew } from 'src/models'
import { uid, Notify } from 'quasar'

const timerStore = useTimerStore()

const projectOptions = ref([
  'Anotace obrázků', 'Anotace textů', 'Anotace chodců', 'Vyhledávání obrázků', 'Vyhledávání textů', 
  'Vyhledávání obličejů', 'Anotace Stránek', 'TextBite'
])

const selectedProject = computed({
  get: () => timerStore.selectedProject,
  set: value => timerStore.selectedProject = value
})

const selectedDate = computed({
  get: () => timerStore.selectedDate,
  set: value => timerStore.selectedDate = value
})

const timeFrom = computed({
  get: () => timerStore.timeFrom,
  set: value => timerStore.timeFrom = value
})

const timeTo = computed({
  get: () => timerStore.timeTo,
  set: value => timerStore.timeTo = value
})

const timerRunning = computed(() => timerStore.timerRunning)

const duration = computed(() => {
  const timeStart = new Date(`01/01/2007 ${timeFrom.value}`)
  const timeEnd = new Date(`01/01/2007 ${timeTo.value}`)
  const diff = timeEnd.getTime() - timeStart.getTime()
  return `${diff / 1000 / 60} min`
})

const isValidForm = computed(() => selectedDate.value && timeFrom.value && timeTo.value && selectedProject.value)

const props = defineProps<{ userId: string | null }>()
const emit = defineEmits(['addTimeEntry'])

function createNewTimeEntry(): TimeTrackingItemNew {
  return {
    id: uid(),
    user_id: props.userId ?? '',
    start_time: `${selectedDate.value} ${timeFrom.value}`,
    end_time: `${selectedDate.value} ${timeTo.value}`,
    task: selectedProject.value,
    description: ''
  }
}

function addNewTimeEntry(newTimeEntry: TimeTrackingItemNew) {
  emit('addTimeEntry', newTimeEntry)
}

function storeTimeEntry(newTimeEntry: TimeTrackingItemNew) {
  const storedEntries = JSON.parse(localStorage.getItem('tempTimeEntries') || '[]')
  storedEntries.push(newTimeEntry)
  localStorage.setItem('tempTimeEntries', JSON.stringify(storedEntries))
}

function retrieveAndEmitStoredTimeEntries() {
  const storedEntries = JSON.parse(localStorage.getItem('tempTimeEntries') || '[]')
  storedEntries.forEach((entry: TimeTrackingItemNew) => {
    emit('addTimeEntry', entry)
  })
  localStorage.removeItem('tempTimeEntries')
}

function saveFormState() {
  localStorage.setItem('selectedDate', selectedDate.value)
  localStorage.setItem('timeFrom', timeFrom.value)
  localStorage.setItem('timeTo', timeTo.value)
  localStorage.setItem('selectedProject', selectedProject.value)
}

function resetForm() {
  timerStore.selectedDate = new Date().toISOString().slice(0, 10)
  timerStore.timeFrom = ''
  timerStore.timeTo = ''
  timerStore.timerRunning = false
  saveFormState()
}

function showNotification() {
  timerStore.isNotificationVisible = true
  timerStore.notificationRef = Notify.create({
    message: `${selectedProject.value} (${timerStore.calculateDuration()} min)`,
    color: 'primary',
    position: 'bottom-right',
    timeout: 0,
    actions: [
      {
        label: 'Finish',
        color: 'white',
        handler: finishNotification,
        style: 'background-color: #ff0000; color: #ffffff; border: 2px solid #ff0000; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); padding: 5px 10px; border-radius: 2px;',
        class: 'q-btn'
      }
    ]
  })
}

function hideNotification() {
  if (timerStore.notificationRef) {
    timerStore.notificationRef()
    timerStore.notificationRef = null
  }
  timerStore.isNotificationVisible = false
}

function updateNotification() {
  hideNotification()
  showNotification()
}

function formatTime(date: Date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
}

function updateTimer() {
  if (timerRunning.value) {
    const newTime = new Date()
    timeTo.value = formatTime(newTime)
    saveFormState()
    if (newTime.getSeconds() === 0) {
      updateNotification()
    }
  }
}

function startTimer() {
  timerStore.startTimer(selectedProject.value)
  timerStore.intervalId = setInterval(updateTimer, 1000)
  showNotification()
}

function stopTimer() {
  if (timerStore.intervalId) {
    clearInterval(timerStore.intervalId)
    timerStore.intervalId = null
  }
  hideNotification()
  timerStore.stopTimer()
  resetForm()
}

function finish() {
  timeTo.value = formatTime(new Date())
  timerStore.stopTimer()
  clearInterval(timerStore.intervalId as unknown as number);
  timerStore.intervalId = null
  saveFormState()
  hideNotification()
  addNewTimeEntry(createNewTimeEntry())
  resetForm()
}

function finishNotification() {
  timeTo.value = formatTime(new Date())
  timerStore.stopTimer()
  clearInterval(timerStore.intervalId as unknown as number);
  timerStore.intervalId = null
  saveFormState()
  hideNotification()
  storeTimeEntry(createNewTimeEntry())
  resetForm()
}

function submitForm() {
  if (!isValidForm.value) return
  addNewTimeEntry(createNewTimeEntry())
  hideNotification()
  resetForm()
}

onMounted(() => {
  selectedDate.value = localStorage.getItem('selectedDate') || ''
  timeFrom.value = localStorage.getItem('timeFrom') || ''
  timeTo.value = localStorage.getItem('timeTo') || ''
  selectedProject.value = localStorage.getItem('selectedProject') || projectOptions.value[0]
  if (timerRunning.value) {
    timerStore.intervalId = setInterval(updateTimer, 1000)
    hideNotification()
    showNotification()
  }

  retrieveAndEmitStoredTimeEntries()
})

onBeforeUnmount(() => {
  retrieveAndEmitStoredTimeEntries()
  if (timerStore.intervalId) {
    clearInterval(timerStore.intervalId)
    timerStore.intervalId = null
  }
})

watch(timerRunning, newVal => {
  if (!newVal && timerStore.intervalId) {
    clearInterval(timerStore.intervalId)
    timerStore.intervalId = null
  }
})
</script>