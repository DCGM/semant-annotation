import { api } from 'boot/axios'
import { defineStore } from 'pinia'
import { useErrorStore } from 'src/stores/error'
import { UserWithPassword, User } from 'src/models'
import qs from 'qs'

interface UserStore {
  user: User | null
}

export const useUserStore = defineStore('user', {
  state: (): UserStore => ({
    user: null
  }),
  actions: {
    async setAuthorized () {
      await this.testAuthentication()
    },
    async testAuthentication () {
      try {
        const response = await api.get('me')
          .then(response => response.data)
          .catch(error => {
            if (error.response.status === 401) {
              Promise.resolve(null)
            }
          })
        if (response != null) {
          this.user = response
        } else {
          this.signOut()
        }
      } catch (error) {
        useErrorStore().reportError('ERROR', 'Failed authentication test.', error)
      }
    },
    signOut () {
      this.user = null
      document.cookie = 'Authorization=;  Max-Age=0'
    },
    async signIn (userName: string, password: string) {
      try {
        await api.post('/token', qs.stringify({ username: userName, password }),
          { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
        await this.testAuthentication()
      } catch (error) {
        useErrorStore().reportError('ERROR', 'Failed to sign in.', error)
      }
    },

    async registr_user (user: UserWithPassword) {
      try {
        await api.post('/user/', user)
        this.signIn(user.username, user.password)
      } catch (error) {
        useErrorStore().reportError('ERROR', 'Failed to register user.', error)
      }
    }

  }
})
