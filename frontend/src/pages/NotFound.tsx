import { Link } from 'react-router-dom';
import { ArrowLeft, SearchX } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="w-full max-w-xl rounded-2xl border border-gray-200 bg-white p-8 text-center shadow-sm">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-gray-100 text-gray-500">
          <SearchX size={28} />
        </div>

        <p className="text-sm font-semibold uppercase tracking-[0.2em] text-gray-400">404</p>
        <h1 className="mt-2 text-3xl font-bold text-gray-900">Страница не найдена</h1>
        <p className="mt-3 text-sm leading-6 text-gray-500">
          Возможно, ссылка устарела, страница была перемещена или адрес введён с ошибкой.
        </p>

        <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
          <Link
            to="/dashboard"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white no-underline hover:bg-primary-700"
          >
            На главную
          </Link>

          <Link
            to="/documents"
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-4 py-2.5 text-sm font-medium text-gray-700 no-underline hover:bg-gray-50"
          >
            <ArrowLeft size={16} />
            К документам
          </Link>
        </div>
      </div>
    </div>
  );
}