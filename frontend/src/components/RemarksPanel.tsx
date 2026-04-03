import { useState, useEffect } from "react";
import { MessageSquare, CheckCircle, XCircle, RotateCcw, Send } from "lucide-react";

type RemarkStatus = "open" | "resolved" | "rejected" | "superseded";

interface RemarkResponse {
  id: number; author_name: string; text: string; created_at: string;
}
interface Remark {
  id: number; source: string; text: string; status: RemarkStatus;
  author_name: string; assignee_name?: string;
  resolution_comment?: string; created_at: string;
  document_id?: number; responses: RemarkResponse[];
}

const STATUS_UI: Record<RemarkStatus, { label: string; cls: string }> = {
  open:       { label: "Открыто",           cls: "bg-red-100 text-red-700 border-red-200" },
  resolved:   { label: "✅ Решено",          cls: "bg-green-100 text-green-700 border-green-200" },
  rejected:   { label: "❌ Ошибочно",        cls: "bg-gray-100 text-gray-600 border-gray-200" },
  superseded: { label: "🔄 Снято (изм. ТЗ)", cls: "bg-yellow-100 text-yellow-700 border-yellow-200" },
};

const SOURCE_LABEL: Record<string, string> = {
  internal: "Внутреннее", customer: "Заказчик", reviewer: "Проверяющий",
};

