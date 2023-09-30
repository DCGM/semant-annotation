<template>
  <q-dialog :modelValue="modelValue" @update:model-value="(e) => emit('update:modelValue', e)" @keydown.stop="dialogKeyhandler" no-shake>
    <q-card v-if="props.task" class="q-pa-lg shadow-1" style="width: 800px; max-width: 90vw;">
      <q-card-section>
        <div class="text-h5">Annotation task {{ props.task?.name }}</div>
      </q-card-section>

      <q-card-section>
        <!-- Description -->
        <div class="text-h6">Description</div>
        <div class="q-mt-md" v-html="props.task?.description"></div>
      </q-card-section>
      <!-- List all active subtasks as expansion items with description -->
      <q-card-section>
        <div class="text-h6">Subtasks</div>
        <q-list bordered class="rounded-borders">
          <q-expansion-item v-for="subtask in sortedSubtasks" :key="subtask.id" :label="subtask.name" expand-separator>
              <div class="q-pa-md" v-html="subtask.description" />
          </q-expansion-item>
        </q-list>
        <q-btn unelevated color="primary" size="lg" class="full-width q-mt-md" label="Close" @click="emit('update:modelValue', false)" />
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { AnnotationTask, AnnotationSubtask } from 'src/models'
import { defineComponent, computed} from 'vue'
import { useUserStore } from 'src/stores/user'

const userStore = useUserStore()



const sortedSubtasks = computed(() => {
  if( props.task === null) {
    return []
  }
  var subtasks = JSON.parse(JSON.stringify(props.task.subtasks))
  if( userStore.user && !userStore.user.trusted) {
    subtasks = subtasks.filter((subtask: AnnotationSubtask) => {
      return subtask.active
    })
  }
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
</script>
