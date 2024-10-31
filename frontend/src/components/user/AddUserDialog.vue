<template>
  <q-dialog :modelValue="modelValue" @update:model-value="(e) => emit('update:modelValue', e)" @before-show="open"
    @keydown.stop="dialogKeyhandler" no-backdrop-dismiss no-shake>
    <q-card class="q-pa-lg shadow-1" style="min-width: 600px;">
      <q-card-section>
        <div class="text-h5">New user</div>
      </q-card-section>
      <q-form @submit="onSubmit">
        <q-card-section>
          <q-input v-model="userName" label="User name" square filled lazy-rules dense
            :rules="[val => !!val || 'Required.', val => val.length > 3 || 'Too short.', val => !val.includes(' ') || 'Cant inlude space.']" />
          <q-input v-model="fullName" label="Full name" square filled lazy-rules dense
            :rules="[val => !!val || 'Required.', val => val.length > 6 || 'Too short.']" />
          <q-input v-model="email" label="E-mail" square filled lazy-rules dense
            :rules="[val => !!val || 'Required.', val => val.length > 6 || 'Too short.']" />
          <q-input v-model="institution" label="Institution" square filled lazy-rules dense
            :rules="[val => !!val || 'Required.', val => val.length > 6 || 'Too short.']" />
          <div>
            <q-checkbox v-model="trusted" label="Admin" left-label />
          </div>
          <q-input v-model="password" label="Password" type="password" square filled lazy-rules dense
            :rules="[val => !!val || 'Required.', val => val.length > 6 || 'Too short.']" />
          <q-input v-model="verifyPassword" label="Verify password" type="password" square filled lazy-rules dense
            :rules="[val => val === password || 'Does not match the selected password.']" />
        </q-card-section>
        <q-card-actions class="q-px-md">
          <q-btn unelevated color="primary" size="lg" class="full-width q-mt-md" label="Add user" type="submit"
            :disable="disable" />
          <q-btn flat color="negative" size="md" class="full-width q-mt-md" label="Cancel"
            @click="emit('update:modelValue', false)" :disable="disable" />
        </q-card-actions>
      </q-form>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { UserWithPassword } from 'src/models'
import { uid, Loading } from 'quasar'
import { defineComponent, ref } from 'vue'
import { api } from 'boot/axios'
import { useErrorStore } from 'src/stores/error'
import { actionNotification, successNotification } from 'src/utils/notification'

const errorStore = useErrorStore()

const userName = ref('')
const fullName = ref('')
const email = ref('')
const institution = ref('')
const trusted = ref(false)
const password = ref('')
const verifyPassword = ref('')
const disable = ref(false)

function open () {
  userName.value = ''
  fullName.value = ''
  email.value = ''
  institution.value = ''
  trusted.value = false
  password.value = ''
  verifyPassword.value = ''
}

async function onSubmit () {
  console.log('SUBMIT')
  disable.value = true
  Loading.show({ delay: 300 })
  const dismiss = actionNotification(`Adding user ${userName.value}.`)
  try {
    const id = uid()
    const user: UserWithPassword = { id, username: userName.value, full_name: fullName.value, email: email.value, institution: institution.value, trusted: Number(trusted.value), password: password.value, disabled: false }
    // log message if response code is 400
    await api.post('/user/', user)

    successNotification(`Added user ${userName.value}.`)
    emit('user_changed')
    emit('update:modelValue', false)
  } catch (error) {
    console.log(error)
    errorStore.reportError('Error', error.response.data.message, '')
  } finally {
    dismiss()
    disable.value = false
    Loading.hide()
  }
}

defineComponent({
  name: 'CreateModelDialog'
})

defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'user_changed'])

function dialogKeyhandler (event) {
  if (event.key === 'Escape') {
    emit('update:modelValue', false)
  }
}

</script>
