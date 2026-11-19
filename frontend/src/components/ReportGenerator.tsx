"use client";

import React, { useState } from "react";
import {
  FileText, Download, CheckCircle2, ShieldCheck, Printer,
  FileSpreadsheet, ArrowDownToLine, Clock, Scale, ShieldAlert
} from "lucide-react";
import { AuditSession, DashboardStats } from "../lib/types";
import { api } from "../lib/api";

interface ReportGeneratorProps {
  activeSession: AuditSession | null;
  stats: DashboardStats | null;
}

export const ReportGenerator: React.FC<ReportGeneratorProps> = ({
  activeSession,
  stats
}) => {
  const [isGenerating, setIsGenerating] = useState(false);

  const sessionId = activeSession?.id || "CURRENT_AUDIT";
  const downloadUrl = api.getReportDownloadUrl(sessionId);

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
            <FileText className="h-6 w-6 text-blue-400" />
            <span>Automated DPDP Audit Report Generator</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Publication-grade PDF compliance artifacts & executive risk summaries
          </p>
        </div>

        {/* Download PDF Trigger */}
        <a
          href={downloadUrl}
          download
          className="flex items-center space-x-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-2.5 text-xs font-bold text-white shadow-lg shadow-blue-500/25 hover:from-blue-500 hover:to-indigo-500 transition-all"
        >
          <ArrowDownToLine className="h-4 w-4" />
          <span>Download Audit PDF Report</span>
        </a>
      </div>

      {/* PDF Report Document Preview Box */}
      <div className="rounded-2xl border border-slate-700 bg-[#0E1626] p-8 space-y-6 shadow-2xl max-w-4xl mx-auto">
        
        {/* Document Header */}
        <div className="flex justify-between items-start border-b border-slate-800 pb-6">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <span className="text-xl font-black text-white">PRIVESCAN AI</span>
              <span className="rounded bg-blue-500/10 px-2 py-0.5 text-[10px] font-bold text-blue-400 border border-blue-500/20">
                OFFICIAL REPORT
              </span>
            </div>
            <p className="text-xs text-slate-400">
              India DPDP Act, 2023 & Rules 2025 Autonomous Compliance Audit
            </p>
          </div>

          <div className="text-right text-xs font-mono text-slate-400 space-y-0.5">
            <div>Session ID: <strong className="text-white">{sessionId}</strong></div>
            <div>Date: <strong className="text-white">{new Date().toLocaleDateString()}</strong></div>
            <div>Status: <span className="text-emerald-400 font-bold">COMPLETED</span></div>
          </div>
        </div>

        {/* Executive Summary Section */}
        <div className="space-y-3">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            1. Executive Audit Summary
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            This document certifies the autonomous discovery and contextual privacy audit executed by the PRIVESCAN AI multi-agent system.
            Granular inspection of document schemas, column labels, and numerical formats was performed to uncover exposed Personal Data and isolate false alarms.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
              <span className="text-[10px] text-slate-500 font-mono block">FILES SCANNED</span>
              <span className="text-lg font-bold text-white">{activeSession?.total_files || stats?.total_files_scanned || 0}</span>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
              <span className="text-[10px] text-slate-500 font-mono block">PII FINDINGS</span>
              <span className="text-lg font-bold text-white">{activeSession?.total_findings || stats?.total_findings || 0}</span>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
              <span className="text-[10px] text-slate-500 font-mono block">CRITICAL / HIGH</span>
              <span className="text-lg font-bold text-red-400">
                {(activeSession?.critical_findings || 0) + (activeSession?.high_findings || 0) || (stats?.high_risk_findings || 0)}
              </span>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
              <span className="text-[10px] text-slate-500 font-mono block">COMPOSITE RISK</span>
              <span className="text-lg font-bold text-purple-400">
                {activeSession?.risk_score || stats?.overall_risk_score || 0} / 100
              </span>
            </div>
          </div>
        </div>

        {/* Sections Highlights */}
        <div className="space-y-4 pt-2 border-t border-slate-800">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            2. Included PDF Report Artifacts
          </h3>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 space-y-1">
              <div className="font-semibold text-blue-300 flex items-center space-x-1.5">
                <CheckCircle2 className="h-4 w-4 text-blue-400" />
                <span>Context Intelligence Deduplication</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Detailed evidence showing how 10-digit Order IDs were distinguished from 10-digit phone numbers.
              </p>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 space-y-1">
              <div className="font-semibold text-emerald-300 flex items-center space-x-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>DPDP Statutory Provisions Alignment</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Mapped against Sections 4, 5, 6, 8(5), 8(7), 12 of India&apos;s DPDP Act 2023 with commencement status.
              </p>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 space-y-1">
              <div className="font-semibold text-purple-300 flex items-center space-x-1.5">
                <CheckCircle2 className="h-4 w-4 text-purple-400" />
                <span>Remediation Proposals & Sign-offs</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Actionable log of generated masked copies, access restrictions, and human administrator approvals.
              </p>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/40 p-3 space-y-1">
              <div className="font-semibold text-amber-300 flex items-center space-x-1.5">
                <CheckCircle2 className="h-4 w-4 text-amber-400" />
                <span>Multi-Agent Execution Audit Trail</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Millisecond-level execution timestamps, tool calls, and node transitions of the LangGraph orchestrator.
              </p>
            </div>
          </div>
        </div>

        {/* Footer Action */}
        <div className="pt-4 border-t border-slate-800 flex justify-between items-center text-xs">
          <span className="text-slate-500 font-mono">Report Engine: ReportLab 5.1.0</span>
          <a
            href={downloadUrl}
            download
            className="flex items-center space-x-1.5 text-blue-400 hover:underline font-bold"
          >
            <span>Click to download full signed PDF</span>
            <Download className="h-4 w-4" />
          </a>
        </div>

      </div>

    </div>
  );
};
