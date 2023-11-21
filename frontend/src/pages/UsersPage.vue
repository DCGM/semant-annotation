<template>
  <q-page v-if="userStore.user && userStore.user.trusted" padding style="padding: 0; padding-top: 52px;margin: 0;">
    <q-page-sticky expand position="top" style="z-index: 100;">
      <q-toolbar class="bg-white shadow-1">
        <q-toolbar-title>
          Users
        </q-toolbar-title>
        <q-btn color="primary" label="Add user" @click="addUserDialog = true" />
      </q-toolbar>
    </q-page-sticky>
    <div class="q-pa-md">
      <q-table :columns="columns" :rows="users" row-key="id">
        <template v-slot:body-cell-actions="props">
          <q-td :props="props">
            <q-btn dense flat round icon="edit" @click="edit(props.row)">
              <q-tooltip :delay="1000">edit user</q-tooltip>
            </q-btn>
            <!-- Disable user -->
            <q-btn dense flat round icon="delete" @click="disableUser(props.row)">
              <q-tooltip :delay="1000">disable user</q-tooltip>
            </q-btn>
            <!-- User statistics -->
            <q-btn dense flat round icon="bar_chart" @click="showStatistics(props.row)">
              <q-tooltip :delay="1000">show statistics</q-tooltip>
            </q-btn>
          </q-td>
        </template>
      </q-table>
    </div>
    <AddUserDialog v-model="addUserDialog" @user_changed="loadUsers" />
    <UserProfileDialog v-if="selectedUser" v-model="userProfileDialog" :user="selectedUser" @user_changed="loadUsers" />
  </q-page>
</template>

<script setup lang="ts">
import { ref, onBeforeMount, computed } from 'vue'
import { QTable, QTableProps } from 'quasar'
import { useUserStore } from 'src/stores/user'
import AddUserDialog from 'src/components/user/AddUserDialog.vue'
import UserProfileDialog from 'src/components/user/UserProfileDialog.vue'
import { api } from 'src/boot/axios'
import { actionNotification, successNotification } from 'src/utils/notification'
import { User } from 'src/models'
import { useErrorStore } from 'src/stores/error'

const userStore = useUserStore()
const addUserDialog = ref(false)
const userProfileDialog = ref(false)
const users = ref([])
const selectedUser = ref<User | null>(null)
const errorStore = useErrorStore()

function edit (user: User) {
  selectedUser.value = user
  userProfileDialog.value = true
}

const columns: QTableProps['columns'] = [
  { name: 'username', label: 'User Name', field: 'username', align: 'left' },
  { name: 'email', label: 'Email', field: 'email', align: 'left' },
  { name: 'full_name', label: 'Full name', field: 'full_name', align: 'left' },
  { name: 'institution', label: 'Institution', field: 'institution', align: 'left' },
  { name: 'trusted', label: 'Admin', field: 'trusted', align: 'left' },
  { name: 'disabled', label: 'Disabled', field: 'disabled', align: 'left' },
  {
    name: 'actions',
    required: true,
    label: 'Actions',
    align: 'left',
    field: row => row.id,
    format: val => `${val}`,
    sortable: true
  }
]


function disableUser () {
  errorStore.reportError('NOT IMPLEMENTED YET', 'Disabling users is not implemented yet.', '')
}

function showStatistics () {
  errorStore.reportError('NOT IMPLEMENTED YET', 'Showing statistics is not implemented yet.', '')
}


async function loadUsers () {
  const dismiss = actionNotification('Loading users.')
  const retirevedUsers = await api.get('/user')
  dismiss()
  successNotification('Loaded users.')
  users.value = retirevedUsers.data
}

onBeforeMount(loadUsers)

</script>
