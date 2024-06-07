<template>
  <q-page padding>
    <q-card class="q-pa-md">
      <q-card-section>
        <q-select
          v-model="selected_task"
          :options="tasks"
          label="Task"
          clearable
          option-label="name"
          :display-value="`${selected_task ? selected_task.name : 'All'}`"
        />
        <q-select
          v-model="selected_user"
          :options="users"
          label="User"
          option-label="username"
          :display-value="`${selected_user ? selected_user.username : 'All'}`"
          clearable
        />
        <q-select
          v-model="selected_result"
          :options="resulttypeUpper"
          label="Results"
          option-label="types"
          :display-value="selected_result ? toUpper(selected_result) : 'All'"
          clearable
        />
        <q-input v-model="from_date" label="From date" type="date" clearable />
        <q-input v-model="to_date" label="To date" type="date" clearable />
      </q-card-section>
    </q-card>
    <!-- TABLE -->
 <q-table
      class="my-sticky-header-column-table"
      :rows="rows"
      :columns="columns"
      row-key="id"
      :rows-per-page-options="[users.length]"
    >
      <template v-if="!selected_task" v-slot:header="props">
        <q-tr :props="props">
          <q-th/>
          <q-th v-for="(column, index) in additionalHeaders" :key="index" :colspan="3">
            {{ column }}
          </q-th>
        </q-tr>
        <q-tr :props="props">
          <q-th :props="props" v-for="column in props.cols" :key="column.name">
            {{ column.label }}
          </q-th>
        </q-tr>
      </template>
    </q-table>
  </q-page>
</template>

<script setup lang="ts">
// imports 
import { ref, onMounted, computed , watchEffect} from 'vue';
import { Loading } from 'quasar';
import { AnnotationTask, SimplifiedAnnotationTaskResult, User, AnnotationResultType } from 'src/models';
import { api } from 'src/boot/axios';
import { useErrorStore } from 'src/stores/error';


// variables that store responses by server etc
const errorStore = useErrorStore();
const tasks = ref<AnnotationTask[]>([]);
const users = ref<User[]>([]);
const results = ref<SimplifiedAnnotationTaskResult[]>([]);
const resulttype = ref<AnnotationResultType[]>([]);

const from_date = ref<string>('');
const to_date = ref<string>('');

const selected_task = ref<AnnotationTask | null>(null);
const selected_result = ref<AnnotationResultType | null>(null);
const selected_user = ref<User | null>(null);
const resulttypeUpper = ref<string[]>([]);

function toUpper(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}


const additionalHeaders = computed(() => {
  if (selected_task.value) {
    return [selected_task.value.name];
  } else {
    return tasks.value.map(task => task.name);
  }
});

// column for users
const baseColumns = [
  {
    name: 'user',
    label: 'User name',
    field: 'user',
    align: 'left',
  },
];

// columns generation based on selected task (when task selected, it only shows one in the table)
const columns = computed(() => {
  const taskColumns = selected_task.value
    ? generateTaskColumns(selected_task.value)
    : tasks.value.flatMap(task => generateTaskColumns(task));

  return [...baseColumns, ...taskColumns];
});

// column values, TIME, COUNT, LINES
function generateTaskColumns(task) {
  return [{
      name: `task_${task.id}_time`,
      label: `Time`,
      field: `task_${task.id}_time`,
      align: 'center',
    },
    {
      name: `task_${task.id}_count`,
      label: `Count`,
      field: `task_${task.id}_count`,
      align: 'center',
    },
    {
      name: `task_${task.id}_lines`,
      label: `Lines`,
      field: `task_${task.id}_lines`,
      align: 'center',
    }
  ];
}

