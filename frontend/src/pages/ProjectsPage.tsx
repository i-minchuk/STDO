import { WorkspaceLayout, ExplorerSidebar, InspectorPanel, BottomPanel, EditorArea, useWorkspaceStore } from '../components/workspace';
import { FileText } from 'lucide-react';
import { useState } from 'react';

export default function ProjectsPage() {
  const { addTab } = useWorkspaceStore();
  const [selectedRemark, setSelectedRemark] = useState<any>(null);

  const handleNewTab = () => {
    addTab({
      id: `new-doc-${Date.now()}`,
      type: 'document',
      title: 'Новый документ',
      subtitle: 'Черновик',
      icon: <FileText size={14} />,
      isDirty: true,
    });
  };

  const documentData = {
    code: 'КМ1-А01',
    revision: 'B02',
    status: 'approved' as const,
    author: 'Иванов А.В.',
    reviewer: 'Петров С.К.',
    approver: 'Сидоров В.М.',
    releaseDate: '2025-01-15',
    nextDeadline: '2025-04-15',
    dependencies: ['КМ1-А00'],
    totalRemarks: 3,
    openRemarks: 1,
  };

  return (
    <WorkspaceLayout
      explorer={<ExplorerSidebar />}
      inspector={<InspectorPanel selectedRemark={selectedRemark} onSelectRemark={setSelectedRemark} />}
      bottomPanel={<BottomPanel />}
      documentData={documentData}
      onNewTab={handleNewTab}
    >
      <EditorArea />
    </WorkspaceLayout>
  );
}
