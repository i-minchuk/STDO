import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export default function DocumentCreate() {
  const navigate = useNavigate();

  return (
    <div className="max-w-3xl mx-auto bg-white rounded-xl shadow-sm p-8">
      <button
        type="button"
        onClick={() => navigate('/documents')}
        className="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 mb-6"
      >
        <ArrowLeft size={18} /> Вернуться к документам
      </button>
      <h1 className="text-2xl font-bold mb-4">Создать документ</h1>
      <p className="text-gray-600">Функция создания документа будет доступна в следующем обновлении.</p>
    </div>
  );
}
