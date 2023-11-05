<template>
  <q-layout view="hHh LpR fFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar class="GNL__toolbar">
        <q-btn flat dense round @click="toggleLeftDrawer" aria-label="Menu" icon="menu" class="q-mr-sm" />

        <q-toolbar-title shrink class="row items-center no-wrap">
          <router-link to="/" style="text-decoration: none; color: inherit;">
            <span class="q-ml-sm">semAnt annotation</span>
          </router-link>
        </q-toolbar-title>
        <q-space />
        <UserIcon />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered class="bg-white" :width="200">
      <q-scroll-area class="fit">
        <q-list padding class="text-grey-8">

          <router-link to="/news/" style="text-decoration: none; color: inherit;">
            <q-item class="drawer-item" :class="{ 'drawer-item-selected': currentRoute.startsWith('/news') }" v-ripple
                    clickable>
              <q-item-section avatar>
                <q-icon name="fa-solid fa-newspaper" />
              </q-item-section>
              <q-item-section>
                <q-item-label>News</q-item-label>
              </q-item-section>
            </q-item>
          </router-link>

          <router-link v-if="userStore.user" to="/annotation_tasks/" style="text-decoration: none; color: inherit;">
            <q-item class="drawer-item" :class="{ 'drawer-item-selected': currentRoute.startsWith('/annotation_tasks') }"
                    v-ripple clickable>
              <q-item-section avatar>
                <q-icon name="fa-solid fa-book-open-reader" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Annotation tasks</q-item-label>
              </q-item-section>
            </q-item>
          </router-link>

          <router-link v-if="userStore.user" to="/annotation_results/" style="text-decoration: none; color: inherit;">
            <q-item class="drawer-item"
                    :class="{ 'drawer-item-selected': currentRoute.startsWith('/annotation_results') }"
                    v-ripple clickable>
              <q-item-section avatar>
                <q-icon name="fa-solid fa-book" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Annotation results</q-item-label>
              </q-item-section>
            </q-item>
          </router-link>

          <!-- Time tracking -->
          <router-link v-if="userStore.user" to="/time_tracking/" style="text-decoration: none; color: inherit;">
            <q-item class="drawer-item" :class="{ 'drawer-item-selected': currentRoute.startsWith('/time_tracking') }"
                    v-ripple clickable>
              <q-item-section avatar>
                <q-icon name="fa-solid fa-clock" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Time tracking</q-item-label>
              </q-item-section>
            </q-item>
          </router-link>


          <router-link v-if="userStore.user" to="/annotation_statistics/" style="text-decoration: none; color: inherit;">
            <q-item class="drawer-item"
                    :class="{ 'drawer-item-selected': currentRoute.startsWith('/annotation_statistics') }"
                    v-ripple clickable>
              <q-item-section avatar>
                <q-icon name="fa-solid fa-book" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Annotation statistics</q-item-label>
              </q-item-section>
            </q-item>
          </router-link>

          <router-link v-if="userStore.user && userStore.user.trusted" to="/users/"
                       style="text-decoration: none; color: inherit;">
            <q-item class="drawer-item" :class="{ 'drawer-item-selected': currentRoute.startsWith('/users') }" v-ripple
                    clickable>
              <q-item-section avatar>
                <q-icon name="supervisor_account" />
              </q-item-section>
              <q-item-section>
                <q-item-label> User management </q-item-label>
              </q-item-section>
            </q-item>
          </router-link>

          <q-item v-if="!userStore.user" class="drawer-item" v-ripple clickable @click="logInDialog = true">
            <q-item-section avatar>
              <q-icon name="fa-solid fa-user" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Sign in</q-item-label>
            </q-item-section>
          </q-item>

          <q-item v-if="!userStore.user" class="drawer-item" v-ripple clickable @click="logInDialog = true">
            <q-item-section avatar>
              <q-icon name="fa-solid fa-user-plus" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Register new user</q-item-label>
            </q-item-section>
          </q-item>

          <q-separator inset class="q-my-sm" />

          <div class="q-mt-md">
            <div class="flex flex-center q-gutter-xs">
              <a class="drawer-footer-link" aria-label="Privacy">Privacy</a>
              <span> · </span>
              <a class="drawer-footer-link" aria-label="Terms">Terms</a>
              <span> · </span>
              <a class="drawer-footer-link" aria-label="About">About PERO</a>
            </div>
          </div>
        </q-list>
      </q-scroll-area>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
  <LoginDialog v-model="logInDialog" />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import LoginDialog from 'src/components/user/LoginDialog.vue'
import { useUserStore } from 'src/stores/user'
import UserIcon from 'src/components/toolbar/UserIcon.vue'

const route = useRoute()
const userStore = useUserStore()

const logInDialog = ref(false)
const leftDrawerOpen = ref(true)

const currentRoute = computed(() => {
  return route.path ? route.path : ''
})

function toggleLeftDrawer () {
  leftDrawerOpen.value = !leftDrawerOpen.value
}

</script>

<style scoped>
.GNL__toolbar {
  height: 64px;
}

.GNL__toolbar__toolbar-input {
  width: 55%;
}

.drawer-item {
  line-height: 24px;
  border-radius: 0 24px 24px 0;
  margin-right: 12px;
}

.drawer-item-selected {
  background: #d1e2e9;
}

.q-icon {
  color: #333638;
}

.q-item__label {
  color: #2e3133;
  letter-spacing: .01785714em;
  font-size: .875rem;
  font-weight: 500;
  line-height: 1.25rem;
}

.drawer-footer-link {
  color: inherit;
  text-decoration: none;
  font-weight: 500;
  font-size: .75rem;
}

/*&:hover
     color: #000*/
</style>
