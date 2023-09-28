<template>
  <q-dialog :modelValue="modelValue" @update:model-value="(e) => emit('update:modelValue', e)" @keydown.stop="dialogKeyhandler">
      <q-card class="q-pa-lg shadow-1 justify-center items-center" style="width: 500px; max-width: 80vw;">
        <q-card-section>
            <div class="text-h5">Sign in</div>
        </q-card-section>
        <q-card-section>
          <q-form class="q-gutter-md">
              <q-input square filled v-model="userName" @keydown.enter.prevent="login" label="User name" />
              <q-input square filled v-model="password" @keydown.enter.prevent="login" type="password" label="Password" />
          </q-form>
          </q-card-section>
          <q-card-actions class="q-px-md">
              <q-btn unelevated color="primary" size="lg" class="full-width" label="Login" @click="login"/>
          </q-card-actions>
      </q-card>
    </q-dialog>
</template>

<script setup lang="ts">
import qs from 'qs'
import { defineComponent, ref } from 'vue'
import { Loading } from 'quasar'
import { successNotification } from 'src/utils/notification'
import { api } from 'boot/axios'
import { useUserStore } from 'src/stores/user'
import { useErrorStore } from 'src/stores/error'
const errorStore = useErrorStore()
const userStore = useUserStore()

defineComponent({
  name: 'LoginDialog'
})

defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue'])

function dialogKeyhandler (event: KeyboardEvent) {
  if (event.key === 'Escape') {
    emit('update:modelValue', false)
  }
}

const userName = ref(null)
const password = ref(null)

async function login () {
  Loading.show({ delay: 300 })
  try {
    await api.post('/token', qs.stringify({ username: userName.value, password: password.value }),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
    await userStore.setAuthorized()
    successNotification(`Logged in as user ${userName.value}`)
    emit('update:modelValue', false)
  } catch (error) {
    password.value = null
    errorStore.reportError('Error', `Failed login as user ${userName.value}.`, error)
  } finally {
    console.log('HIDE.')
    Loading.hide()
  }
}

</script>
