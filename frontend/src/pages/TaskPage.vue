<template>
  <q-page v-if="userStore.user" padding style="padding: 0; padding-top: 52px;margin: 0;">
    <q-page-sticky expand position="top" style="z-index: 100;">
      <q-toolbar class="bg-white shadow-1">
        <q-toolbar-title>
          Annotation tasks
        </q-toolbar-title>
        <q-btn v-if="userStore.user && userStore.user.trusted" color="primary" label="Add task" @click="addTaskDialog = true" />
      </q-toolbar>
    </q-page-sticky>
    <div class="row q-gutter-md q-mt-md q-px-md">
      <q-card class="q-pa-md" v-for="task in tasksToShow" :key="task.id" style="max-width: 600px; width: 100%;">
        <q-card-section  >
          <div class="text-h6">
            {{ task.name }}
            <span v-if="userStore.user && userStore.user.trusted && !task.active" class="text-primary">(INACTIVE)</span>
          </div>
          <div class="text-subtitle2">
            <span v-for="subtask in task.subtasks" :key="subtask.id">
              <span v-if="subtask.active" class="q-pr-md">
                {{ subtask.name }}
              </span>
            </span>
          </div>
        </q-card-section>
        <q-card-section>
          <q-scroll-area style="height: 200px; ">
            <div class="text-subtitle2" :innerHTML="task.description" />
          </q-scroll-area>
        </q-card-section>

        <q-separator />

        <q-card-actions align="right">
          <q-btn flat label="Annotate" color="primary" @click="annotate(task)" />
          <q-btn flat label="Info" color="primary" @click="taskInfoDialog = true; selectedTask = task" />
          <q-btn v-if="userStore.user && userStore.user.trusted"
            flat label="Upload images" color="secondary" @click="uploadImages(task)" />
          <q-btn v-if="userStore.user && userStore.user.trusted"
            flat label="Edit" color="secondary" @click="edit(task)" />
          <q-btn v-if="userStore.user && userStore.user.trusted"
            flat label="Delete" color="negative" @click="openDeleteDialog(task)" />
        </q-card-actions>
      </q-card>
    </div>
    <CreateAnnotationTaskDialog v-model="addTaskDialog" @refreshTasks="loadTasks" />
    <EditAnnotationTaskDialog v-model="editTaskDialog" :task="selectedTask" @refreshTasks="loadTasks" />
    <UploadImagesDialog v-if="selectedTask" v-model="uploadImagesDialog" :taskId="selectedTask.id" />
    <TaskInfo v-if="selectedTask" v-model="taskInfoDialog" :task="selectedTask" />
    <!-- Simple delete dialog -->
    <q-dialog v-model="deleteDialog">
      <q-card class="q-pa-md">
        <q-card-section>
          <div class="text-h6">Delete task "{{ selectedTask?.name }}"</div>
          <div class="text-subtitle2">Are you sure you want to delete this task?</div>
        </q-card-section>
        <q-separator />
        <q-card-actions align="right" class="q-mt-sm">
          <q-btn label="Cancel action" color="primary" v-model="deleteDialog" />
          <q-btn v-if="selectedTask" label="Confirm Delete" color="negative" @click="deleteTask(selectedTask)" />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onBeforeMount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from 'src/stores/user'
import { api } from 'src/boot/axios'
import { actionNotification, successNotification } from 'src/utils/notification'
import { AnnotationTask } from 'src/models'
import CreateAnnotationTaskDialog from 'src/components/annotations/CreateAnnotationTaskDialog.vue'
import EditAnnotationTaskDialog from 'src/components/annotations/EditAnnotationTaskDialog.vue'
import UploadImagesDialog from 'src/components/annotations/UploadImagesDialog.vue'
import TaskInfo from 'src/components/annotations/TaskInfo.vue'
import { useErrorStore } from 'src/stores/error'

const errorStore = useErrorStore()
const router = useRouter()

const userStore = useUserStore()
const addTaskDialog = ref(false)
const editTaskDialog = ref(false)
const uploadImagesDialog = ref(false)
const taskInfoDialog = ref(false)
const deleteDialog = ref(false)
const annotationTasks = ref(Array<AnnotationTask>())
const selectedTask = ref<AnnotationTask | null>(null)

function uploadImages (task: AnnotationTask) {
  selectedTask.value = task
  uploadImagesDialog.value = true
}

function edit (task: AnnotationTask) {
  selectedTask.value = task
  editTaskDialog.value = true
}

function openDeleteDialog (task: AnnotationTask) {
  selectedTask.value = task
  deleteDialog.value = true
}

function annotate(task: AnnotationTask) {
  router.push('/annotation_tasks/' + task.id)
}

async function deleteTask(task: AnnotationTask) {
  deleteDialog.value = false
  const dismiss = actionNotification('Deleting task ' + task.name)
  try{
    await api.delete('/task/task/' + task.id)
    successNotification('Deleted task ' + task.name)
    loadTasks()
  } catch (error) {
    errorStore.reportError('Error', 'Failed to delete task ' + task.name, error)
  } finally{
    dismiss()
  }
}

const tasksToShow = computed(() => {
  if (userStore.user && userStore.user.trusted) {
    return annotationTasks.value
  } else {
    return annotationTasks.value.filter(task => task.active)
  }
})


async function loadTasks () {
  const dismiss = actionNotification('Loading tasks.')
  try{
    annotationTasks.value = await api.get('/task/task').then(response => response.data)
    successNotification('Loaded tasks.')
  } catch (error) {
    errorStore.reportError('Error', 'Failed to load tasks.', error)
  } finally{
    dismiss()
  }
}

onBeforeMount(loadTasks)

</script>
