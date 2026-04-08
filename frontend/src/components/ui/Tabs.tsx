import React, { useState } from 'react';

interface TabProps {
  label: string;
  icon?: React.ElementType;
  content: React.ReactNode;
}

interface TabsProps {
  tabs: TabProps[];
  initialTab?: string;
}

export default function Tabs({ tabs, initialTab }: TabsProps) {
  const [activeTab, setActiveTab] = useState(initialTab || (tabs.length > 0 ? tabs[0].label : ''));

  return (
    <div className="w-full">
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.label}
              onClick={() => setActiveTab(tab.label)}
              className={`inline-flex items-center gap-2 px-1 py-4 text-sm font-medium border-b-2 transition-colors duration-200 ease-in-out
                ${activeTab === tab.label
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              {tab.icon && <tab.icon size={16} />}
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </div>
      <div className="py-6">
        {tabs.find((tab) => tab.label === activeTab)?.content}
      </div>
    </div>
  );
}
