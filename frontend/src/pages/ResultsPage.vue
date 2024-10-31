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
        <q-tooltip v-if="!selected_task">Select task first</q-tooltip>
      </q-card-actions>
      <q-btn v-if="showTable" label="Show table" @click="showTable = false" />
      <q-btn v-else label="Show cards" @click="showTable = true" />
    </q-card>
    <div v-if="results">
      <q-card class="q-pa-md">
        <q-card-section>
          <div class="text-h6">Total results: {{ results.length }} </div>
          <div class="text-h6">Annotated: {{ annotatedCount }} </div>
          <div class="text-h6">Rejected: {{ rejectedCount }} </div>
        </q-card-section>
      </q-card>
    </div>

    <div v-if="showTable">
      <q-table v-if="results" :rows="rows" :columns="columns" row-key="id" />
    </div>
    <div v-else-if="results" class="row items-start">
      <q-card v-for="result in rows" :key="result.id" class="q-ma-sm">
        <q-card-section>
          <div>User: {{ result.user }}</div>
          <div>Created: {{ result.created_date }}</div>
          <div>Type: {{ result.result_type }}</div>
          <TaskInstace :taskInstanceId="result.annotation_task_instance_id" />
        </q-card-section>
        <q-separator inset />
        <q-card-section horizontal>
          <q-card-section
                          v-for="subtask in selected_task.subtasks"
                          :key="subtask.id">
            <div class="text-h6">{{ subtask.name }}</div>
            <div v-for="value in result[subtask.id]" :key="value">
              {{ value.text }}
            </div>
          </q-card-section>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { Loading } from 'quasar';
import { AnnotationTask, AnnotationTaskResult, User } from 'src/models';
import { api } from 'src/boot/axios';
import { useErrorStore } from 'src/stores/error';
import TaskInstace from 'src/components/annotations/TaskInstance.vue';

defineComponent({
  name: 'ResultsPage',
});

const errorStore = useErrorStore();

const tasks = ref<AnnotationTask[]>([]);
const users = ref<User[]>([]);
const results = ref<AnnotationTaskResult[]>([]);
const from_date = ref<string>('');
const to_date = ref<string>('');
const selected_task = ref<AnnotationTask | null>(null);
const selected_user = ref<User | null>(null);
const showTable = ref<boolean>(false);

const rejectedCount = computed(() => {
  if (!results.value) {
    return 0;
  }
  return results.value.filter((r) => r.result_type == 'rejected').length;
});

const annotatedCount = computed(() => {
  if (!results.value) {
    return 0;
  }
  return results.value.filter((r) => r.result_type == 'new').length;
});

let baseColumns = [
  {
    name: 'user',
    label: 'User name',
    field: 'user',
    align: 'left',
    sortable: true,
  },
  {
    name: 'result_type',
    label: 'Type',
    field: 'result_type',
    align: 'left',
    sortable: true,
  },
  {
    name: 'created_date',
    label: 'Created',
    field: 'created_date',
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
  // has to fill user from matching user_id to id in users.value
  // has to move results from results.result[] to result[subtask.id]
  if (!selected_task.value) {
    return [];
  }
  let rows = [];
  for (let result of results.value) {
    const user = users.value.find((u) => u.id == result.user_id);
    let row = {
      id: result.id,
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
  return rows;
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
  if (!selected_task.value) {
    return;
  }
  try {
    Loading.show({ delay: 300 });
    let query = { annotation_task_id: selected_task.value.id };
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
      .post('/task/results', query)
      .then((res) => res.data);
    // sort results by results[i].user_id and then results[i].end_time
    results.value.sort((a, b) => {
      if (a.user_id < b.user_id) {
        return -1;
      }
      if (a.user_id > b.user_id) {
        return 1;
      }
      if (a.end_time < b.end_time) {
        return -1;
      }
      if (a.end_time > b.end_time) {
        return 1;
      }
      return 0;
    });


  } catch (error) {
    errorStore.reportError('Error', 'Failed to get results.', error);
  } finally {
    Loading.hide();
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
