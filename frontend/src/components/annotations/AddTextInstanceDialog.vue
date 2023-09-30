<template>
  <q-dialog :modelValue="modelValue" @update:model-value="(e) => emit('update:modelValue', e)" @show="onShow"
    @keydown.stop="dialogKeyhandler" no-backdrop-dismiss no-shake>
    <q-card class="q-pa-lg shadow-1" style="width: 800px; max-width: 90vw;">
      <q-card-section>
        <div class="text-h5">Add annotation task instance</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="onSubmit">
          <div class="text-h6">Task</div>
          <q-editor class="q-mt-md" v-model="text" :toolbar="editorToolbarOptions" :fonts="editorFonts" />
          <div class="text-h6 q-mt-md">Metadata</div>
          <q-input class="q-mt-md" square filled v-model="metadata" label="Metadata" type="textarea" />


          <q-btn unelevated color="primary" size="lg" class="full-width q-mt-md" label="ADD" type="submit"
            :disable="disable" />
          <q-btn flat color="negative" size="md" class="full-width q-mt-md" label="Close"
            @click="emit('update:modelValue', false)" :disable="disable" />
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { AnnotationTaskInstanceUpdate, AnnotationTask } from 'src/models'
import { uid, useQuasar, Loading } from 'quasar'
import { defineComponent, ref} from 'vue'
import { useErrorStore } from 'src/stores/error'
import { successNotification } from 'src/utils/notification'
import { api } from 'src/boot/axios'

const errorStore = useErrorStore()
const quasar = useQuasar()

const text = ref('')
const metadata = ref('')
const disable = ref(false)

async function onShow () {
  text.value = ''
}

async function onSubmit () {
  disable.value = true
  Loading.show({ delay: 300 })
  try {
    const taskUpdate: AnnotationTaskInstanceUpdate = {
      id: uid(),
      annotation_task_id: props.task.id,
      image: '',
      text: text.value,
      instance_metadata: metadata.value,
      active: true
    }
    text.value = ''
    await api.post('/task/task_instance', taskUpdate)
    successNotification('Created annotation task instance.')
  } catch (error) {
    errorStore.reportError('Error', 'Failed to add task instance.', error)
  } finally {
    disable.value = false
    Loading.hide()
  }
}

defineComponent({
  name: 'AddTextInstanceDialog',
})


interface Props {
  modelValue: boolean
  task: AnnotationTask
}

const props = defineProps<Props>()

const emit = defineEmits(['update:modelValue'])

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
