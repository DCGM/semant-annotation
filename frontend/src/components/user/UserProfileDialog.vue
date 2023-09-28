<template>
  <q-dialog :modelValue="modelValue" @update:model-value="(e) => emit('update:modelValue', e)" @before-show="open"
    @keydown.stop="dialogKeyhandler" no-shake>
    <q-card class="q-pa-lg shadow-1" style="width: 500px; max-width: 80vw;">
      <q-card-section>
        <div class="text-h5">User profile "{{ username }}"</div>
      </q-card-section>
      <q-card-section>
        <q-form @submit="onSubmitUserForm" class="q-gutter-md">
          <q-input square filled v-model="username" label="Username" :readonly="!userStore.user?.trusted" />
          <q-input square filled v-model="fullName" label="Full name" :readonly="!userStore.user?.trusted" />
          <q-input square filled v-model="institution" label="Institution" :readonly="!userStore.user?.trusted" />
          <q-input square filled v-model="email" label="E-mail" :readonly="!userStore.user?.trusted" />
          <div v-if="userStore.user?.trusted">
            <q-checkbox v-model="trusted" label="Admin" left-label />
          </div>

          <q-btn v-if="userStore.user?.trusted" unelevated color="primary" size="lg" class="full-width"
            label="Update user information" type="submit" @click="updateUser" />
        </q-form>
      </q-card-section>
      <q-separator />
      <q-card-section>
        <q-form @submit="onSubmitPassword" class="q-gutter-md">
          <q-input square filled v-model="password" type="password" label="Password" lazy-rules
            :rules="[val => val === null || val.length === 0 || val.length >= 8 || 'Password must be at leas 8 characters long.']" />
          <q-input square filled v-model="verifyPassword" type="password" label="Verify password" lazy-rules
            :rules="[val => password === null || password.length < 8 || val === password || 'Does not match the selected password.']" />
          <q-btn label="Change Password" type="submit" unelevated color="primary" size="lg" class="full-width" />
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script setup lang="ts">
import { defineComponent, ref } from 'vue'
import { api } from 'boot/axios'
import { useErrorStore } from 'src/stores/error'
import { actionNotification } from 'src/utils/notification'
import { useUserStore } from 'src/stores/user'
import qs from 'qs'
import { Notify } from 'quasar'
import { User } from 'src/models'

const errorStore = useErrorStore()
const userStore = useUserStore()

const username = ref('')
const fullName = ref('')
const institution = ref('')
const email = ref('')
const trusted = ref(false)
const disabled = ref(false)
const password = ref(null)
const verifyPassword = ref(null)

async function onSubmitUserForm () {
  console.log('onSubmitUserForm')
}

function open () {
  username.value = props.user.username
  fullName.value = props.user.full_name
  institution.value = props.user.institution
  trusted.value = props.user.trusted > 0
  email.value = props.user.email
  password.value = null
  verifyPassword.value = null
}

async function updateUser () {
  const dismiss = actionNotification('Updating user information.')
  try {
    // Create User object and send to server
    const user: User = {
      id: props.user.id,
      username: username.value,
      full_name: fullName.value,
      institution: institution.value,
      email: email.value,
      trusted: trusted.value ? 1 : 0,
      disabled: disabled.value
    }
    console.log(user)
    await api.put('/user', user)
    await userStore.testAuthentication()
    Notify.create({
      message: 'User information successfully updated',
      type: 'positive',
      position: 'bottom-right',
      timeout: 6000
    })
    emit('user_changed')
  } catch (error) {
    errorStore.reportError('Error', 'Unable to update user information on server.', error)
  } finally {
    dismiss()
  }
}

async function onSubmitPassword () {
  const dismiss = actionNotification('Changing password.')
  try {
    console.log(qs.stringify({ password: password.value }))
    await api.put('/user/password?' + qs.stringify({ password: password.value, user_id: props.user.id }))
    Notify.create({
      message: 'User password successfully changed',
      type: 'positive',
      position: 'bottom-right',
      timeout: 6000
    })
  } catch (error) {
    errorStore.reportError('Error', 'Unable to change password on server.', error)
  } finally {
    dismiss()
    password.value = null
    verifyPassword.value = null
  }
}

defineComponent({
  name: 'UserProfileDialog'
})

interface Props {
  modelValue: boolean,
  user: User
}
const props = defineProps<Props>()

const emit = defineEmits(['update:modelValue', 'user_changed'])

function dialogKeyhandler (event) {
  if (event.key === 'Escape') {
    emit('update:modelValue', false)
  }
}

</script>
