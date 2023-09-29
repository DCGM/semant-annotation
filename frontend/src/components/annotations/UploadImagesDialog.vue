<template>
  <q-dialog v-if="props.taskId" :modelValue="modelValue" full-height  @update:model-value="(e) => emit('update:modelValue', e)">
      <q-uploader class="full-height" name="file"
              :url="`${apiURL}/task/image/${props.taskId}`"
              multiple
              field-name="file"
              label="Upload images"
              @failed="failedUpload"
              @uploaded="successfullUpload"
              :with-credentials="true"

          />
  </q-dialog>
  </template>

<script setup lang="ts">

import { defineComponent, defineProps } from 'vue'
import { errorNotification, successNotification } from 'src/utils/notification'
import { apiURL } from 'src/boot/axios'

defineComponent({
  name: 'UploadImagesDialog'
})

const emit = defineEmits(['update:modelValue'])

function successfullUpload (e: any) {
  successNotification(`Successfully uploaded ${e.files.length > 1 ? 'files' : 'file'}.`)
}

function failedUpload (e: any) {
  for (const file of e.files) {
    const error = JSON.parse(file.xhr.response).detail
    errorNotification(`Upload failed ${file.name}. Error: ${error}`)
  }
}

interface Props {
  modelValue: boolean
  taskId: string
}

const props = defineProps<Props>()

</script>

<style scoped>

</style>
