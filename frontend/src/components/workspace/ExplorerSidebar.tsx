import { useWorkspaceStore } from './store/workspaceStore';
import { Folder, FileText, CheckSquare, MessageSquare } from 'lucide-react';
import { useEffect } from 'react';

interface ExplorerSidebarProps {
  projectId?: string;
}

// Мок-данные определены вне компонента, чтобы не пересоздавались
const INITIAL_EXPLORER_DATA = [
  {
    id: 'project-1',
    type: 'project' as const,
    label: 'Завод "Альфа"',
    code: 'PRJ-001',
    expanded: true,
    children: [
      {
        id: 'stage-p',
        type: 'stage' as const,
        label: 'Стадия П',
        expanded: true,
        children: [
          {
            id: 'kit-km',
            type: 'kit' as const,
            label: 'Комплект КМ',
            count: 142,
            expanded: true,
            children: [
              {
                id: 'section-km1',
                type: 'section' as const,
                label: 'Раздел КМ1',
                status: 'in-progress',
                expanded: true,
                children: [
                  {
                    id: 'doc-km1-001',
                    type: 'document' as const,
                    label: 'КМ1-А01',
                    code: 'КМ1-А01',
                    status: 'approved',
                  },
                  {
                    id: 'doc-km1-002',
                    type: 'document' as const,
                    label: 'КМ1-А02',
                    code: 'КМ1-А02',
                    status: 'in-review',
                  },
                ],
              },
              {
                id: 'section-km2',
                type: 'section' as const,
                label: 'Раздел КМ2',
                status: 'approval',
              },
            ],
          },
          {
            id: 'kit-kj',
            type: 'kit' as const,
            label: 'Комплект КЖ',
            count: 89,
          },
        ],
      },
      {
        id: 'stage-r',
        type: 'stage' as const,
        label: 'Стадия Р',
        children: [
          {
            id: 'kit-kmd',
            type: 'kit' as const,
            label: 'Комплект КМД',
            count: 56,
          },
        ],
      },
      {
        id: 'tasks-group',
        type: 'task' as const,
        label: 'Задачи группы',
        count: 12,
      },
    ],
  },
];

