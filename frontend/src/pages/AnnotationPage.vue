<template>
<q-page padding style="padding: 0; padding-top: 52px;margin: 0;" >
    <q-page-sticky expand position="top" style="z-index: 100;">
      <q-toolbar class="bg-white shadow-1">
        <q-toolbar-title>
          <!-- BACK icon filled dark -->
          <q-btn round dense icon="arrow_back" color="primary" @click="$router.back()" />
          <!-- Task name -->
          <span class="text-h6 q-ml-md">
          {{ annotationTask?.name }}
          </span>
        </q-toolbar-title>
        <q-btn flat label="Task Info" color="primary" @click="taskInfoDialog = true" />
        <q-btn color="primary q-ml-md" label="DONE" @click="submitResponse" />
      </q-toolbar>
    </q-page-sticky>
    <div class="row q-gutter-md q-mt-md q-px-md">
      <div>
      <img v-if="taskInstance?.image && taskInstance?.annotation_task_id"
          :src="`${apiURL}/task/image/${taskInstance?.annotation_task_id}/${taskInstance?.id}`"
          style=" height: 200px"/>
      </div>
      <!-- Subtqasks -->
      <q-card v-for="subtask in relevantSubtasks" :key="subtask.id" class="q-pa-md" style="max-width: 400px; width: 100%;">
        <q-card-section>
          <div class="text-h6">
            {{ subtask.name }}
          </div>
        </q-card-section>
        <q-separator />
        <q-card-section>
          <q-input v-for="(response, index) in textResponses[subtask.id]" :key="index" v-model="textResponses[subtask.id][index]" dense />
        </q-card-section>
      </q-card>
    </div>
    <TaskInfo v-if="annotationTask" v-model="taskInfoDialog" :task="annotationTask" />
</q-page>
</template>


<script setup lang="ts">

import { defineComponent, defineProps, ref, onMounted, onBeforeMount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { uid, Loading } from 'quasar'
import { AnnotationTask, AnnotationSubtask, AnnotationTaskInstance, AnnotationTaskResult, AnnotationTaskResultUpdate } from 'src/models'
import { useUserStore } from 'src/stores/user'
import { api, apiURL } from 'src/boot/axios'
import { actionNotification, successNotification } from 'src/utils/notification'
import { useErrorStore } from 'src/stores/error'
import TaskInfo from 'src/components/annotations/TaskInfo.vue'


const errorStore = useErrorStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const taskInfoDialog = ref(false)


const textReponseCount = 10

const annotationTask = ref<AnnotationTask | null>(null)
const taskInstance = ref<AnnotationTaskInstance | null>(null)

const textResponses = ref({})

defineComponent({
  name: 'AnnotationPage'
})

onBeforeMount(async () => {
  await loadAnnotationTask()
  await getNextAnnotationTaskInstance()
})

const relevantSubtasks = computed(() => {
  if (annotationTask.value === null) {
    return []
  }
  var subtasks: AnnotationSubtask[] = annotationTask.value.subtasks
  subtasks = subtasks.filter((s: AnnotationSubtask) => s.active)
  subtasks.sort((a: AnnotationSubtask, b: AnnotationSubtask) => {
    if (a.created_date < b.created_date) {
      return -1
    } else if (a.created_date > b.created_date) {
      return 1
    } else {
      return 0
    }
  })
  return subtasks
})

async function submitResponse(){
  if( taskInstance.value === null) {
    return
  }
  if( userStore.user === null) {
    return
  }

  Loading.show({ delay: 300 })
  try{
    const resultData: AnnotationTaskResultUpdate = {
      id: uid(),
      user_id: userStore.user.id,
      annotation_task_instance_id: taskInstance.value.id,
      result: JSON.stringify(textResponses.value),
      result_type: 'new'
    }
    await api.post('/task/task_instance_result', resultData)
    await getNextAnnotationTaskInstance()
  } catch (error) {
    errorStore.reportError('Error', 'Failed to submit annotation task result', error)
    router.push('/annotation_tasks')
  } finally {
    Loading.hide()
  }
}


async function loadAnnotationTask() {
  annotationTask.value  = null
  // should overlay the whole page with loading indicator until this is done
  Loading.show({ delay: 300 })
  try {
    annotationTask.value = await api.get(`/task/task/${route.params.task_id}`).then(response => response.data)
  } catch (error) {
    errorStore.reportError('Error', 'Failed to load annotation task', error)
    router.push('/annotation_tasks')
  } finally {
    Loading.hide()
  }
}

async function getNextAnnotationTaskInstance() {
  if (annotationTask.value === null) {
    return
  }
  taskInstance.value = null
  Loading.show({ delay: 300 })
  try{
    // /api/task/task_instance_random/:task_id/:result_count
    taskInstance.value = await api.get(`/task/task_instance_random/${route.params.task_id}/0/-1`).then(response => response.data)
    for(const subtask of annotationTask.value.subtasks) {
      if(subtask.active) {
        textResponses.value[subtask.id] = []
        for(let i = 0; i < textReponseCount; i++) {
          textResponses.value[subtask.id].push('')
        }
      }
    }

  }
  catch (error) {
    errorStore.reportError('Error', 'Failed to load annotation task instance', error)
    router.push('/annotation_tasks')
  } finally {
    Loading.hide()
  }
}

</script>
