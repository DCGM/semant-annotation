<template>
  <q-card class="q-pa-md" style="max-width: 350px; width: 100%;">
    <q-card-section>
      <q-expansion-item
                        v-model="expanded"
                        :label="subtask.name"
                        :caption="subtask.description"
                        :expand-separator="true"
                        :default-open="true"
                        expand-icon="info">
        <!-- show descriptin -->
        Description: {{ subtask.description }}
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
import { AnnotationSubtask, TextResponses, TextResponse } from 'src/models'

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
  subtask: AnnotationSubtask
}

const props = defineProps<Props>()

defineComponent({
  name: 'SubtaskResponse'
})

onMounted(async () => {
  textResponses.value = []
  for (let i = 0; i < initialTextReponseCount; i++) {
    textResponses.value.push({ history: [], timestamp: new Date().toISOString(), text: '' })
  }
})

function clear () {
  textResponses.value = []
  for (let i = 0; i < initialTextReponseCount; i++) {
    textResponses.value.push({ history: [], timestamp: new Date().toISOString(), text: '' })
  }
}

defineExpose({
  clear
})

</script>
