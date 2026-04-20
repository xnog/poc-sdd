import { listTasks, type Task } from '@/lib/api';

import { TodoList } from './_components/TodoList';

export const dynamic = 'force-dynamic';

export default async function HomePage() {
  let initial: Task[] = [];
  let initialError: string | null = null;
  try {
    initial = await listTasks();
  } catch (err) {
    initialError =
      err instanceof Error ? err.message : 'Failed to load tasks';
  }

  return (
    <main
      style={{
        padding: 24,
        fontFamily: 'system-ui, sans-serif',
        maxWidth: 640,
        margin: '0 auto',
      }}
    >
      <h1>POC SDD — Todo list</h1>
      {initialError && (
        <div
          role="alert"
          style={{
            color: '#c00',
            fontSize: '0.9em',
            marginBottom: 12,
          }}
        >
          Couldn&apos;t load existing tasks ({initialError}). You can still
          create new ones.
        </div>
      )}
      <TodoList initial={initial} />
    </main>
  );
}
