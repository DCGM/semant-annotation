<template>
  <q-dialog :modelValue="modelValue" @update:model-value="(e) => emit('update:modelValue', e)" @show="onShow"
    @keydown.stop="dialogKeyhandler" no-backdrop-dismiss no-shake>
    <q-card class="q-pa-lg shadow-1" style="width: 800px; max-width: 90vw;">
      <q-card-section>
        <div class="text-h5">New annotation task</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="onSubmit">
          <q-input class="q-mt-md" square filled v-model="localTask.name" label="Task name"
            :rules="[val => !!val || 'Required.', val => val.length > 2 || 'Too short.']" />
          <!-- type can be -->
          <q-editor class="q-mt-md" v-model="localTask.description" :toolbar="editorToolbarOptions" :fonts="editorFonts" />
          <q-toggle v-model="localTask.active" label="Is active" />

          <q-btn unelevated color="primary" size="lg" class="full-width q-mt-md" label="Update task" type="submit"
            :disable="disable" />
          <q-btn flat color="negative" size="md" class="full-width q-mt-md" label="Cancel"
            @click="emit('update:modelValue', false)" :disable="disable" />
        </q-form>
      </q-card-section>
      <!-- list all subtasks -->
      <q-card-section>
        <div class="text-h6">Subtasks</div>
        <q-list bordered separator>
          <q-item v-for="subtask in sortedSubtasks" :key="subtask.id">
            <q-item-section>
              <q-item-label>{{ subtask.name }} <span v-if="!subtask.active" class="text-primary">(INACTIVE)</span> </q-item-label>
            </q-item-section>

            <q-item-section side>
              <q-btn flat dense @click="editSubtask(subtask)" label="Edit"/>
            </q-item-section>
          </q-item>
        </q-list>
        <q-btn unelevated color="primary" size="lg" class="full-width q-mt-md" label="Add subtask" @click="newSubtask()" />
      </q-card-section>

    </q-card>
    <EditSubtaskDialog v-model="editSubtaskDialog" :subtask="selectedSubtask" @refreshSubtasks="loadSubtasks" :annotationTaskId="localTask.id" />
  </q-dialog>
</template>

<script setup lang="ts">
import { AnnotationTaskUpdate, AnnotationTask, AnnotationSubtask } from 'src/models'
import { uid, useQuasar, Loading } from 'quasar'
import { defineComponent, ref, computed, watch } from 'vue'
import { useErrorStore } from 'src/stores/error'
import { actionNotification, successNotification } from 'src/utils/notification'
import { api } from 'src/boot/axios'
import EditSubtaskDialog from './EditSubtaskDialog.vue'

const errorStore = useErrorStore()
const quasar = useQuasar()

const localTask = ref(new AnnotationTask())
const disable = ref(false)

const editSubtaskDialog = ref(false)
const selectedSubtask = ref<AnnotationSubtask | null>(null)


function editSubtask (subtask: AnnotationSubtask) {
  selectedSubtask.value = subtask
  editSubtaskDialog.value = true
}

function newSubtask () {
  selectedSubtask.value = null
  editSubtaskDialog.value = true
}

const sortedSubtasks = computed(() => {
  const subtasks = JSON.parse(JSON.stringify(localTask.value.subtasks))
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

async function loadSubtasks () {
  try {
    const dismiss = actionNotification('Reloading sub tasks.')
    const response: AnnotationTask = await api.get(`/task/task/${localTask.value.id}`).then(r => r.data)
    emit('refreshTasks')
    localTask.value.subtasks = response.subtasks
    dismiss()
  } catch (error) {
    errorStore.reportError('Error', `Failed to load subtasks for task ${localTask.value.name}.`, error)
  }
}

async function onShow () {
  if (props.task) {
    localTask.value = JSON.parse(JSON.stringify(props.task))
  } else {
    errorStore.reportError('Error', 'No task provided.', new Error('No task provided.'))
    emit('update:modelValue', false)
  }
}

async function onSubmit () {
  disable.value = true
  Loading.show({ delay: 300 })
  try {
    const taskUpdate: AnnotationTaskUpdate = {
      id: localTask.value.id,
      name: localTask.value.name,
      description: localTask.value.description,
      active: localTask.value.active
    }
    await api.put('/task/task', taskUpdate)
    successNotification(`Updated annotation task: ${localTask.value}.`)
    emit('refreshTasks')
    emit('update:modelValue', false)
    localTask.value = new AnnotationTask()
  } catch (error) {
    errorStore.reportError('Error', `Failed to update annotation task ${localTask.value.name}.`, error)
  } finally {
    disable.value = false
    Loading.hide()
  }
}

defineComponent({
  name: 'EditAnnotationTaskDialog'
})


interface Props {
  modelValue: boolean
  task: AnnotationTask | null
}

const props = defineProps<Props>()


const emit = defineEmits(['update:modelValue', 'refreshTasks'])

function dialogKeyhandler (event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('update:modelValue', false)
  }
}

const editorToolbarOptions = [
  ['bold', 'italic', 'underline'],
  ['link'],
  [
    {
      label: quasar.lang.editor.fontSize,
      icon: quasar.iconSet.editor.fontSize,
      fixedLabel: true,
      fixedIcon: true,
      list: 'no-icons',
      options: [
        'size-1',
        'size-2',
        'size-3',
        'size-4',
        'size-5',
        'size-6'
      ]
    },
    {
      label: quasar.lang.editor.defaultFont,
      icon: quasar.iconSet.editor.font,
      fixedIcon: true,
      list: 'no-icons',
      options: [
        'default_font',
        'arial',
        'arial_black',
        'comic_sans',
        'courier_new',
        'impact',
        'lucida_grande',
        'times_new_roman',
        'verdana'
      ]
    },
    'removeFormat'
  ],
  ['unordered', 'ordered', 'outdent', 'indent']
]

const editorFonts = {
  arial: 'Arial',
  arial_black: 'Arial Black',
  comic_sans: 'Comic Sans MS',
  courier_new: 'Courier New',
  impact: 'Impact',
  lucida_grande: 'Lucida Grande',
  times_new_roman: 'Times New Roman',
  verdana: 'Verdana'
}

</script>
