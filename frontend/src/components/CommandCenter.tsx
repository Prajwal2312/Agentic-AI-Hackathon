"use client";

import React from "react";
import {
  FileCheck, ShieldAlert, AlertTriangle, HelpCircle, Layers,
  Activity, ArrowUpRight, Clock, ShieldCheck, CheckCircle2,
  FileSpreadsheet, FileText, Database, Shield
} from "lucide-react";
import {
  PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar,
  XAxis, YAxis, Tooltip, Legend
} from "recharts";
import { DashboardStats } from "../lib/types";

interface CommandCenterProps {
  stats: DashboardStats | null;
  onNavigateTab: (tab: string) => void;
  onTriggerDemo: () => void;
}

export const CommandCenter: React.FC<CommandCenterProps> = ({
  stats,
  onNavigateTab,
  onTriggerDemo
}) => {
  if (!stats) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center space-y-3">
          <Activity className="h-8 w-8 animate-spin text-blue-500 mx-auto" />
          <p className="text-sm text-slate-400">Loading Privacy Command Center telemetry...</p>
        </div>
      </div>
    );
  }

  // Formatting for Recharts
  const piiData = Object.entries(stats.pii_categories_distribution || {}).map(([name, count]) => ({
    name: name.replace("_", " "),
    count
  }));

  const riskData = [
    { name: "Critical", value: stats.risk_severity_distribution?.CRITICAL || 0, color: "#EF4444" },
    { name: "High", value: stats.risk_severity_distribution?.HIGH || 0, color: "#F97316" },
    { name: "Medium", value: stats.risk_severity_distribution?.MEDIUM || 0, color: "#FBBF24" },
    { name: "Low", value: stats.risk_severity_distribution?.LOW || 0, color: "#10B981" }
  ].filter(d => d.value > 0);

  const fileTypeData = Object.entries(stats.files_by_type || {}).map(([type, count]) => ({
    type,
    files: count,
    findings: stats.findings_by_file_type?.[type] || 0
  }));

  return (
    <div className="space-y-8 pb-12">
      
      {/* Top Header Banner */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
            <Activity className="h-6 w-6 text-blue-400" />
            <span>Privacy Command Center</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Autonomous audit telemetry | Live DPDP compliance & exposure posture
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onNavigateTab("scanner")}
            className="rounded-lg bg-blue-600/20 border border-blue-500/30 px-3.5 py-1.5 text-xs font-semibold text-blue-400 hover:bg-blue-600/30 transition-all"
          >
            + Upload New Files
          </button>
          <button
            onClick={() => onNavigateTab("reports")}
            className="rounded-lg bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-700 transition-all"
          >
            Export PDF Report
          </button>
        </div>
      </div>

      {/* Primary Metric KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        
        {/* Total Files */}
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/80 p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Scanned Files</span>
            <FileSpreadsheet className="h-4 w-4 text-blue-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats.total_files_scanned}</div>
          <div className="text-[10px] text-emerald-400 flex items-center space-x-1">
            <span>{stats.audit_completion_percentage}% processed</span>
          </div>
        </div>

        {/* Total Findings */}
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/80 p-4 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">PII Discovered</span>
            <Database className="h-4 w-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{stats.total_findings}</div>
          <div className="text-[10px] text-slate-400">Context verified</div>
        </div>

        {/* High Risk Findings */}
        <div className="rounded-xl border border-red-500/20 bg-red-950/20 p-4 space-y-2">
          <div className="flex items-center justify-between text-red-300">
            <span className="text-xs font-medium">High / Critical</span>
            <ShieldAlert className="h-4 w-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold text-red-400">{stats.high_risk_findings}</div>
          <div className="text-[10px] text-red-300">Requires safeguarding</div>
        </div>

        {/* Ambiguous Detections */}
        <div className="rounded-xl border border-amber-500/20 bg-amber-950/20 p-4 space-y-2">
          <div className="flex items-center justify-between text-amber-300">
            <span className="text-xs font-medium">Ambiguous Items</span>
            <HelpCircle className="h-4 w-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">{stats.ambiguous_detections}</div>
          <div className="text-[10px] text-amber-300">Human verified</div>
        </div>

        {/* Requiring Remediation */}
        <div className="rounded-xl border border-cyan-500/20 bg-cyan-950/20 p-4 space-y-2">
          <div className="flex items-center justify-between text-cyan-300">
            <span className="text-xs font-medium">Remediation Queue</span>
            <FileCheck className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-400">{stats.files_requiring_remediation}</div>
          <div className="text-[10px] text-cyan-300">Masking proposals</div>
        </div>

        {/* Composite Risk Score */}
        <div className="rounded-xl border border-purple-500/20 bg-purple-950/20 p-4 space-y-2">
          <div className="flex items-center justify-between text-purple-300">
            <span className="text-xs font-medium">Risk Score</span>
            <Shield className="h-4 w-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-purple-400">{stats.overall_risk_score} <span className="text-xs font-normal text-slate-400">/ 100</span></div>
          <div className="text-[10px] text-purple-300">Weighted exposure</div>
        </div>

      </div>

      {/* Visual Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Chart 1: PII Category Distribution */}
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/70 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">Discovered PII Categories</h3>
            <span className="text-[10px] font-mono text-slate-400">Total: {stats.total_findings}</span>
          </div>
          <div className="h-56 w-full">
            {piiData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={piiData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="name" stroke="#64748B" fontSize={10} angle={-25} textAnchor="end" />
                  <YAxis stroke="#64748B" fontSize={10} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0F172A", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                    labelStyle={{ color: "#F8FAFC" }}
                  />
                  <Bar dataKey="count" fill="#38BDF8" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-slate-400">
                Run an audit to view PII distribution.
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Risk Severity Distribution */}
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/70 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">Risk Severity Distribution</h3>
            <span className="text-[10px] font-mono text-slate-400">By impact score</span>
          </div>
          <div className="h-56 w-full flex items-center justify-center">
            {riskData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={riskData}
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={70}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0F172A", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px", paddingTop: "10px" }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-slate-400">No risk distribution data yet.</div>
            )}
          </div>
        </div>

        {/* Chart 3: Files & Findings by File Type */}
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/70 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">Exposure by File Format</h3>
            <span className="text-[10px] font-mono text-slate-400">PDF, XLSX, CSV, DOCX</span>
          </div>
          <div className="h-56 w-full">
            {fileTypeData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={fileTypeData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <XAxis dataKey="type" stroke="#64748B" fontSize={10} />
                  <YAxis stroke="#64748B" fontSize={10} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0F172A", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                  />
                  <Legend wrapperStyle={{ fontSize: "11px" }} />
                  <Bar dataKey="files" fill="#818CF8" name="Files Count" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="findings" fill="#F43F5E" name="PII Findings" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-full items-center justify-center text-xs text-slate-400">
                No file format metrics available.
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Bottom Grid: Agent Status & Recent Audit Activity Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Agent Activity Status Cards */}
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/70 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Autonomous Agents Status</span>
            </h3>
            <button
              onClick={() => onNavigateTab("agents")}
              className="text-xs text-blue-400 hover:underline flex items-center space-x-1"
            >
              <span>View Hub</span>
              <ArrowUpRight className="h-3 w-3" />
            </button>
          </div>

          <div className="space-y-2.5">
            {stats.agent_statuses && stats.agent_statuses.length > 0 ? (
              stats.agent_statuses.slice(0, 5).map((ag, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg border border-slate-800/80 bg-slate-900/60 p-2.5 text-xs">
                  <div className="space-y-0.5">
                    <div className="font-semibold text-slate-200">{ag.agent_name}</div>
                    <div className="text-[11px] text-slate-400 truncate max-w-xs">{ag.task_description}</div>
                  </div>
                  <div className="text-right">
                    <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/20">
                      {ag.status}
                    </span>
                    <div className="text-[10px] font-mono text-slate-500 mt-1">{ag.execution_duration_ms} ms</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 py-4 text-center">
                Agents are standby. Run a scan to initiate autonomous execution.
              </div>
            )}
          </div>
        </div>

        {/* Audit Log Activity Stream */}
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/70 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Clock className="h-4 w-4 text-indigo-400" />
              <span>Recent Audit Events Log</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Immutable ledger</span>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {stats.recent_activity && stats.recent_activity.length > 0 ? (
              stats.recent_activity.slice(0, 6).map((log, i) => (
                <div key={i} className="rounded-lg border border-slate-800/60 bg-slate-900/40 p-2.5 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-blue-300">{log.agent_name}</span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-300 leading-snug">{log.details}</p>
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 py-4 text-center">
                No recent activity logged yet.
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
};
