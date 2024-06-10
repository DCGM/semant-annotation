<template>
  <q-card class="q-mx-sm row">
    <q-input
             v-model="itemDate"
             label="Date"
             type="date"
             class="q-ma-sm" readonly />
    <q-input
      v-model="timeFrom"
      mask="time"
      :rules="['time']"
      class="q-ma-sm"
      label="From"
      readonly
    >
      <template v-slot:append>
        <q-icon name="access_time" class="cursor-pointer">
          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
            <q-time
              v-model="timeFrom"
              format24h
              readonly
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
      readonly
    >
      <template v-slot:append>
        <q-icon name="access_time" class="cursor-pointer">
          <q-popup-proxy cover transition-show="scale" transition-hide="scale">
            <q-time
              v-model="timeTo"
              format24h
              readonly
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
             type="time" class="q-ma-sm" readonly />
    <q-input
             v-model="timeTo"
             label="To"
             type="time" class="q-ma-sm" readonly />
    <q-input
             v-model="task"
             label="Project" class="q-ma-sm" readonly />
             -->

    <!-- Read only field showing computed duration -->
    <q-input
             v-model="duration"
             label="Duration"
             type="text" class="q-ma-sm" readonly />

    <q-btn
           label="Delete"
           color="negative"
           class="q-ma-sm" @click="emit('delete', props.timeEntry.id)" />
  </q-card>
</template>

<script setup lang="ts">
import { defineComponent, defineEmits, computed } from 'vue'
import { TimeTrackingItem } from 'src/models'

defineComponent({
  name: 'TimeTrackingItem',
})

const emit = defineEmits(['delete'])

interface Props {
  timeEntry: TimeTrackingItem
}

const props = defineProps<Props>()

const itemDate = computed(() => {
  const date = new Date(props.timeEntry.start_time)
  return date.toISOString().substr(0, 10)
})

const timeFrom = computed(() => {
  const date = new Date(props.timeEntry.start_time)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
})


const timeTo = computed(() => {
  const date = new Date(props.timeEntry.end_time)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })
})

const duration = computed(() => {
  const start = new Date(props.timeEntry.start_time)
  const end = new Date(props.timeEntry.end_time)
  const diff = end.getTime() - start.getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor((diff / (1000 * 60)) % 60)
  return `${hours}h ${minutes}m`
})

const task = computed(() => {
  return props.timeEntry.task
})

</script>
