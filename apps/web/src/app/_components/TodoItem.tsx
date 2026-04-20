'use client';

import { useState } from 'react';

import { setTaskDone, type Task } from '@/lib/api';

type TodoItemProps = {
  task: Task;
  onToggle: (id: number, done: boolean) => void;
  onDelete: (id: number) => Promise<void>;
};

export function TodoItem({ task, onToggle, onDelete }: TodoItemProps) {
  const [pending, setPending] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const nextDone = e.target.checked;
    setError(null);
    setPending(true);
    onToggle(task.id, nextDone);
    try {
      await setTaskDone(task.id, nextDone);
    } catch (err) {
      onToggle(task.id, !nextDone);
      setError(err instanceof Error ? err.message : 'Failed to update task');
    } finally {
      setPending(false);
    }
  }

  async function handleDelete() {
    setError(null);
    setDeleting(true);
    try {
      await onDelete(task.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      setDeleting(false);
    }
  }

  return (
    <li
      style={{
        padding: '8px 12px',
        borderBottom: '1px solid #eee',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
      }}
    >
      <input
        type="checkbox"
        checked={task.done}
        onChange={handleChange}
        disabled={pending}
        aria-label={`Mark "${task.title}" as ${task.done ? 'not done' : 'done'}`}
      />
      <span
        style={{
          flex: 1,
          textDecoration: task.done ? 'line-through' : 'none',
          color: task.done ? '#888' : 'inherit',
        }}
      >
        {task.title}
      </span>
      <time
        dateTime={task.created_at}
        suppressHydrationWarning
        style={{ color: '#888', fontSize: '0.85em' }}
      >
        {formatTimestamp(task.created_at)}
      </time>
      {error && (
        <span role="alert" style={{ color: '#c00', fontSize: '0.85em' }}>
          {error}
        </span>
      )}
      <button
        type="button"
        onClick={handleDelete}
        disabled={deleting}
        aria-label={`Delete task "${task.title}"`}
        style={{
          background: 'transparent',
          border: '1px solid #ddd',
          color: '#c00',
          padding: '4px 8px',
          borderRadius: 4,
          cursor: deleting ? 'default' : 'pointer',
          fontSize: '0.85em',
        }}
      >
        Delete
      </button>
    </li>
  );
}

function formatTimestamp(iso: string): string {
  const normalized = /[Zz]|[+-]\d{2}:?\d{2}$/.test(iso) ? iso : `${iso}Z`;
  const d = new Date(normalized);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString();
}
