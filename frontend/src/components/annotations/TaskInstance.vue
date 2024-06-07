<template>
  <q-card-section v-if="taskInstance?.image" class="row q-mt-md">
    <q-img
      :src="`${apiURL}/task/image/${taskInstance?.annotation_task_id}/${taskInstance?.id}`"
      style="max-width: 400px; max-height: 300px"
      loading="lazy"
      fit="contain"
    />
  </q-card-section>
  <q-card-section
    v-if="taskInstance?.text"
    class="row q-mt-md q-px-md"
    style="max-width: 400px"
  >
    <div :innerHTML="taskInstance?.text" />
  </q-card-section>
</template>

<script setup lang="ts">
import { ref, onBeforeMount, defineProps } from 'vue';
import { Loading } from 'quasar';
import { AnnotationTaskInstance } from 'src/models';
import { api, apiURL } from 'src/boot/axios';
import { useErrorStore } from 'src/stores/error';

interface Props {
  taskInstanceId: string;
}

const props = defineProps<Props>();
const errorStore = useErrorStore();
const taskInstance = ref<AnnotationTaskInstance | null>(null);


onBeforeMount(async () => {
  try {
    Loading.show();
    taskInstance.value = await api
      .get(`/task/task_instance/${props.taskInstanceId}/`)
      .then((response) => response.data);
  } catch (error) {
    errorStore.reportError(
      'Error',
      'Failed to load annotation task instance',
      error
    );
  } finally {
    Loading.hide();
  }
});
</script>
