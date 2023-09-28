export interface User {
  id: string
  username: string
  email: string
  full_name: string
  institution: string
  trusted: number
  disabled: boolean
}

export interface UserWithPassword extends User {
  password: string
}

export class NewsUpdate {
  id = ''
  title = ''
  short = ''
  content = ''
  deleted = false
  released_date: string | null = null
}

export class News extends NewsUpdate {
  created_date = ''
  last_change = ''
}
