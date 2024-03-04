<template>
  <q-card class="q-mx-sm row">
    <q-input
             v-model="selectedDate"
             label="Date"
             type="date"
             class="q-ma-sm" :readonly="timerRunning" />
    <q-input
      v-model="timeFrom"
      mask="time"
      :rules="['time']"
      class="q-ma-sm"
      label="From"
    >
      <template v-slot:append>
        <q-icon name="access_time" class="cursor-pointer">
          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
            <q-time
              v-model="timeFrom"
              format24h
            >
              <div class="row items-center justify-end">
                <q-btn v-close-popup label="Close" color="primary" flat />
              </div>
            </q-time>
          </q-popup-proxy>
        </q-icon>
      </template>
    </q-input>
    <q-input
      v-model="timeTo"
      mask="time"
      :rules="['time']"
      class="q-ma-sm"
      label="To"
    >
      <template v-slot:append>
        <q-icon name="access_time" class="cursor-pointer">
          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
            <q-time
              v-model="timeTo"
              format24h
            >
              <div class="row items-center justify-end">
                <q-btn v-close-popup label="Close" color="primary" flat />
              </div>
            </q-time>
          </q-popup-proxy>
        </q-icon>
      </template>
    </q-input>
    <!--
    <q-input
             v-model="timeFrom"
             label="From"
             type="time" class="q-ma-sm"
             :readonly="timerRunning"
             :format24h="true"
    />
    <q-input
             v-model="timeTo"
             label="To"
             type="time" class="q-ma-sm" :readonly="timerRunning"
             min="00:00" max="23:59" pattern="[0-2][0-9]:[0-5][0-9]"
    />
    -->
    <q-select
              v-model="selectedProject"
              :options="projectOptions"
              label="Project" class="q-ma-sm" />

    <!-- Read only field showing computed duration -->
    <q-input
             v-model="duration"
             label="Duration"
             type="text" class="q-ma-sm" readonly />

    <q-btn v-if="!timerRunning"
           label="Start" color="primary" class="q-ma-sm"
           @click="startTimer" />
    <q-btn v-if="timerRunning"
           label="STOP"
           color="negative"
           class="q-ma-sm" @click="cancelTimer" />
    <q-btn
           type="submit"
           label="Add"
           color="primary"
           class="q-ma-sm" @click="submitForm" :disable="!selectedDate || !timeFrom || !timeTo || !selectedProject" />
  </q-card>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, defineComponent, defineEmits } from 'vue'
import { TimeTrackingItemNew } from 'src/models'
import { uid } from 'quasar'

defineComponent({
  name: 'TimeTrackerLine'
})

interface Props {
  userId: string | null
}

const props = defineProps<Props>()

const emit = defineEmits(['addTimeEntry'])

const projectOptions = ref(['Anotace obrázků', 'Anotace textů', 'Anotace chodců', 'Vyhledávání obrázků', 'Vyhledávání textů', 'Vyhledávání obličejů', 'Anotace Stránek', 'TextBite'])
const selectedDate = ref('')
const timeFrom = ref('')
const timeTo = ref('')
const selectedProject = ref(projectOptions.value[0].value)
const timerRunning = ref(false)
let intervalId: any = null

function submitForm () {
  timerRunning.value = false
  clearInterval(intervalId)
  intervalId = null

  if (!selectedDate.value || !timeFrom.value || !timeTo.value || !selectedProject.value || !props.userId) {
    return
  }
  const newTimeEntry: TimeTrackingItemNew = {
    id: uid(),
    user_id: props.userId,
    start_time: selectedDate.value + ' ' + timeFrom.value,
    end_time: selectedDate.value + ' ' + timeTo.value,
    task: selectedProject.value,
    description: ''
  }

  emit('addTimeEntry', newTimeEntry)
  console.log(newTimeEntry)
  reset()
}

function reset () {
  selectedDate.value = new Date().toISOString().slice(0, 10)
  timeFrom.value = new Date().toISOString().slice(11, 16)
  timeTo.value = ''
  timerRunning.value = false
  clearInterval(intervalId)
  intervalId = null
}

// Periodicaly update timer when timerRunnning is True
function startTimer () {
  selectedDate.value = new Date().toISOString().slice(0, 10)
  timeFrom.value = new Date().toISOString().slice(11, 16)
  timeTo.value = new Date().toISOString().slice(11, 16)
  timerRunning.value = true
  intervalId = setInterval(() => {
    if (timerRunning.value) {
      timeTo.value = new Date().toISOString().slice(11, 16)
    }
  }, 1000)
}

function cancelTimer () {
  timerRunning.value = false
  clearInterval(intervalId)
  intervalId = null
}

onMounted(() => {
  // init with today's date (only date without time)
  selectedDate.value = new Date().toISOString().slice(0, 10)
  selectedProject.value = projectOptions.value[0]
})

const duration = computed(() => {
  var timeStart = new Date('01/01/2007 ' + timeFrom.value)
  var timeEnd = new Date('01/01/2007 ' + timeTo.value)
  var diff = timeEnd - timeStart;
  return diff / 1000 / 60 + ' min';
})


</script>
