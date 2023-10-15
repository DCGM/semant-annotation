<!-- eslint-disable vue/no-v-text-v-html-on-component -->
<template>
  <q-page padding style="padding: 0; padding-top: 52px; margin: 0">
    <q-page-sticky expand position="top" style="z-index: 100">
      <q-toolbar class="bg-white shadow-1">
        <q-toolbar-title> News </q-toolbar-title>
        <q-btn
          v-if="userStore.user && userStore.user.trusted"
          color="primary"
          label="Add News"
          @click="addDialog = true"
        />
      </q-toolbar>
    </q-page-sticky>
    <AudioRecorder></AudioRecorder>

    <div class="row q-pa-md items-start" style="z-index: 10">
      <NewsCard v-for="item in newsStore.news" :key="item.id" :news="item" />
    </div>
    <EditNewsDialog v-model="addDialog" />
  </q-page>
</template>

<script setup lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useNewsStore } from 'src/stores/news';
import EditNewsDialog from 'src/components/news/EditNewsDialog.vue';
import { useUserStore } from 'src/stores/user';
import NewsCard from 'src/components/news/NewsCard.vue';

import AudioRecorder from 'src/components/AudioRecorder.vue';

defineComponent({
  name: 'NewsPage',
});

const userStore = useUserStore();
const newsStore = useNewsStore();
const addDialog = ref(false);

onMounted(async () => {
  await newsStore.refresh();
});
</script>
