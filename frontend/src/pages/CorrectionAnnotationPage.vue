<template>
  <q-page padding style="padding: 0; padding-top: 52px;margin: 0;">
    <q-page-sticky expand position="top" style="z-index: 100;">
      <q-toolbar class="bg-white shadow-1">
        <q-toolbar-title>
          <!-- BACK icon filled dark -->
          <q-btn round dense icon="arrow_back" color="primary" @click="$router.back()" />
          <!-- Task name -->
          <span class="text-h6 q-ml-md">
            {{ annotationTask?.name }}
          </span>
          <q-btn color="primary q-ml-md" label="DONE" @click="submitResponse('correction')" />

        </q-toolbar-title>
        <q-btn flat label="Task Info" color="primary" @click="taskInfoDialog = true" />
        <q-btn color="negative q-ml-md" label="REJECT" @click="submitResponse('rejected')" />
      </q-toolbar>
    </q-page-sticky>

    <div v-if="taskInstance?.image" class="row q-mt-md">
      <q-card style="max-width: 600px; width: 100%;">
        <q-card-section>
          <div class="text-h6">
            Image
          </div>
        </q-card-section>
        <q-card-section>
          <img :src="`${apiURL}/task/image/${taskInstance?.annotation_task_id}/${taskInstance?.id}`"
               style="height: 300px" />
        </q-card-section>
      </q-card>
    </div>
    <div v-if="taskInstance?.text" class="row q-mt-md q-px-md">
      <q-card style="max-width: 600px; width: 100%;">
        <q-card-section>
          <div class="text-h6">
            Text
          </div>
        </q-card-section>
        <q-card-section>
          <div :innerHTML="taskInstance?.text" />
        </q-card-section>
      </q-card>
    </div>
    <div v-if="instanceResults" class="row q-gutter-md q-mt-md q-px-md" >
      <!-- Subtqasks -->
      <CorrectionSubtaskResponse  v-for="subtask in relevantSubtasks" :key="subtask.id" :subtask="subtask" :instanceResults="instanceResults"
                       @responseUpdate="subtaskResponseUpdate(subtask.id, $event)" ref="subtaskResponsesRefs" />
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
import SubtaskResponse from 'src/components/annotations/SubtaskResponse.vue'
import { TextResponse, SubtaskResponses } from 'src/models'
import CorrectionSubtaskResponse from 'src/components/annotations/CorrectionSubtaskResponse.vue'

const errorStore = useErrorStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const taskInfoDialog = ref(false)

const textReponseCount = 10

const annotationTask = ref<AnnotationTask | null>(null)
const taskInstance = ref<AnnotationTaskInstance | null>(null)
const instanceResults = ref<AnnotationTaskResult | null>(null)

const subtaskResponsesRefs = ref<SubtaskResponses[]>([])

let startTime = new Date().toISOString()

const getResultTypeStyle = (resultType: 'rejected' | 'new' | 'correction') => {
  const styles = {
    rejected: { color: 'red', 'font-weight': 'bold' },
    new: { color: 'green', 'font-weight': 'bold' },
    correction: { color: 'yellow', 'font-weight': 'bold' },
  };
  return styles[resultType] || {};
};

const subtaskResponses = ref<SubtaskResponses>({})

defineComponent({
  name: 'AnnotationPage'
})

onBeforeMount(async () => {
  await loadAnnotationTask()
  await getNextAnnotationTaskInstance()
})


function subtaskResponseUpdate (subtaskId: string, newValue: TextResponse[]) {
  subtaskResponses.value[subtaskId] = newValue
}

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

async function submitResponse (resultType = 'correction') {
  if (taskInstance.value === null) {
    return
  }
  if (userStore.user === null) {
    return
  }

  Loading.show({ delay: 300 })
  try {
    const resultData: AnnotationTaskResultUpdate = {
      id: uid(),
      user_id: userStore.user.id,
      annotation_task_instance_id: taskInstance.value.id,
      result: JSON.stringify(subtaskResponses.value),
      start_time: startTime.slice(0, -1),
      end_time: new Date().toISOString().slice(0, -1),
      result_type: resultType
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


async function loadAnnotationTask () {
  annotationTask.value = null
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

async function getNextAnnotationTaskInstance () {
  if (annotationTask.value === null) {
    return
  }
  taskInstance.value = null
  instanceResults.value = null
  
  Loading.show({ delay: 300 })
  try {
    // /api/task/task_instance_random/:task_id/:result_count
    taskInstance.value = await api.get(`/task/task_instance_random/${route.params.task_id}/1/-1`).then(response => response.data)
    instanceResults.value = await api.get(`/task/task_instance_annot_random/${taskInstance.value?.id}`).then(response => response.data)
    
    startTime = new Date().toISOString()
    
  } catch (error) {
    errorStore.reportError('Error', 'Failed to load annotation task instance', error)
    router.push('/annotation_tasks')
  } finally {
    Loading.hide()
  }
}

</script>
