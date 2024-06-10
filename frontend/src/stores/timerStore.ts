import { defineStore } from 'pinia';
import { ref } from 'vue';
import { TimeTrackingItemNew } from 'src/models';
export const useTimerStore = defineStore('timer', () => {
  const timerRunning = ref(false);
  const selectedDate = ref('');
  const timeFrom = ref('');
  const timeTo = ref('');
  const selectedProject = ref('');
  const isNotificationVisible = ref(false);
  const notificationRef = ref<(() => void) | null>(null);
  const intervalId = ref<ReturnType<typeof setInterval> | null>(null);

  function startTimer(project: string) {
    const currentTime = new Date();
    selectedDate.value = currentTime.toISOString().slice(0, 10);
    timeFrom.value = formatTime(currentTime);
    timeTo.value = formatTime(currentTime);
    selectedProject.value = project;
    timerRunning.value = true;
  }
  const timeEntries = ref<TimeTrackingItemNew[]>([]);
  function addTimeEntry(entry: TimeTrackingItemNew) {
    timeEntries.value.push(entry);
  }

  function stopTimer() {
    timerRunning.value = false;
  }

  function calculateDuration() {
    const timeStart = new Date(`01/01/2007 ${timeFrom.value}`);
    const timeEnd = new Date(`01/01/2007 ${timeTo.value}`);
    const diff = Number(timeEnd) - Number(timeStart);
    return Math.floor(diff / 1000 / 60);
  }

  function formatTime(date: Date) {
    return date.toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  }

  return {
    timerRunning,
    selectedDate,
    timeFrom,
    timeTo,
    selectedProject,
    isNotificationVisible,
    notificationRef,
    intervalId,
    startTimer,
    stopTimer,
    calculateDuration,
    addTimeEntry,
  };
});
