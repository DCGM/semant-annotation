<template>
  <q-card class="q-pa-md" style="max-width: 350px; width: 100%;">
    <q-card-section>
      <q-expansion-item
                        v-model="expanded"
                        :label="subtask.name"
                        :expand-separator="true"
                        :default-open="true"
                        expand-icon="info">
        <!-- show descriptin -->
        Description: <span v-html="subtask.description" />
      </q-expansion-item>
    </q-card-section>
    <q-card-section>
      <!-- addResponseChange tracks changes (content and timestamp)-->
      <q-input v-for="(item, index) in textResponses" :key="index"
               dense
               v-model="item.text" @update:model-value="update(item, $event)" />
      <q-btn label="Add more" @click="textResponses.push({ history: [], timestamp: new Date().toISOString(), text: '' })"
             icon="add"
             class="full-width" />
    </q-card-section>
  </q-card>
</template>


<script setup lang="ts">

import { defineComponent, defineProps, ref, onMounted, defineEmits, watch, defineExpose } from 'vue'
import { AnnotationSubtask, TextResponses, TextResponse, AnnotationTaskResult } from 'src/models'

const initialTextReponseCount = 10
const expanded = ref(false)

const textResponses = ref<TextResponses>([])

const emit = defineEmits(['responseUpdate'])

watch(textResponses, (newValue) => {
  emit('responseUpdate', newValue)
})

function update (item: TextResponse, event: any) {
  item.history.push({ timestamp: new Date().toISOString(), text: event })
  item.timestamp = new Date().toISOString()
  item.text = event
}

interface Props {
  subtask: AnnotationSubtask,
  instanceResults: AnnotationTaskResult
}

const props = defineProps<Props>()

defineComponent({
  name: 'SubtaskResponse'
})

const subtask = props.subtask
const instanceResults = props.instanceResults

onMounted(async () => {
  // initialize results as an empty array of TextResponse
  const results: TextResponse[] = []

  // load results based on result for task instance for each subtask
  const subResults = JSON.parse(instanceResults.result)
  for (const [key, value] of Object.entries(subResults)) {
    
    // store only current subtask
    if (key === subtask.id) {
      if (Array.isArray(value)) {
        value.forEach((item) => {
          if (typeof item === 'object' && item !== null) {
            results.push({
              history: Array.isArray(item.history) ? item.history : [],
              timestamp: item.timestamp || new Date().toISOString(),
              text: item.text || ''
            })
          }
        })
      }
      break
    }
  }

  // show annotation results for each subtask
  textResponses.value = []
  for (let i = 0; i < initialTextReponseCount; i++) {
    textResponses.value.push({
      history: results[i]?.history || [],
      timestamp: results[i]?.timestamp || new Date().toISOString(),
      text: results[i]?.text || ''
    })
  }
})


</script>
