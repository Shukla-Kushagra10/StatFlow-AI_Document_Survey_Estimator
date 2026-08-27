import React from 'react';
import { 
  LayoutDashboard, 
  UploadCloud, 
  CheckCircle2, 
  Sparkles, 
  Sliders, 
  AlertTriangle, 
  FileText, 
  History, 
  Scale 
} from 'lucide-react';

export default function Sidebar({ currentTab, setCurrentTab }) {
  const menuItems = [
    { id: 'dashboard', label: 'Overview & Profile', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload & Ingest', icon: UploadCloud },
    { id: 'clean', label: 'Clean & Impute', icon: Sparkles },
    { id: 'validate', label: 'Rule Validation', icon: CheckCircle2 },
    { id: 'outliers', label: 'Outlier Detection', icon: AlertTriangle },
    { id: 'weighting', label: 'Survey Weighting', icon: Scale },
    { id: 'estimation', label: 'Estimation & MoE', icon: Sliders },
    { id: 'reports', label: 'Official Release Report', icon: FileText },
    { id: 'audit', label: 'Audit Trail', icon: History }
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between shrink-0 min-h-[calc(100vh-65px)]">
      <nav className="p-4 space-y-1.5">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 px-3 py-2">
          Processing Pipeline
        </div>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-sky-600 text-white shadow-sm shadow-sky-900/50'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-slate-800/80 text-xs text-slate-400">
        <p className="font-semibold text-slate-300">MoSPI Statathon 2025</p>
        <p className="text-[11px] text-slate-400 mt-0.5">Problem Statement ID: PS-4</p>
      </div>
    </aside>
  );
}