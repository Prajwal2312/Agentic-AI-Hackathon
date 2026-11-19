"use client";

import React from "react";
import {
  ShieldAlert, Activity, FileText, Database, ShieldCheck,
  FileCheck, Cpu, Sliders, Play, RefreshCw, Layers, ClipboardList
} from "lucide-react";
import { AuditSession } from "../lib/types";

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  sessions: AuditSession[];
  activeSessionId: string;
  setActiveSessionId: (id: string) => void;
  onTriggerDemo: () => void;
  isDemoLoading: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  setCurrentTab,
  sessions,
  activeSessionId,
  setActiveSessionId,
  onTriggerDemo,
  isDemoLoading
}) => {
  const navTabs = [
    { id: "landing", label: "Overview", icon: Layers },
    { id: "dashboard", label: "Command Center", icon: Activity },
    { id: "scanner", label: "Scanner", icon: Database },
    { id: "inventory", label: "Data Inventory", icon: ClipboardList },
    { id: "agents", label: "Multi-Agent Hub", icon: Cpu },
    { id: "findings", label: "Findings", icon: ShieldAlert },
    { id: "compliance", label: "DPDP Compliance", icon: ShieldCheck },
    { id: "remediation", label: "Remediation", icon: FileCheck },
    { id: "reports", label: "Audit Reports", icon: FileText },
    { id: "playground", label: "Context Engine", icon: Sliders },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-[#080C16]/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        
        {/* Brand Logo */}
        <div 
          onClick={() => setCurrentTab("landing")}
          className="flex cursor-pointer items-center space-x-3 transition-transform hover:scale-105"
        >
          <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 p-0.5 shadow-lg shadow-blue-500/20">
            <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-[#0A0F1D]">
              <ShieldCheck className="h-5 w-5 text-blue-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-black tracking-wider text-white">
                PRIVE<span className="text-blue-400">SCAN</span>
              </span>
              <span className="rounded bg-blue-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-blue-400 border border-blue-500/20">
                AI 2.0
              </span>
            </div>
            <p className="text-[10px] tracking-tight text-slate-400 font-mono">
              DPDP Compliance & Discovery
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden lg:flex items-center space-x-1">
          {navTabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setCurrentTab(tab.id)}
                className={`flex items-center space-x-1.5 rounded-lg px-3 py-1.5 text-xs font-medium transition-all ${
                  isActive
                    ? "bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm shadow-blue-500/10"
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isActive ? "text-blue-400" : "text-slate-400"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Action Controls: Session Selector & Run Demo */}
        <div className="flex items-center space-x-3">
          {/* Active Session Dropdown */}
          {sessions.length > 0 && (
            <div className="hidden sm:flex items-center space-x-1.5 rounded-lg border border-slate-800 bg-slate-900/80 px-2 py-1">
              <span className="text-[10px] font-mono text-slate-400">Session:</span>
              <select
                value={activeSessionId}
                onChange={(e) => setActiveSessionId(e.target.value)}
                className="bg-transparent text-xs font-semibold text-blue-400 focus:outline-none cursor-pointer"
              >
                {sessions.map((s) => (
                  <option key={s.id} value={s.id} className="bg-slate-900 text-slate-200">
                    {s.id} ({s.status})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Quick Demo Trigger Button */}
          <button
            onClick={onTriggerDemo}
            disabled={isDemoLoading}
            className="flex items-center space-x-2 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-md shadow-blue-500/25 transition-all hover:from-blue-500 hover:to-indigo-500 hover:shadow-lg disabled:opacity-50"
          >
            {isDemoLoading ? (
              <>
                <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                <span>Running Audit...</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>Run Demo Audit</span>
              </>
            )}
          </button>
        </div>

      </div>

      {/* Mobile Tab Scroller */}
      <div className="flex lg:hidden overflow-x-auto px-4 py-2 border-t border-slate-800/60 bg-[#0A0F1D] space-x-2">
        {navTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setCurrentTab(tab.id)}
              className={`flex items-center space-x-1.5 whitespace-nowrap rounded-lg px-2.5 py-1 text-xs font-medium transition-all ${
                isActive
                  ? "bg-blue-600/20 text-blue-400 border border-blue-500/30"
                  : "text-slate-400 hover:bg-slate-800/60"
              }`}
            >
              <Icon className="h-3.5 w-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};
