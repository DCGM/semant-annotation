<template>
  <q-page class="flex flex-center">
    <form>
      <q-card class="q-pa-md" style="max-width: 500px;">
        <q-card-section>
          <q-select v-model="selected_task" :options="tasks" label="Task" />
          <q-select v-model="selected_user" :options="users" label="User" />
          <q-input v-model="from_date" label="From date" type="date" />
          <q-input v-model="to_date" label="To date" type="date" />
        </q-card-section>
        <q-card-actions>
          <q-btn label="Load results" color="primary" @click="loadResults" />
        </q-card-actions>
      </q-card>
    </form>
  </q-page>
</template>

<script setup lang="ts">
import { defineComponent,  ref, onMounted, computed } from 'vue'
import { uid, Loading } from 'quasar'
import { AnnotationTask, AnnotationSubtask, AnnotationTaskInstance, AnnotationTaskResult, User } from 'src/models'
import { api, apiURL } from 'src/boot/axios'
import { actionNotification, successNotification } from 'src/utils/notification'
import { useErrorStore } from 'src/stores/error'

defineComponent({
  name: 'ResultsPage'
})

var tasks = ref<AnnotationTask[]>([])
var users = ref<User[]>([])
var results = ref<AnnotationTaskResult[]>([])
var from_date = ref<string>('')
var to_date = ref<string>('')
var selected_task = ref<AnnotationTask | null>(null)
var selected_user = ref<User | null>(null)


onMounted(async () => {
  console.log('SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
  results.value = null
  await loadTasks()
  await loadUsers()
  console.log(tasks.value)
  console.log(users.value)
})

async function loadTasks() {
  try {
    tasks.value = await api.get('/task/task/')
  } catch (error) {
    errorStore.addError(error)
  }
}

async function loadUsers() {
  try {
    users.value = await api.get('/user/')
  } catch (error) {
    errorStore.addError(error)
  }
}

async function loadResults(){
  try {
    const results = await api.get(f`/task/results/${selected_task.value.id}/${selected_user.value.id}/${from_date.value}/${to_date.value}`)
    results.value = results
  } catch (error) {
    errorStore.addError(error)
  }
}
/*    <q-table
      v-if="results"
      :data="results"
      :columns="columns"
      row-key="id"
      :loading="loading"
      :rows-per-page-options="[10, 20, 50]"
      :pagination="pagination"
      :filter="filter"
      :selected-rows-label="getSelectedString"
      selection="multiple"
      @filter="updateFilter"
      @request="updateRequest"
      @selection="updateSelection"
    />
*/




</script>