export default function RemarksPanel({ projectId }: { projectId: number }) {
  const [remarks, setRemarks] = useState<Remark[]>([]);
  const [filter, setFilter] = useState<RemarkStatus | "all">("all");
  const [replyTexts, setReplyTexts] = useState<Record<number, string>>({});
  const [newText, setNewText] = useState("");
  const [loading, setLoading] = useState(false);

  const fetchRemarks = async () => {
    setLoading(true);
    try {
      const url = `/api/remarks/project/${projectId}${filter !== "all" ? `?status=${filter}` : ""}`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      if (res.ok) setRemarks(await res.json());
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchRemarks(); }, [projectId, filter]);

  const updateStatus = async (id: number, status: RemarkStatus, comment?: string) => {
    await fetch(`/api/remarks/${id}/resolve`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json",
                 Authorization: `Bearer ${localStorage.getItem("token")}` },
      body: JSON.stringify({ status, comment }),
    });
    fetchRemarks();
  };

  const sendResponse = async (remarkId: number) => {
    const text = replyTexts[remarkId]?.trim();
    if (!text) return;
    await fetch(`/api/remarks/${remarkId}/responses`, {
      method: "POST",
      headers: { "Content-Type": "application/json",
                 Authorization: `Bearer ${localStorage.getItem("token")}` },
      body: JSON.stringify({ text }),
    });
    setReplyTexts(prev => ({ ...prev, [remarkId]: "" }));
    fetchRemarks();
  };

  const addRemark = async () => {
    if (!newText.trim()) return;
    await fetch("/api/remarks/", {
      method: "POST",
      headers: { "Content-Type": "application/json",
                 Authorization: `Bearer ${localStorage.getItem("token")}` },
      body: JSON.stringify({ project_id: projectId, text: newText }),
    });
    setNewText("");
    fetchRemarks();
  };

  const filtered = filter === "all" ? remarks : remarks.filter(r => r.status === filter);
  const counts = remarks.reduce((acc, r) => {
    acc[r.status] = (acc[r.status] || 0) + 1; return acc;
  }, {} as Record<string, number>);

  return (
    <aside className="w-96 h-full flex flex-col border-l border-gray-200 bg-white shadow-xl">
      {/* Заголовок */}
      <div className="p-4 border-b bg-gray-50 flex items-center gap-2">
        <MessageSquare size={18} className="text-blue-600" />
        <span className="font-semibold text-gray-800">Замечания по проекту</span>
        <span className="ml-auto text-xs bg-red-500 text-white px-2 py-0.5 rounded-full">
          {counts["open"] || 0} откр.
        </span>
      </div>

      {/* Фильтры */}
      <div className="flex gap-1.5 p-3 border-b flex-wrap">
        {(["all", "open", "resolved", "rejected", "superseded"] as const).map(s => (
          <button key={s} onClick={() => setFilter(s)}
            className={`px-2.5 py-1 rounded-full text-xs font-medium border transition-all
              ${filter === s ? "bg-blue-600 text-white border-blue-600"
                             : "bg-white text-gray-600 border-gray-300 hover:border-blue-400"}`}>
            {s === "all" ? `Все (${remarks.length})` : `${STATUS_UI[s].label} (${counts[s] || 0})`}
          </button>
        ))}
      </div>

      {/* Список замечаний */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {loading && <p className="text-center text-sm text-gray-400 py-4">Загрузка...</p>}
        {!loading && filtered.length === 0 && (
          <p className="text-center text-sm text-gray-400 py-8">Нет замечаний</p>
        )}
        {filtered.map(remark => (
          <div key={remark.id}
            className={`border rounded-xl p-3 transition-all
              ${remark.status === "open" ? "border-red-200 bg-red-50/30"
                : "border-gray-200 bg-white"}`}>

            {/* Заголовок замечания */}
            <div className="flex justify-between items-start mb-2 gap-2">
              <div className="flex items-center gap-1.5 flex-wrap">
                <span className="text-xs text-gray-400">#{remark.id}</span>
                <span className="text-xs px-2 py-0.5 rounded bg-blue-50 text-blue-600 border border-blue-200">
                  {SOURCE_LABEL[remark.source] || remark.source}
                </span>
              </div>
              <span className={`text-xs px-2 py-0.5 rounded-full border font-medium whitespace-nowrap
                ${STATUS_UI[remark.status as RemarkStatus]?.cls}`}>
                {STATUS_UI[remark.status as RemarkStatus]?.label}
              </span>
            </div>

            <p className="text-sm text-gray-800 mb-2 leading-relaxed">{remark.text}</p>
            <p className="text-xs text-gray-400 mb-2">
              {remark.author_name} · {new Date(remark.created_at).toLocaleDateString("ru-RU")}
              {remark.assignee_name && ` → ${remark.assignee_name}`}
            </p>

            {/* Наши ответы */}
            {remark.responses.map(resp => (
              <div key={resp.id}
                className="mt-2 pl-3 border-l-2 border-blue-400 bg-blue-50/50 rounded-r py-1 pr-2">
                <p className="text-xs font-semibold text-blue-700">{resp.author_name}:</p>
                <p className="text-sm text-gray-800">{resp.text}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {new Date(resp.created_at).toLocaleDateString("ru-RU")}
                </p>
              </div>
            ))}

            {/* Поле ответа */}
            {remark.status === "open" && (
              <div className="mt-2 flex gap-2">
                <input
                  type="text"
                  placeholder="Написать ответ..."
                  value={replyTexts[remark.id] || ""}
                  onChange={e => setReplyTexts(p => ({...p, [remark.id]: e.target.value}))}
                  onKeyDown={e => e.key === "Enter" && sendResponse(remark.id)}
                  className="flex-1 text-xs border rounded-lg px-2 py-1.5 focus:outline-none
                    focus:ring-1 focus:ring-blue-400"
                />
                <button onClick={() => sendResponse(remark.id)}
                  className="p-1.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
                  <Send size={12} />
                </button>
              </div>
            )}

            {/* Кнопки смены статуса */}
            {remark.status === "open" && (
              <div className="mt-2.5 flex gap-1.5 flex-wrap">
                <button onClick={() => updateStatus(remark.id, "resolved", "Замечание устранено")}
                  className="flex items-center gap-1 text-xs bg-green-500 text-white
                    px-2.5 py-1 rounded-lg hover:bg-green-600">
                  <CheckCircle size={11} /> Решено
                </button>
                <button onClick={() => updateStatus(remark.id, "rejected",
                  "Замечание ошибочно назначено")}
                  className="flex items-center gap-1 text-xs bg-gray-400 text-white
                    px-2.5 py-1 rounded-lg hover:bg-gray-500">
                  <XCircle size={11} /> Ошибочно
                </button>
                <button onClick={() => updateStatus(remark.id, "superseded",
                  "Снято в связи с изменением ТЗ")}
                  className="flex items-center gap-1 text-xs bg-yellow-500 text-white
                    px-2.5 py-1 rounded-lg hover:bg-yellow-600">
                  <RotateCcw size={11} /> Изм. ТЗ
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Поле нового замечания */}
      <div className="p-3 border-t bg-gray-50">
        <div className="flex gap-2">
          <input type="text" placeholder="Новое замечание..."
            value={newText} onChange={e => setNewText(e.target.value)}
            onKeyDown={e => e.key === "Enter" && addRemark()}
            className="flex-1 text-sm border rounded-lg px-3 py-2 focus:outline-none
              focus:ring-2 focus:ring-blue-400" />
          <button onClick={addRemark}
            className="bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 text-sm">
            +
          </button>
        </div>
      </div>
    </aside>
  );
}