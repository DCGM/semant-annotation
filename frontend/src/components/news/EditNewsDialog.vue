<template>
  <q-dialog :modelValue="modelValue" persistent full-width @update:model-value="(e) => emit('update:modelValue', e)" @before-show="open"
    @keydown.stop="dialogKeyhandler">
    <q-card class="q-pa-lg shadow-1">
      <q-card-section>
        <div class="text-h5">Edit News</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="onSubmit">
          <q-input class="q-mt-md" filled v-model="localNews.title" label="Title"
            :rules="[(val) => (val && val.length > 0) || 'Title must be filled in.']" />
            <q-input
              label="Short"
              v-model="localNews.short"
              filled
              type="textarea"
            />
          <q-editor class="q-mt-md" v-model="localNews.content" placeholder="Description..." max-height="300px"
            :toolbar="[
              ['bold', 'italic', 'underline'],
              ['link'],
              [
                {
                  label: $q.lang.editor.fontSize,
                  icon: $q.iconSet.editor.fontSize,
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
                  label: $q.lang.editor.defaultFont,
                  icon: $q.iconSet.editor.font,
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
              ['unordered', 'ordered', 'outdent', 'indent'],
            ]" :fonts="{
  arial: 'Arial',
  arial_black: 'Arial Black',
  comic_sans: 'Comic Sans MS',
  courier_new: 'Courier New',
  impact: 'Impact',
  lucida_grande: 'Lucida Grande',
  times_new_roman: 'Times New Roman',
  verdana: 'Verdana'
}" />
        <q-card-section>
          <q-input disable v-model="localNews.released_date" label="Release date"></q-input>
          <q-btn icon="event" color="primary" label="Set release date">
            <q-popup-proxy cover transition-show="scale" transition-hide="scale">
              <div class="q-gutter-md row items-start">
                <q-date v-model="localNews.released_date" mask="YYYY-MM-DDTHH:mm" color="primary" />
                <q-time v-model="localNews.released_date" mask="YYYY-MM-DDTHH:mm" color="primary" />
              </div>
            </q-popup-proxy>
          </q-btn>

        </q-card-section>
          <q-btn v-if="localNews.id" unelevated color="secondary" size="lg" class="full-width q-mt-md" label="Save News" type="submit"
            :disable="disable" />
          <q-btn v-else unelevated color="secondary" size="lg" class="full-width q-mt-md" label="Create News" type="submit"
            :disable="disable" />

          <q-btn flat color="negative" size="md" class="full-width q-mt-md" label="Cancel"
            @click="emit('update:modelValue', false)" :disable="disable" />
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { defineComponent, ref } from 'vue'
import { uid } from 'quasar'
import { useNewsStore } from 'src/stores/news'
import { NewsUpdate } from 'src/models'

const newsStore = useNewsStore()

const localNews = ref(new NewsUpdate())
const disable = ref(false)

function open () {
  localNews.value = props.news == null ? new NewsUpdate() : { ...props.news }
}

async function onSubmit () {
  disable.value = true
  if (localNews.value.id === '') {
    localNews.value.id = uid()
    await newsStore.add(localNews.value)
  } else {
    await newsStore.update(localNews.value)
  }
  newsStore.refresh()
  emit('update:modelValue', false)
  disable.value = false
}

defineComponent({
  name: 'EditNewsDialog'
})

interface Props {
  modelValue: boolean,
  news: NewsUpdate | null
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: false,
  news: null
})

const emit = defineEmits(['update:modelValue'])

function dialogKeyhandler (event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('update:modelValue', false)
  }
}

</script>
