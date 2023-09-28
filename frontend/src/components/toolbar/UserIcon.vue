<template>
  <div class="q-gutter-sm row items-center no-wrap">
    <q-btn round dense flat color="grey-8" icon="notifications">
      <!--q-badge color="red" text-color="white" floating>
       2
       </q-badge-->
      <q-tooltip>Notifications</q-tooltip>
    </q-btn>
    <q-btn round flat>
      <q-avatar size="28px">
        <img src="https://cdn.quasar.dev/img/boy-avatar.png">
      </q-avatar>
      <q-menu auto-close>
        <q-list dense>
          <q-item v-if="userStore.user" class="GL__menu-link-signed-in">
            <q-item-section>
              <div>Signed in as <strong>{{ userStore.user?.username }}</strong></div>
            </q-item-section>
          </q-item>
          <q-item v-else class="GL__menu-link-signed-in">
            <strong>You are not signed in.</strong>
          </q-item>
          <q-separator />

          <q-item v-if="!userStore.user" clickable class="GL__menu-link-signed-in">
            <q-item-section @click="logInDialog = true">
              Log in
            </q-item-section>
          </q-item>
          <q-item v-if="!userStore.user" clickable class="GL__menu-link-signed-in">
            <q-item-section @click="logInDialog = true">
              Register
            </q-item-section>
          </q-item>

          <q-item v-if="userStore.user" clickable class="GL__menu-link" @click="userProfileDialog = true">
            <q-item-section>Your profile</q-item-section>
          </q-item>
          <q-separator />
          <q-item clickable class="GL__menu-link">
            <q-item-section>Help</q-item-section>
          </q-item>
          <q-item clickable class="GL__menu-link">
            <q-item-section>Settings</q-item-section>
          </q-item>
          <q-item v-if="userStore.user" clickable class="GL__menu-link" @click="signOut">
            <q-item-section>Sign out</q-item-section>
          </q-item>
        </q-list>
      </q-menu>
    </q-btn>
  </div>
  <UserProfileDialog v-model="userProfileDialog" :user="userStore.user" />
  <LoginDialog v-model="logInDialog" />
</template>

<script setup>
import { ref } from 'vue'
import UserProfileDialog from 'src/components/user/UserProfileDialog.vue'
import LoginDialog from 'src/components/user/LoginDialog.vue'
import { useUserStore } from 'src/stores/user'
import { useRouter } from 'vue-router'

const router = useRouter()

const userStore = useUserStore()
const userProfileDialog = ref(false)
const logInDialog = ref(false)

async function signOut () {
  userStore.signOut()
  router.push('/login/')
}

</script>
