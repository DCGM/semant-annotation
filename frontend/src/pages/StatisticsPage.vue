<template>
  <q-page padding>
    <q-card class="q-pa-md">
      <q-card-section>
        <q-select
                  v-model="selected_task"
                  :options="tasks"
                  label="Task"
                  clearable
                  option-label="name" />
        <q-select
                  v-model="selected_user"
                  :options="users"
                  label="User"
                  option-label="username"
                  clearable />
        <q-input v-model="from_date" label="From date" type="date" clearable />
        <q-input v-model="to_date" label="To date" type="date" clearable />
      </q-card-section>
      <q-card-actions>
        <q-btn
               label="Load results"
               color="primary"
               @click="loadResults"
               :disable="!selected_task" />
      </q-card-actions>
    </q-card>

    <!--q-table v-if="results" :rows="rows" :columns="columns" row-key="id" /-->
    {{ rows }}
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { Loading } from 'quasar';
import { AnnotationTask, SimplifiedAnnotationTaskResult, User } from 'src/models';
import { api } from 'src/boot/axios';
import { useErrorStore } from 'src/stores/error';


const errorStore = useErrorStore();

const tasks = ref<AnnotationTask[]>([]);
const users = ref<User[]>([]);
const results = ref<SimplifiedAnnotationTaskResult[]>([]);
const from_date = ref<string>('');
const to_date = ref<string>('');
const selected_task = ref<AnnotationTask | null>(null);
const selected_user = ref<User | null>(null);

let baseColumns = [
  {
    name: 'user',
    label: 'User name',
    field: 'user',
    align: 'left',
    sortable: true,
  },
];

const columns = computed(() => {
  if (!selected_task.value) {
    return [];
  }
  let columns = [...baseColumns];
  let subtasks = selected_task.value.subtasks;
  for (let subtask of subtasks) {
    columns.push({
      name: subtask.name,
      label: subtask.name,
      field: subtask.id,
      align: 'left',
      sortable: false,
    });
  }
  return columns;
});

const rows = computed(() => {
  return []
  if (!results.value) {
    return [];
  }

  // copy results and sort them by start_time
  let sortedResults = [...results.value];
  sortedResults.sort((a, b) => {
    return a.start_time.localeCompare(b.start_time);
  });

  const start_date: Date = new Date(sortedResults[0].start_time);
  const end_date: Date = new Date(sortedResults[sortedResults.length - 1].end_time);


  // create Array mapping all days between start and end date to a number - this will be used to count the number of results per day
  let currentDate = start_date;
  let resultsPerDay = new Map();
  while (currentDate <= end_date) {
    resultsPerDay.set(currentDate.toISOString().slice(0, 10), 0);
    currentDate.setDate(currentDate.getDate() + 1);
  }

  // count the number of results per day
  for (let result of sortedResults) {
    let date = new Date(result.start_time).toISOString().slice(0, 10);
    resultsPerDay.set(date, resultsPerDay.get(date) + 1);
  }

  return Array.from(resultsPerDay).map(([key, value]) => {
    return {
      date: key,
      count: value
    }
  });








  /*

    let rows = [];
    for (let result of results.value) {
      const user = users.value.find((u) => u.id == result.user_id);

      let row = {
        user: user?.username || 'unknown',
        annotation_task_instance_id: result.annotation_task_instance_id,
        result_type: result.result_type,
        created_date: result.created_date,
      };

      const subResults = JSON.parse(result.result);
      for (const [key, value] of Object.entries(subResults)) {
        // value is a list of string, needs to be joined
        row[key] = value;
      }
      rows.push(row);
    }
    console.log(rows);
    return rows;*/
});

onMounted(async () => {
  console.log('SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS');
  results.value = [];
  await loadTasks();
  await loadUsers();
  console.log(tasks.value);
  console.log(users.value);
});

async function loadTasks () {
  try {
    Loading.show({ delay: 300 });
    tasks.value = await api.get('/task/task').then((res) => res.data);
  } catch (error) {
    errorStore.reportError('Error', 'Failed to get tasks.', error);
  } finally {
    Loading.hide();
  }
}

async function loadUsers () {
  try {
    Loading.show({ delay: 300 });
    users.value = await api.get('/user').then((res) => res.data);
  } catch (error) {
    errorStore.reportError('Error', 'Failed to get users.', error);
  } finally {
    Loading.hide();
  }
}

async function loadResults () {
  try {
    Loading.show({ delay: 300 });
    let query: any = {}
    if (!selected_task.value) {
      query['annotation_task_id'] = selected_task.value.id;
    }
    if (selected_user.value) {
      query['user_id'] = selected_user.value.id;
    }
    if (from_date.value) {
      query['from_date'] = from_date.value;
    }
    if (to_date.value) {
      query['to_date'] = to_date.value;
    }

    results.value = await api
      .post('/task/result_times', query)
      .then((res) => res.data);
    console.log(results.value);
  } catch (error) {
    errorStore.reportError('Error', 'Failed to get results.', error);
  } finally {
    Loading.hide();
  }
}
</script>
