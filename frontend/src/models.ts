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

export interface AnnotationSubtaskUpdate {
  id: string
  annotation_task_id: string
  name: string
  description: string
  active: boolean
}

export interface AnnotationSubtask extends AnnotationSubtaskUpdate {
  created_date: string
  last_change: string
}

export interface AnnotationTaskUpdate {
  id: string
  name: string
  description: string
  active: boolean
}

export interface AnnotationTask extends AnnotationTaskUpdate {
  created_date: string
  last_change: string
  subtasks: AnnotationSubtaskUpdate[]
}

export interface AnnotationTaskInstanceUpdate {
  id: string
  annotation_task_id: string
  image: string
  text: string
  instance_metadata: string
  active: boolean
}

export interface AnnotationTaskInstance extends AnnotationTaskInstanceUpdate {
  created_date: string
  last_change: string
  result_count: number
}

export interface AnnotationTaskResultUpdate {
  id: string
  user_id: string
  annotation_task_instance_id: string
  result: string
}

export interface AnnotationTaskResult extends AnnotationTaskResultUpdate {
  created_date: string
  last_change: string
}

