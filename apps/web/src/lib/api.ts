/**
 * Thin client for the `api` app's todo-list endpoints.
 *
 * Base URL comes from `NEXT_PUBLIC_API_BASE_URL`, defaulting to
 * `http://localhost:8000` for local dev.
 */

export type Task = {
  id: number;
  title: string;
  done: boolean;
  created_at: string;
};

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export async function listTasks(): Promise<Task[]> {
  const res = await fetch(`${API_BASE_URL}/tasks`, { cache: 'no-store' });
  if (!res.ok) {
    throw new Error(`Failed to list tasks: ${res.status}`);
  }
  return (await res.json()) as Task[];
}

export async function createTask(title: string): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body?.detail) detail = body.detail;
    } catch {
      // non-JSON error body; keep the default detail
    }
    throw new Error(detail);
  }
  return (await res.json()) as Task;
}

export async function deleteTask(id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/tasks/${id}`, { method: 'DELETE' });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body?.detail) detail = body.detail;
    } catch {
      // non-JSON error body
    }
    throw new Error(detail);
  }
}

export async function setTaskDone(id: number, done: boolean): Promise<Task> {
  const res = await fetch(`${API_BASE_URL}/tasks/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ done }),
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body?.detail) detail = body.detail;
    } catch {
      // non-JSON error body
    }
    throw new Error(detail);
  }
  return (await res.json()) as Task;
}
