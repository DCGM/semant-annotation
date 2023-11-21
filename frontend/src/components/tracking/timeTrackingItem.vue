<template>
  <q-card class="q-mx-sm row">
    <q-input
             v-model="itemDate"
             label="Date"
             type="date"
             class="q-ma-sm" readonly />
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
  return date.toISOString().substr(11, 5)
})

const timeTo = computed(() => {
  const date = new Date(props.timeEntry.end_time)
  return date.toISOString().substr(11, 5)
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
