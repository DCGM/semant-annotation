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
    <div class="q-pa-md">
      <q-card class="q-pa-md" v-for="task in annotationTasks" :key="task.id">
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
          <div class="text-subtitle2" :innerHTML="task.description">
          </div>
        </q-card-section>

        <q-separator dark />

        <q-card-actions align="right">
          <q-btn flat label="Annotate" color="primary" @click="annotate(task)" />
          <q-btn v-if="userStore.user && userStore.user.trusted"
            flat label="Edit" color="primary" @click="edit(task)" />
        </q-card-actions>
      </q-card>
    </div>
    <CreateAnnotationTaskDialog v-model="addTaskDialog" @refreshTasks="loadTasks" />
    <EditAnnotationTaskDialog v-model="editTaskDialog" :task="selectedTask" @refreshTasks="loadTasks" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onBeforeMount, computed } from 'vue'
import { useUserStore } from 'src/stores/user'
import { api } from 'src/boot/axios'
import { actionNotification, successNotification } from 'src/utils/notification'
import { AnnotationTask } from 'src/models'
import CreateAnnotationTaskDialog from 'src/components/annotations/CreateAnnotationTaskDialog.vue'
import EditAnnotationTaskDialog from 'src/components/annotations/EditAnnotationTaskDialog.vue'
import { useErrorStore } from 'src/stores/error'

const errorStore = useErrorStore()

const userStore = useUserStore()
const addTaskDialog = ref(false)
const editTaskDialog = ref(false)
const annotationTasks = ref(Array<AnnotationTask>())
const selectedTask = ref<AnnotationTask | null>(null)


function edit (task: AnnotationTask) {
  selectedTask.value = task
  editTaskDialog.value = true
}

function annotate(task: AnnotationTask) {
  console.log('ANNOTATE ', task)
}



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
