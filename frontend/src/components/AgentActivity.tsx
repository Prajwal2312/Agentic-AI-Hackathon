"use client";

import React, { useState } from "react";
import {
  Cpu, CheckCircle2, Clock, AlertTriangle, ChevronDown, ChevronRight,
  Database, Eye, ShieldAlert, Scale, Lock, RefreshCw, Terminal, Layers
} from "lucide-react";
import { AgentExecution } from "../lib/types";

interface AgentActivityProps {
  executions: AgentExecution[];
  activeSessionId: string;
}

export const AgentActivity: React.FC<AgentActivityProps> = ({
  executions,
  activeSessionId
}) => {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  const agentIcons: Record<string, any> = {
    "Discovery Agent": Database,
    "Context Intelligence Agent": Eye,
    "Context Intelligence Agent (Deep Verification)": Eye,
    "Risk Assessment Agent": AlertTriangle,
    "DPDP Compliance Agent": Scale,
    "Remediation Agent": Lock,
    "Orchestrator Agent": Layers
  };

  const agentColors: Record<string, string> = {
    "Discovery Agent": "text-blue-400 border-blue-500/30 bg-blue-500/10",
    "Context Intelligence Agent": "text-purple-400 border-purple-500/30 bg-purple-500/10",
    "Context Intelligence Agent (Deep Verification)": "text-indigo-400 border-indigo-500/30 bg-indigo-500/10",
    "Risk Assessment Agent": "text-amber-400 border-amber-500/30 bg-amber-500/10",
    "DPDP Compliance Agent": "text-emerald-400 border-emerald-500/30 bg-emerald-500/10",
    "Remediation Agent": "text-cyan-400 border-cyan-500/30 bg-cyan-500/10",
    "Orchestrator Agent": "text-violet-400 border-violet-500/30 bg-violet-500/10"
  };

  const toggleLogs = (name: string) => {
    setExpandedAgent(expandedAgent === name ? null : name);
  };

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
            <Cpu className="h-6 w-6 text-purple-400" />
            <span>Agent Activity Center</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            LangGraph StateGraph Execution | 5 Specialised Autonomous Agents & Conditional Gate
          </p>
        </div>

        <div className="flex items-center space-x-2 rounded-lg border border-slate-800 bg-slate-900/80 px-3 py-1.5 text-xs font-mono text-slate-300">
          <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping mr-1"></span>
          <span>Session: {activeSessionId || "All Sessions"}</span>
        </div>
      </div>

      {/* Visual LangGraph Workflow Timeline */}
      <div className="rounded-xl border border-slate-800 bg-[#0E1626]/70 p-6 space-y-4">
        <h3 className="text-sm font-bold text-white flex items-center space-x-2">
          <Layers className="h-4 w-4 text-blue-400" />
          <span>Orchestrator Workflow Topology & Conditional Transitions</span>
        </h3>

        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <div className="rounded-lg border border-slate-700 bg-slate-900/80 px-3 py-2 text-slate-300">
            START: Receive Audit
          </div>
          <span className="text-slate-500 font-bold">→</span>

          <div className="rounded-lg border border-blue-500/30 bg-blue-500/10 px-3 py-2 text-blue-400 font-semibold">
            1. Discovery Node
          </div>
          <span className="text-slate-500 font-bold">→</span>

          <div className="rounded-lg border border-purple-500/30 bg-purple-500/10 px-3 py-2 text-purple-400 font-semibold">
            2. Context Agent
          </div>
          <span className="text-slate-500 font-bold">→</span>

          {/* Conditional Decision Diamond */}
          <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-amber-300 font-bold flex items-center space-x-1.5">
            <span className="text-amber-400">◇</span>
            <span>Verification Gate</span>
          </div>
          <span className="text-slate-500 font-bold">→</span>

          <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-2 text-amber-400 font-semibold">
            3. Risk Node
          </div>
          <span className="text-slate-500 font-bold">→</span>

          <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-emerald-400 font-semibold">
            4. DPDP Compliance
          </div>
          <span className="text-slate-500 font-bold">→</span>

          <div className="rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-3 py-2 text-cyan-400 font-semibold">
            5. Remediation Plan
          </div>
          <span className="text-slate-500 font-bold">→</span>

          <div className="rounded-lg border border-emerald-500/40 bg-emerald-500/20 px-3 py-2 text-emerald-300 font-bold">
            FINISH: Audit Log
          </div>
        </div>
      </div>

      {/* Agents Execution Cards */}
      <div className="space-y-4">
        {executions.length > 0 ? (
          executions.map((ag) => {
            const Icon = agentIcons[ag.agent_name] || Cpu;
            const colorClass = agentColors[ag.agent_name] || "text-slate-400 border-slate-700 bg-slate-800";
            const isExpanded = expandedAgent === ag.agent_name;

            let parsedLogs: string[] = [];
            if (ag.logs_json) {
              try {
                parsedLogs = JSON.parse(ag.logs_json);
              } catch {
                parsedLogs = [ag.logs_json];
              }
            }

            return (
              <div
                key={ag.id}
                className="rounded-xl border border-slate-800 bg-[#0E1626]/80 transition-all hover:border-slate-700"
              >
                {/* Header Row */}
                <div
                  onClick={() => toggleLogs(ag.agent_name)}
                  className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-5 cursor-pointer gap-4"
                >
                  <div className="flex items-center space-x-3.5">
                    <div className={`h-10 w-10 rounded-xl flex items-center justify-center border ${colorClass}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-white flex items-center space-x-2">
                        <span>{ag.agent_name}</span>
                        <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
                          {ag.status}
                        </span>
                      </h4>
                      <p className="text-xs text-slate-400 mt-0.5">
                        {ag.task_description || "Autonomous processing task"}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-6 text-xs text-slate-400 font-mono">
                    <div className="text-right">
                      <span className="text-slate-500 block text-[10px]">EXECUTION TIME</span>
                      <span className="text-white font-bold">{ag.execution_duration_ms} ms</span>
                    </div>

                    <div className="text-right">
                      <span className="text-slate-500 block text-[10px]">ITEMS PROCESSED</span>
                      <span className="text-white font-bold">{ag.findings_count}</span>
                    </div>

                    <div className="text-slate-400 hover:text-white">
                      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    </div>
                  </div>
                </div>

                {/* Expandable Execution Logs Drawer */}
                {isExpanded && (
                  <div className="border-t border-slate-800/80 bg-slate-950/70 p-5 font-mono text-xs text-slate-300 space-y-2">
                    <div className="flex items-center justify-between text-slate-500 pb-2 border-b border-slate-800/60">
                      <span className="flex items-center space-x-1.5">
                        <Terminal className="h-3.5 w-3.5 text-blue-400" />
                        <span>Execution Event Logs ({parsedLogs.length} events)</span>
                      </span>
                      <span>Agent ID: #{ag.id}</span>
                    </div>
                    <div className="space-y-1.5 max-h-56 overflow-y-auto pt-1">
                      {parsedLogs.length > 0 ? (
                        parsedLogs.map((logStr, lIdx) => (
                          <div key={lIdx} className="text-[11px] leading-relaxed flex items-start space-x-2">
                            <span className="text-blue-500 select-none">›</span>
                            <span>{logStr}</span>
                          </div>
                        ))
                      ) : (
                        <div className="text-slate-500">No log details recorded.</div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            );
          })
        ) : (
          <div className="rounded-xl border border-slate-800 bg-[#0E1626]/50 p-10 text-center space-y-3">
            <Cpu className="h-8 w-8 text-slate-600 mx-auto" />
            <h4 className="text-sm font-semibold text-slate-300">No Agent Executions Yet</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Execute an audit from the Scanner or trigger the benchmark demo to view real agent activity.
            </p>
          </div>
        )}
      </div>

    </div>
  );
};
