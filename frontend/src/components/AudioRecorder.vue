<template>
  <div @keydown="key_handler">
    <!-- text prompt with fixed height -->
    <div class="text-subtitle2" style="height: 70px; overflow-y: scroll">
      {{ selectedText }}
    </div>
    <q-input v-model="text" filled type="textarea" />
    <q-btn
      label="Remove last sentence"
      @click="removeLastSentence"
      :disable="recording || bussy"
    />
    <q-btn
      label="Add next sentence"
      @click="addNextSentence"
      :disable="recording"
    />
    <!-- start audio recording -->
    <q-btn
      :icon="recording ? 'stop' : 'mic'"
      color="primary"
      @click="recording ? stopAudioRecording() : startAudioRecording()"
      :disable="selectedText.length === 0 || bussy"
      size="xl"
    />
    <!-- cancel recording -->
    <q-btn
      round
      dense
      icon="cancel"
      color="negative"
      @click="stopAudioRecording(true)"
      :disable="!recording || bussy"
    />
    <!-- select input audio device -->
    <q-select
      v-model="selectedAudioDevice"
      :options="audioDevices"
      option-value="deviceId"
      option-label="label"
      label="Audio Device"
      dense
      @popup-show="refreshAudioDevices"
    />
  </div>
</template>

<script setup lang="ts">
import { AnnotationTask, AnnotationSubtask } from 'src/models';
import { defineComponent, computed } from 'vue';
import { useUserStore } from 'src/stores/user';
import { ref, onMounted } from 'vue';
import { api } from 'boot/axios';
import { start } from 'repl';

const text = ref('');
const selectedText = ref('');

const audioChunks: Blob[] = [];
let mediaRecorder: MediaRecorder | null = null;
const selectedAudioDevice = ref<MediaDeviceInfo | null>(null);
const audioDevices = ref<MediaDeviceInfo[]>([]);
let stream: MediaStream | null = null;
let recording = ref(false);
let bussy = ref(false);

function count_letters(text: string) {
  let count = 0;
  for (const character of text) {
    // only count letters - not spaces, number, interpunction, etc.
    if (character.match(/[a-zA-Z]/)) {
      count += 1;
    }
  }
  return count;
}

function key_handler(event: KeyboardEvent) {
  // space
  if (event.key === ' ') {
    if (recording.value) {
      stopAudioRecording();
    } else {
      if (count_letters(selectedText.value) > 0) {
        startAudioRecording();
      } else {
        addNextSentence();
      }
    }
  }
}

onMounted(async () => {
  audioDevices.value = await getAvailableAudioDevices();
  if (audioDevices.value.length > 0) {
    selectedAudioDevice.value = audioDevices.value[0];
  }
  // register key handler
  window.addEventListener('keydown', key_handler);
});

async function getAvailableAudioDevices() {
  const devices = await navigator.mediaDevices.enumerateDevices();
  const audioDevices = devices.filter((device) => device.kind === 'audioinput');
  return audioDevices;
}

async function refreshAudioDevices() {
  audioDevices.value = await getAvailableAudioDevices();
}

async function encodeBlob(blob: Blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result;
      resolve(base64String);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

async function startAudioRecording() {
  recording.value = true;
  bussy.value = true;
  try {
    const bitrate = 64000;
    stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        deviceId: selectedAudioDevice.value?.deviceId,
        channelCount: 1,
        echoCancellation: false,
        noiseSuppression: false,
      },
    });
    mediaRecorder = new MediaRecorder(stream, {
      audioBitsPerSecond: bitrate,
    });
    mediaRecorder.start();

    mediaRecorder.addEventListener('dataavailable', (event) => {
      audioChunks.push(event.data);
    });
  } catch (e) {
    console.log(e);
    stopAudioRecording();
  } finally {
    bussy.value = false;
  }
}

async function stopAudioRecording(cancel = false) {
  console.log('stopAudioRecording');
  console.log(stream);
  console.log(mediaRecorder);
  console.log(audioChunks);
  console.log(cancel);
  console.log(recording.value);
  console.log(bussy.value);
  bussy.value = true;

  if (mediaRecorder) {
    if (!cancel) {
      mediaRecorder.addEventListener('stop', async () => {
        console.log('EVENT stop');
        const audioBlob = new Blob(audioChunks, { type: audioChunks[0].type });
        const audioBase64 = await encodeBlob(audioBlob);
        await api
          .post('/audio', {
            audio_base64: audioBase64,
            mime_type: audioChunks[0].type,
            text: selectedText.value,
          })
          .then((response) => {
            console.log(response);
          })
          .catch((error) => {
            console.log(error);
          });
        audioChunks.length = 0;
        selectedText.value = '';
        recording.value = false;
        addNextSentence();
        bussy.value = false;
        startAudioRecording();
      });
    } else {
      mediaRecorder.addEventListener('stop', async () => {
        audioChunks.length = 0;
        recording.value = false;
        bussy.value = false;
      });
    }
    console.log('stop');
    if (stream) {
      stream.getTracks().forEach((track) => track.stop()); //stop each one
    }
    stream = null;
    mediaRecorder.stop();
    mediaRecorder = null;
  }
}

function addNextSentence() {
  /* Add next sentence from text to selectedText */
  const separators = ['.', '?', '!', ';', ':', '\n'];

  // try it 5 times
  for (let i = 0; i < 5; i++) {
    // find first separator
    let index = text.value.length;
    for (const separator of separators) {
      const i = text.value.indexOf(separator);
      if (i >= 0 && i < index) {
        index = i;
      }
    }
    if (index < text.value.length) {
      selectedText.value += text.value.substring(0, index + 1);
      text.value = text.value.substring(index + 1);
    } else {
      selectedText.value += text.value;
      text.value = '';
    }
    if (count_letters(selectedText.value) > 0) {
      break;
    }
  }
}

function removeLastSentence() {
  /* Remove last sentence from selectedText and add it to text */

  if (selectedText.value.length === 0) {
    return;
  }

  const separators = ['.', '?', '!'];
  // remove separator if it is the last character
  for (const separator of separators) {
    if (selectedText.value.endsWith(separator)) {
      text.value = separator + text.value;
      selectedText.value = selectedText.value.substring(
        0,
        selectedText.value.length - 1
      );
    }
  }

  // find last separator
  let index = -1;
  for (const separator of separators) {
    const i = selectedText.value.lastIndexOf(separator);
    if (i > index) {
      index = i;
    }
  }
  if (index >= 0) {
    text.value = selectedText.value.substring(index + 1) + text.value;
    selectedText.value = selectedText.value.substring(0, index + 1);
  } else {
    text.value = selectedText.value + text.value;
    selectedText.value = '';
  }
}
</script>
