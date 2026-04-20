'use client';

import { useState, type FormEvent } from 'react';

import { createTask, type Task } from '@/lib/api';

type TodoFormProps = {
  onCreated: (task: Task) => void;
};

export function TodoForm({ onCreated }: TodoFormProps) {
  const [title, setTitle] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = title.trim().length > 0 && !submitting;

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!canSubmit) return;

    setSubmitting(true);
    setError(null);
    try {
      const task = await createTask(title);
      onCreated(task);
      setTitle('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', gap: 8, flexDirection: 'column' }}>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs doing?"
          disabled={submitting}
          style={{
            flex: 1,
            padding: '8px 12px',
            fontSize: 16,
            border: '1px solid #ccc',
            borderRadius: 4,
          }}
          aria-label="Task title"
        />
        <button
          type="submit"
          disabled={!canSubmit}
          style={{
            padding: '8px 16px',
            fontSize: 16,
            border: '1px solid #333',
            borderRadius: 4,
            background: canSubmit ? '#333' : '#999',
            color: 'white',
            cursor: canSubmit ? 'pointer' : 'not-allowed',
          }}
        >
          Add
        </button>
      </div>
      {error && (
        <div role="alert" style={{ color: '#c00', fontSize: '0.9em' }}>
          {error}
        </div>
      )}
    </form>
  );
}
