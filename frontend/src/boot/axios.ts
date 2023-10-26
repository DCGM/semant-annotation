import { boot } from 'quasar/wrappers'
import { useUserStore } from 'src/stores/user'
import { useErrorStore } from 'src/stores/error'
import axios, { AxiosInstance } from 'axios'

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
    $api: AxiosInstance;
  }
}

axios.defaults.withCredentials = true

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
const apiURL = process.env.BACKEND_URL ? process.env.BACKEND_URL + '/api' : 'http://pchradis2.fit.vutbr.cz:8000/api'
const api = axios.create({ baseURL: apiURL })

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API

  const userStore = useUserStore()
  const errorStore = useErrorStore()
  // const router = useRouter()
  // const route = useRoute()

  let lastRenew = new Date()

  api.interceptors.response.use(
    (response) => {
    // Any status code that lie within the range of 2xx cause this function to trigger
    // Do something with response data
      const now = new Date()
      if (now.valueOf() - lastRenew.valueOf() > 30000) {
        lastRenew = now
        api.post('/token/renew')
      }
      return response
    },
    (error) => {
      if (error.response && error.response.status === 401 && userStore.user != null) {
        userStore.user = null
        errorStore.reportError('ERROR', 'Authorization expired.', error.response)
        window.location.pathname = '/'
        // router.push({ name: 'login' }) // , query: { next: route.fullPath } */
      }
      // Do something with response error
      return Promise.reject(error)
    })
})

export { api, apiURL }
