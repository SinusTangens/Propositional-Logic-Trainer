/**
 * API Service für die Kommunikation mit dem Django Backend
 * Nutzt den Vite Proxy (/api -> localhost:8000/api) für Same-Origin Requests
 */

const API_BASE = '/api';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

/**
 * CSRF Token aus Cookie holen
 */
function getCsrfToken(): string | null {
  const name = 'csrftoken';
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='));
  return cookieValue ? cookieValue.split('=')[1] : null;
}

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options?: RequestInit
): Promise<ApiResponse<T>> {
  try {
    const csrfToken = getCsrfToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options?.headers,
    };
    
    if (csrfToken) {
      (headers as Record<string, string>)['X-CSRFToken'] = csrfToken;
    }
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
      credentials: 'include', // Wichtig für Session-Cookies
      headers,
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      
      // Handle DRF validation errors (field-based errors)
      if (typeof errorData === 'object' && !errorData.error) {
        const errorMessages: string[] = [];
        for (const [field, messages] of Object.entries(errorData)) {
          if (Array.isArray(messages)) {
            // Map English error messages to German
            const translatedMessages = messages.map(msg => translateErrorMessage(String(msg)));
            errorMessages.push(`${getFieldLabel(field)}: ${translatedMessages.join(', ')}`);
          } else if (typeof messages === 'string') {
            errorMessages.push(`${getFieldLabel(field)}: ${translateErrorMessage(messages)}`);
          }
        }
        if (errorMessages.length > 0) {
          throw new Error(errorMessages.join('\n'));
        }
      }
      
      throw new Error(errorData.error || `API Error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return { data };
  } catch (error) {
    console.error('API Error:', error);
    return { error: error instanceof Error ? error.message : 'Unknown error' };
  }
}

/**
 * Translate common Django error messages to German
 */
function translateErrorMessage(msg: string): string {
  const translations: Record<string, string> = {
    'This password is too similar to the username.': 'Das Passwort ist dem Benutzernamen zu ähnlich.',
    'This password is too short. It must contain at least 8 characters.': 'Das Passwort ist zu kurz. Es muss mindestens 8 Zeichen enthalten.',
    'This password is too common.': 'Dieses Passwort ist zu häufig verwendet.',
    'This password is entirely numeric.': 'Das Passwort darf nicht nur aus Zahlen bestehen.',
    'A user with that username already exists.': 'Ein Benutzer mit diesem Benutzernamen existiert bereits.',
    'user with this email already exists.': 'Ein Benutzer mit dieser E-Mail existiert bereits.',
    'Enter a valid email address.': 'Bitte geben Sie eine gültige E-Mail-Adresse ein.',
    'This field may not be blank.': 'Dieses Feld darf nicht leer sein.',
    'This field is required.': 'Dieses Feld ist erforderlich.',
    'The passwords do not match.': 'Die Passwörter stimmen nicht überein.',
  };
  
  return translations[msg] || msg;
}

/**
 * Get German field labels
 */
function getFieldLabel(field: string): string {
  const labels: Record<string, string> = {
    'username': 'Benutzername',
    'email': 'E-Mail',
    'password': 'Passwort',
    'password2': 'Passwort bestätigen',
    'first_name': 'Vorname',
    'last_name': 'Nachname',
    'non_field_errors': 'Fehler',
  };
  
  return labels[field] || field;
}

// ============================================================
// Auth API
// ============================================================

export interface LevelProgress {
  type: string;
  task_type: string;
  currentLevel: number;
  totalLevels: number;
  correctInRow: number;
  requiredCorrect: number;
  isUnlocked: boolean;
  isCompleted: boolean;
}

export interface UserStats {
  totalSolved: number;
  correctSolved: number;
  currentStreak: number;
  highscoreStreak: number;
}

export interface AvatarSettings {
  skinColor: string;
  hairColor: string;
  top: string;
  accessories: string;
  facialHair: string;
  clothing: string;
  clothingColor: string;
  eyes: string;
  eyebrows: string;
  mouth: string;
  url: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
  progress: LevelProgress[];
  stats: UserStats;
  avatar: AvatarSettings;
}

export interface AuthResponse {
  isAuthenticated: boolean;
  user: User | null;
}

export interface LoginData {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  password2: string;
  first_name?: string;
  last_name?: string;
}

export async function checkAuth(): Promise<ApiResponse<AuthResponse>> {
  return apiFetch<AuthResponse>('/auth/me/');
}

export async function login(data: LoginData): Promise<ApiResponse<{ message: string; user: User }>> {
  return apiFetch<{ message: string; user: User }>('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function register(data: RegisterData): Promise<ApiResponse<{ message: string; user: User }>> {
  return apiFetch<{ message: string; user: User }>('/auth/register/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function logout(): Promise<ApiResponse<{ message: string }>> {
  return apiFetch<{ message: string }>('/auth/logout/', {
    method: 'POST',
  });
}

export async function changePassword(oldPassword: string, newPassword: string, newPassword2: string): Promise<ApiResponse<{ message: string }>> {
  return apiFetch<{ message: string }>('/auth/password-change/', {
    method: 'POST',
    body: JSON.stringify({
      old_password: oldPassword,
      new_password: newPassword,
      new_password2: newPassword2,
    }),
  });
}

export async function resetProgress(): Promise<ApiResponse<{ message: string; user: User }>> {
  return apiFetch<{ message: string; user: User }>('/auth/reset-progress/', {
    method: 'POST',
  });
}

// ============================================================
// Avatar API
// ============================================================

export async function updateAvatar(settings: Partial<Omit<AvatarSettings, 'url'>>): Promise<ApiResponse<{ message: string; avatar: AvatarSettings }>> {
  return apiFetch<{ message: string; avatar: AvatarSettings }>('/auth/avatar/', {
    method: 'POST',
    body: JSON.stringify(settings),
  });
}

export async function randomizeAvatar(): Promise<ApiResponse<{ message: string; avatar: AvatarSettings }>> {
  return apiFetch<{ message: string; avatar: AvatarSettings }>('/auth/avatar/random/', {
    method: 'POST',
  });
}

// ============================================================
// Task API
// ============================================================

export interface Task {
  id: number;
  task_type: 'DIRECT_INFERENCE' | 'CASE_SPLIT';
  level: number;
  premises: string[];
  variables: string[];
  created_at: string;
}

export interface GenerateTaskRequest {
  task_type: 'DIRECT_INFERENCE' | 'CASE_SPLIT';
  level: number;
}

export async function getTasks(): Promise<ApiResponse<Task[]>> {
  return apiFetch<Task[]>('/tasks/');
}

export async function getTask(id: number): Promise<ApiResponse<Task>> {
  return apiFetch<Task>(`/tasks/${id}/`);
}

export async function createTask(taskData: Partial<Task>): Promise<ApiResponse<Task>> {
  return apiFetch<Task>('/tasks/', {
    method: 'POST',
    body: JSON.stringify(taskData),
  });
}

export async function generateTask(params: GenerateTaskRequest): Promise<ApiResponse<Task>> {
  return apiFetch<Task>('/tasks/generate/', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

export async function getTasksByType(taskType: string, level?: number): Promise<ApiResponse<Task[]>> {
  const params = new URLSearchParams({ task_type: taskType });
  if (level !== undefined) {
    params.append('level', level.toString());
  }
  return apiFetch<Task[]>(`/tasks/by_type/?${params.toString()}`);
}

export async function deleteTask(id: number): Promise<ApiResponse<void>> {
  return apiFetch<void>(`/tasks/${id}/`, {
    method: 'DELETE',
  });
}

// ============================================================
// Solve API
// ============================================================

export interface VariableResult {
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
}

export interface ProgressUpdate {
  level_up: boolean;
  type_completed: boolean;
  new_level: number;
  correct_in_row: number;
}

export interface SolveResponse {
  is_correct: boolean;
  results: Record<string, VariableResult>;
  progress: ProgressUpdate;
  user_progress: LevelProgress[];
  stats: UserStats;
}

export interface SolveRequest {
  task_id: number;
  answers: Record<string, string>;
}

export async function solveTask(data: SolveRequest): Promise<ApiResponse<SolveResponse>> {
  return apiFetch<SolveResponse>('/solve/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export interface FeedbackResponse {
  variable: string;
  feedback: string;
}

export async function getFeedback(taskId: number, variable: string, userAnswer: string): Promise<ApiResponse<FeedbackResponse>> {
  return apiFetch<FeedbackResponse>('/feedback/', {
    method: 'POST',
    body: JSON.stringify({
      task_id: taskId,
      variable,
      user_answer: userAnswer,
    }),
  });
}

export async function getSolution(taskId: number): Promise<ApiResponse<{ solution: Record<string, string>; cached: boolean }>> {
  return apiFetch<{ solution: Record<string, string>; cached: boolean }>(`/solution/${taskId}/`);
}

// ============================================================
// Attempt API (Legacy)
// ============================================================

export interface Attempt {
  id: number;
  user: User;
  task: number;
  solution: Record<string, unknown>;
  is_correct: boolean;
  feedback: string;
  timestamp: string;
}

export interface CreateAttemptData {
  user_id: number;
  task_id: number;
  solution: Record<string, unknown>;
  is_correct: boolean;
  feedback: string;
}

export async function getAttempts(): Promise<ApiResponse<Attempt[]>> {
  return apiFetch<Attempt[]>('/attempts/');
}

export async function getUserAttempts(userId: number): Promise<ApiResponse<Attempt[]>> {
  return apiFetch<Attempt[]>(`/attempts/?user=${userId}`);
}

export async function submitAttempt(
  attemptData: CreateAttemptData
): Promise<ApiResponse<Attempt>> {
  return apiFetch<Attempt>('/attempts/', {
    method: 'POST',
    body: JSON.stringify(attemptData),
  });
}

export default {
  // Auth
  checkAuth,
  login,
  register,
  logout,
  changePassword,
  resetProgress,
  // Tasks
  getTasks,
  getTask,
  createTask,
  generateTask,
  getTasksByType,
  deleteTask,
  // Solve
  solveTask,
  getFeedback,
  getSolution,
  // Attempts
  getAttempts,
  getUserAttempts,
  submitAttempt,
};
