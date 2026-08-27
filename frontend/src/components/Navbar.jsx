import React from 'react';
import { Database, ShieldCheck, BarChart3 } from 'lucide-react';

export default function Navbar({ activeDataset }) {
  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center space-x-3">
        <div className="bg-sky-500 p-2 rounded-lg text-slate-950 font-bold">
          <BarChart3 className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold tracking-wide">MoSPI StatEngine PS-4</h1>
          <p className="text-xs text-slate-400">Automated Survey Preparation, Weighting & Reporting</p>
        </div>
      </div>
      
      {activeDataset ? (
        <div className="flex items-center space-x-4 bg-slate-800/80 px-4 py-2 rounded-lg border border-slate-700">
          <Database className="w-4 h-4 text-sky-400" />
          <div className="text-xs">
            <span className="text-slate-400">Active File: </span>
            <span className="font-semibold text-slate-100">{activeDataset.filename}</span>
          </div>
          <span className="bg-sky-950 text-sky-300 border border-sky-800 text-[10px] px-2 py-0.5 rounded font-mono font-medium">
            {activeDataset.status}
          </span>
        </div>
      ) : (
        <div className="flex items-center text-xs text-amber-300 bg-amber-950/40 border border-amber-800/50 px-3 py-1.5 rounded-md">
          <ShieldCheck className="w-4 h-4 mr-1.5" /> Demo / Live Mode Ready
        </div>
      )}
    </header>
  );
}