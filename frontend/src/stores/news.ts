import { defineStore } from 'pinia'
import { api } from 'boot/axios'
import { useErrorStore } from 'src/stores/error'
import { actionNotification } from 'src/utils/notification'
import { NewsUpdate, News } from 'src/models'

const errorStore = useErrorStore()

export const useNewsStore = defineStore('news', {
  state: () => ({
    news: <News[]> [],
    refreshing: <boolean> false
  }),
  actions: {
    async refresh () {
      const dismiss = actionNotification('Refreshing news.')
      this.refreshing = true
      try {
        this.news = await api.get('/news/').then(response => response.data)
      } catch (error) {
        errorStore.reportError('Request failed', 'Unable to retrive news.', error)
      } finally {
        dismiss()
        this.refreshing = false
      }
    },
    async add (news: NewsUpdate) {
      const dismiss = actionNotification(`Creating news ${news.title}.`)
      try {
        await api.post('/news/', news)
        this.refresh()
      } catch (error) {
        errorStore.reportError('Request failed', `Failed to create document ${name}.`, error)
      } finally {
        dismiss()
      }
    },
    async update (news: NewsUpdate) {
      const dismiss = actionNotification(`Updating news ${news.title}.`)
      console.log(news)
      try {
        await api.put('/news/', news)
        this.refresh()
        return true
      } catch (error) {
        errorStore.reportError('Request failed', `Failed to update news ${news.title}.`, error)
      } finally {
        dismiss()
      }
      return false
    }
  }
})
