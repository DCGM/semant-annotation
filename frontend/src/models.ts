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

export class AnnotationSubtaskUpdate {
  id = ''
  annotation_task_id  = ''
  name = ''
  description = ''
  active = false
}

export class AnnotationSubtask extends AnnotationSubtaskUpdate {
  created_date = ''
  last_change = ''
}

export class AnnotationTaskUpdate {
  id = ''
  name = ''
  description = ''
  active = false
}

export class AnnotationTask extends AnnotationTaskUpdate {
  created_date = ''
  last_change = ''
  subtasks: AnnotationSubtask[] = []
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
  result_type: string
}

export interface AnnotationTaskResult extends AnnotationTaskResultUpdate {
  created_date: string
  last_change: string
}