// inside of the table, each cell value
const rows = computed(() => {
  // variable that holds all the data between users and tasks
  const userTaskDataMap: Record<number, Record<number, { time: number, count: number, lines: number }>> = {};
  // variable that holds all of the information
  const taskTotals: Record<number, { time: number, count: number, lines: number }> = {};

  results.value.forEach(result => {
    // init array for insertion of user, the very first instance of user
    if (!userTaskDataMap[result.user_id]) {
      userTaskDataMap[result.user_id] = {};
    }

    // compute time inverval
    const startTime = new Date(result.start_time);
    const endTime = new Date(result.end_time);
    const timeSpent = (endTime.getTime() - startTime.getTime()) / (1000 * 60 * 60);

    // init array insertion of task, the very first instance of user and task
    if (!userTaskDataMap[result.user_id][result.annotation_task_id]) {
      userTaskDataMap[result.user_id][result.annotation_task_id] = { time: 0, count: 0, lines: 0 };
    }

    // add time and count of annotated results
    userTaskDataMap[result.user_id][result.annotation_task_id].time += timeSpent;
    userTaskDataMap[result.user_id][result.annotation_task_id].count += 1;
    //userTaskDataMap[result.user_id][result.annotation_task_id].lines += 1;

    // do the same process for every user for each task, (accumulated value for tasks)
    if (!taskTotals[result.annotation_task_id]) {
      taskTotals[result.annotation_task_id] = { time: 0, count: 0, lines: 0 };
    }
    taskTotals[result.annotation_task_id].time += timeSpent;
    taskTotals[result.annotation_task_id].count += 1;
    //taskTotals[result.annotation_task_id].lines += 1;
  });

  let userRows;
  
  // is user is selected filter it
  if (selected_user.value) {
    userRows = users.value.filter(user => user.id == selected_user.value.id).map(user => {
      // selected task
      if (selected_task.value){
        return oneTask(user, selected_task.value, userTaskDataMap);
      } else {
        // iteration over all tasks
        return allTasks(user, userTaskDataMap);
      }
    });
  } else {
    // if user is not selected, iterate over all users
      userRows = users.value.map(user => {
        // selected task
        if (selected_task.value) {
          return oneTask(user, selected_task.value, userTaskDataMap);
        } else {
          // iteration over all tasks
          return allTasks(user, userTaskDataMap);
        }
    });
  }

  if(selected_user.value){
    return userRows;
  }else{
    // generate row for task totals
    const totalRow: any = {
      user: 'All',
      user_id: -1,
    };
    tasks.value.forEach(task => {
      let hours = Math.floor(taskTotals[task.id]?.time || 0)
      let minuts = Math.floor((taskTotals[task.id]?.time - Math.floor(taskTotals[task.id]?.time)) * 60 || 0)
      totalRow[`task_${task.id}_time`] = `${hours}h ${minuts}m`;
      totalRow[`task_${task.id}_count`] = taskTotals[task.id]?.count || 0;
      totalRow[`task_${task.id}_lines`] = taskTotals[task.id]?.lines || 0;
    });
  
    return [totalRow,...userRows];
  }
});

// function that exectures computing for all tasks
function allTasks(user, userTaskDataMap) {
  const row: any = {
    user: user.username,
    user_id: user.id,
  };
  tasks.value.forEach(task => {
    const taskData = userTaskDataMap[user.id]?.[task.id] || { time: 0, count: 0, lines: 0 };
    const hours = Math.floor(taskData.time || 0);
    const minutes = Math.floor((taskData.time - hours) * 60 || 0);
    row[`task_${task.id}_time`] = `${hours}h ${minutes}m`;
    row[`task_${task.id}_count`] = taskData.count;
    row[`task_${task.id}_lines`] = taskData.lines;
  });
  return row;
}

// function that computes only selected task
function oneTask(user, task, userTaskDataMap) {
  const row: any = {
    user: user.username,
    user_id: user.id,
  };
  const taskData = userTaskDataMap[user.id]?.[task.id] || { time: 0, count: 0, lines: 0 };
  const hours = Math.floor(taskData.time || 0);
  const minutes = Math.floor((taskData.time - hours) * 60 || 0);
  row[`task_${task.id}_time`] = `${hours}h ${minutes}m`;
  row[`task_${task.id}_count`] = taskData.count;
  row[`task_${task.id}_lines`] = taskData.lines;
  return row;
}



// original functions

// on load
onMounted(async () => {
  await loadTasks();
  await loadUsers();
  await loadResTypes();
  // watcher who will call loadresults whenever something is selected
  watchEffect(() => {
    loadResults();
  });
});

// loading tasks
async function loadTasks() {
  try {
    Loading.show({ delay: 300 });
    tasks.value = await api.get('/task/task').then(res => res.data);
  } catch (error) {
    errorStore.reportError('Error', 'Failed to get tasks.', error);
  } finally {
    Loading.hide();
  }
}

// loading users
async function loadUsers() {
  try {
    Loading.show({ delay: 300 });
    users.value = await api.get('/user/').then(res => res.data);
  } catch (error) {
    errorStore.reportError('Error', 'Failed to get users.', error);
  } finally {
    Loading.hide();
  }
}

// loading result types
async function loadResTypes() {
  try {
    Loading.show({ delay: 300 });
    resulttype.value = await api.get('/task/types').then(res => res.data);
    resulttypeUpper.value = resulttype.value.map(type => toUpper(type));
  } catch (error) {
    errorStore.reportError('Error', 'Failed to get result types.', error);
  } finally {
    Loading.hide();
  }
}

// loading results
async function loadResults() {
  try {
    Loading.show({ delay: 300 });
    const query: any = {};
    if (selected_task.value) {
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
    if (selected_result.value) {
      query['result_type'] = selected_result.value.toLowerCase();
    }

    results.value = await api.post('/task/result_times', query).then(res => res.data);
  } catch (error) {
    errorStore.reportError('Error', 'Failed to get results.', error);
  } finally {
    Loading.hide();
  }
}

</script>