export default function ExplorerSidebar({}: ExplorerSidebarProps) {
  const { explorerData, activeExplorerNode, setActiveExplorerNode, toggleExplorerNode, addTab, setExplorerData } =
    useWorkspaceStore();

  // Инициализация данных при первом рендере
  useEffect(() => {
    if (explorerData.length === 0) {
      setExplorerData(INITIAL_EXPLORER_DATA);
    }
  }, []);

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'approved':
      case 'in-progress':
        return 'var(--success)';
      case 'in-review':
      case 'approval':
        return 'var(--warning)';
      case 'rejected':
      case 'error':
        return 'var(--error)';
      default:
        return 'var(--text-tertiary)';
    }
  };

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'project':
        return <Folder size={16} />;
      case 'stage':
        return <Folder size={16} />;
      case 'kit':
        return <Folder size={16} />;
      case 'section':
        return <Folder size={16} />;
      case 'document':
        return <FileText size={16} />;
      case 'task':
        return <CheckSquare size={16} />;
      case 'remark':
        return <MessageSquare size={16} />;
      default:
        return <FileText size={16} />;
    }
  };

  const handleNodeClick = (node: any, hasChildren: boolean) => {
    setActiveExplorerNode(node.id);
    
    // Если это документ, открываем его во вкладке
    if (node.type === 'document') {
      addTab({
        id: node.id,
        type: 'document',
        title: node.label,
        subtitle: node.code || node.status,
        icon: <FileText size={14} />,
        file: node.file, // Передаём файл если есть
      });
    } else if (hasChildren) {
      // Если это папка с children, разворачиваем/сворачиваем
      toggleExplorerNode(node.id);
    }
  };

  const renderTree = (nodes: any[], level: number = 0) => {
    return nodes.map((node) => {
      const hasChildren = node.children && node.children.length > 0;
      const isActive = node.id === activeExplorerNode;
      const isExpanded = node.expanded ?? true;

      return (
        <div key={node.id}>
          <div
            className={`flex items-center gap-1 px-2 py-1 cursor-pointer transition-colors rounded ${
              isActive ? '' : 'hover:bg-[var(--bg-hover)]'
            }`}
            style={{
              paddingLeft: `${level * 12 + 6}px`,
              backgroundColor: isActive ? 'var(--topbar-active)' : 'transparent',
            }}
            onClick={(e) => {
              e.stopPropagation();
              handleNodeClick(node, hasChildren);
            }}
            role="treeitem"
            aria-expanded={hasChildren ? isExpanded : undefined}
            aria-selected={isActive}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                handleNodeClick(node, hasChildren);
              }
            }}
          >
            {/* Expand/Collapse icon */}
            <div className="w-2.5 h-2.5 flex items-center justify-center shrink-0">
              {hasChildren && (
                <span
                  className="text-[9px] leading-none"
                  style={{ color: 'var(--text-tertiary)' }}
                >
                  {isExpanded ? '▼' : '▶'}
                </span>
              )}
            </div>

            {/* Node icon */}
            <span
              className="shrink-0"
              style={{ color: 'var(--text-secondary)' }}
            >
              {getNodeIcon(node.type)}
            </span>

            {/* Node label */}
            <div className="flex-1 min-w-0">
              <div
                className="text-xs font-medium truncate leading-tight"
                style={{ color: 'var(--text-primary)' }}
              >
                {node.label}
              </div>
              {node.code && (
                <div
                  className="text-[10px] font-mono truncate"
                  style={{ color: 'var(--text-tertiary)' }}
                >
                  {node.code}
                </div>
              )}
            </div>

            {/* Count badge */}
            {node.count !== undefined && (
              <span
                className="text-[10px] px-1 py-0.5 rounded shrink-0"
                style={{
                  backgroundColor: 'var(--bg-surface-2)',
                  color: 'var(--text-tertiary)',
                }}
              >
                {node.count}
              </span>
            )}

            {/* Status indicator */}
            {node.status && (
              <span
                className="w-1.5 h-1.5 rounded-full shrink-0"
                style={{ backgroundColor: getStatusColor(node.status) }}
              />
            )}
          </div>

          {/* Render children if expanded */}
          {hasChildren && isExpanded && (
            <div role="group">
              {renderTree(node.children, level + 1)}
            </div>
          )}
        </div>
      );
    });
  };

  return (
    <aside
      className="flex flex-col h-full"
      style={{ backgroundColor: 'var(--bg-surface)' }}
      role="tree"
      aria-label="Обозреватель проектов"
    >
      {/* Header с поиском */}
      <div
        className="px-2.5 py-2 border-b"
        style={{ borderColor: 'var(--border-default)' }}
      >
        <h3
          className="text-xs font-semibold mb-1.5"
          style={{ color: 'var(--text-primary)' }}
        >
          Проекты
        </h3>

        {/* Поиск */}
        <input
          type="text"
          placeholder="Поиск..."
          className="w-full px-2 py-1 text-xs rounded border focus:outline-none focus:ring-1 transition-all"
          style={{
            backgroundColor: 'var(--bg-surface-2)',
            borderColor: 'var(--border-default)',
            color: 'var(--text-primary)',
          }}
          onFocus={(e) => {
            e.target.style.borderColor = 'var(--primary)';
            e.target.style.boxShadow = '0 0 0 2px rgba(124, 58, 237, 0.1)';
          }}
          onBlur={(e) => {
            e.target.style.borderColor = 'var(--border-default)';
            e.target.style.boxShadow = 'none';
          }}
        />
      </div>

      {/* Дерево сущностей */}
      <div className="flex-1 overflow-y-auto py-0.5" role="group">
        {renderTree(explorerData)}
      </div>

      {/* Footer со статистикой */}
      <div
        className="px-2.5 py-1.5 border-t text-[10px]"
        style={{
          borderColor: 'var(--border-default)',
          color: 'var(--text-tertiary)',
          backgroundColor: 'var(--bg-surface-2)',
        }}
      >
        <div>Проектов: 1</div>
        <div>Документов: 287</div>
        <div>Задач: 12</div>
      </div>
    </aside>
  );
}
