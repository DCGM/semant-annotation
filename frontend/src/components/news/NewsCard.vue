<!-- eslint-disable vue/no-v-text-v-html-on-component -->
<template>
  <q-card class="q-ma-md" style="z-index: 11;">
    <q-card-section>
      <div class="text-h6">{{ news.title }}</div>
    </q-card-section>
    <q-card-section v-html="news.short" />
    <q-card-actions>
      <q-btn v-if="news.content" flat color="primary" label="Read more" />
      <q-btn v-if="userStore.user && userStore.user.trusted" flat color="secondary" label="Edit"
        @click="editDialog = true" />
    </q-card-actions>
    <EditNewsDialog v-if="userStore.user && userStore.user.trusted" v-model="editDialog" :news="news" />
  </q-card>
</template>

<script setup lang="ts">
import { defineComponent, ref } from 'vue'
import { News } from 'src/models'
import EditNewsDialog from 'src/components/news/EditNewsDialog.vue'
import { useUserStore } from 'src/stores/user'

const userStore = useUserStore()
const editDialog = ref(false)

defineComponent({
  name: 'NewsCard'
})

interface Props {
  news: News
}

defineProps<Props>()

</script>

<style lang="sass" scoped>
.my-card
  width: 100%
  max-width: 300px
</style>
