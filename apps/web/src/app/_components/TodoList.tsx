'use client';

import { useState } from 'react';

import { deleteTask as apiDeleteTask, type Task } from '@/lib/api';

import { TodoForm } from './TodoForm';
import { TodoItem } from './TodoItem';

type TodoListProps = {
  initial: Task[];
};

export function TodoList({ initial }: TodoListProps) {
  const [tasks, setTasks] = useState<Task[]>(initial);

  function prepend(task: Task) {
    setTasks((prev) => [task, ...prev]);
  }

  function setDone(id: number, done: boolean) {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, done } : t)),
    );
  }

  async function deleteTask(id: number): Promise<void> {
    let removed: { task: Task; index: number } | null = null;
    setTasks((prev) => {
      const index = prev.findIndex((t) => t.id === id);
      if (index === -1) return prev;
      removed = { task: prev[index], index };
      return [...prev.slice(0, index), ...prev.slice(index + 1)];
    });

    try {
      await apiDeleteTask(id);
    } catch (err) {
      if (removed) {
        const { task, index } = removed;
        setTasks((prev) => [...prev.slice(0, index), task, ...prev.slice(index)]);
      }
      throw err;
    }
  }

  return (
    <div>
      <TodoForm onCreated={prepend} />
      {tasks.length === 0 ? (
        <p style={{ color: '#666', marginTop: 16 }}>
          No tasks yet — create your first above.
        </p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0, marginTop: 16 }}>
          {tasks.map((task) => (
            <TodoItem
              key={task.id}
              task={task}
              onToggle={setDone}
              onDelete={deleteTask}
            />
          ))}
        </ul>
      )}
    </div>
  );
}
