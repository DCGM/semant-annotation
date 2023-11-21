<template>
  <q-dialog :modelValue="modelValue" @update:model-value="(e) => emit('update:modelValue', e)"
    @keydown.stop="dialogKeyhandler" no-backdrop-dismiss no-shake>
    <q-card class="q-pa-lg shadow-1" style="width: 800px; max-width: 90vw;">
      <q-card-section>
        <div class="text-h5">New annotation task</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="onSubmit">
          <q-input class="q-mt-md" square filled v-model="name" label="Task name"
            :rules="[val => !!val || 'Required.', val => val.length > 2 || 'Too short.']" />
          <!-- type can be -->
          <q-editor class="q-mt-md" v-model="description" :toolbar="editorToolbarOptions" :fonts="editorFonts" />
          <q-toggle v-model="active" label="Is active" />

          <q-btn unelevated color="primary" size="lg" class="full-width q-mt-md" label="Create task" type="submit"
            :disable="disable" />
          <q-btn flat color="negative" size="md" class="full-width q-mt-md" label="Cancel"
            @click="emit('update:modelValue', false)" :disable="disable" />
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { AnnotationTaskUpdate } from 'src/models'
import { uid, useQuasar, Loading } from 'quasar'
import { defineComponent, ref, computed, watch } from 'vue'
import { useErrorStore } from 'src/stores/error'
import { actionNotification, successNotification } from 'src/utils/notification'
import { api } from 'src/boot/axios'

const errorStore = useErrorStore()
const quasar = useQuasar()

const name = ref('')
const description = ref('')
const active = ref(false)
const disable = ref(false)


async function onSubmit () {
  disable.value = true
  Loading.show({ delay: 300 })
  try {
    const id = uid()
    const newTask: AnnotationTaskUpdate = {
      id,
      name: name.value,
      description: description.value,
      active: active.value
    }
    await api.post('/task/task', newTask)
    successNotification(`Created new annotation task: ${name.value}.`)
    emit('refreshTasks')
    emit('update:modelValue', false)
    name.value = ''
    description.value = ''
    active.value = false
  } catch (error) {
    errorStore.reportError('Error', `Failed to create document ${name.value}.`, error)
  } finally {
    disable.value = false
    Loading.hide()
  }
}

defineComponent({
  name: 'CreateAnnotationTaskDialog'
})

defineProps({
  modelValue: Boolean
})

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
