<template>
  <!--
      The page has single horizontal component for time input. It has a date input, a time from input, a time to input, and a project select.
      It can be submitted with the ADD button or by pressing enter or user can start timer by pressing the START button and stop it by pressing the STOP button.
      The input is show as a single horizontal line at the top of the page.
      Afterwards, it lists all the time entries.

    -->
  <q-page class="column" padding>
    <TimeTrackerLine @addTimeEntry="addTimeEntry" :userId="userId ? userId : userStore.user?.id" />

    <div class="row q-pa-md items-start " style="z-index: 10;">
      <TimeTrackingItem v-for="item in timeEntries" :key="item.id" :timeEntry="item" class="q-ma-sm"
                        @delete="deleteTimeEntry" />
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import TimeTrackerLine from 'src/components/tracking/timeTrackerLine.vue'
import TimeTrackingItem from 'src/components/tracking/timeTrackingItem.vue'
import { TimeTrackingItemNew } from 'src/models'
import { api } from 'src/boot/axios'
import { useErrorStore } from 'src/stores/error'
import { Loading } from 'quasar';
import { useUserStore } from 'src/stores/user'

const userStore = useUserStore()
const errorStore = useErrorStore()

const userId = ref<string | null>(null)

const timeEntries = ref(Array<TimeTrackingItemNew>())

onMounted(() => {
  loadTimeEntries()
})

async function loadTimeEntries () {
  Loading.show({ delay: 300 });
  await api.get('/time_tracking/time_tracking').then((response) => {
    timeEntries.value = response.data
  }).catch((error) => {
    errorStore.reportError('Error', 'Failed to load time entries.', error)
  }).finally(() => {
    Loading.hide()
  })
}

async function addTimeEntry (newTimeEntry: TimeTrackingItemNew) {
  Loading.show({ delay: 300 });
  try {
    await api.post('/time_tracking/time_tracking', newTimeEntry)
    // Add the new time entry to the list of time entries  at the beginning.
    timeEntries.value = [newTimeEntry, ...timeEntries.value]
  } catch (error) {
    errorStore.reportError('Error', 'Failed to add time entry.', error)
  } finally {
    Loading.hide()
  }
}

async function deleteTimeEntry (id: string) {
  Loading.show({ delay: 300 });
  try {
    await api.delete('/time_tracking/time_tracking/' + id)
    // Remove the time entry from the list of time entries
    timeEntries.value = timeEntries.value.filter((item) => item.id !== id)
  } catch (error) {
    errorStore.reportError('Error', 'Failed to delete time entry.', error)
  } finally {
    Loading.hide()
  }
}





</script>
