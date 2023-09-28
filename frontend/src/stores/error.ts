import { defineStore } from 'pinia'

import { Notify } from 'quasar'

export const useErrorStore = defineStore('error', {
  state: () => ({
  }),
  actions: {
    async reportError (errorName: string, shortDescription: string, details: unknown) {
      console.log(details)
      Notify.create({
        message: `${errorName}: ${shortDescription}`,
        type: 'negative',
        position: 'bottom-right'
      })
    }
  }
})
