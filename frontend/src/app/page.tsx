"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "../components/Navbar";
import { LandingPage } from "../components/LandingPage";
import { CommandCenter } from "../components/CommandCenter";
import { DocumentScanner } from "../components/DocumentScanner";
import { DataInventoryReport } from "../components/DataInventoryReport";
import { AgentActivity } from "../components/AgentActivity";
import { FindingsExplorer } from "../components/FindingsExplorer";
import { ComplianceCenter } from "../components/ComplianceCenter";
import { RemediationCenter } from "../components/RemediationCenter";
import { ReportGenerator } from "../components/ReportGenerator";
import { ContextTesterModal } from "../components/ContextTesterModal";
import { api } from "../lib/api";
import {
  AuditSession, DashboardStats, PIIFinding,
  ComplianceObservation, RemediationAction, AgentExecution
} from "../lib/types";

export default function Home() {
  const [currentTab, setCurrentTab] = useState<string>("dashboard");
  const [sessions, setSessions] = useState<AuditSession[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string>("");
  const [activeSession, setActiveSession] = useState<AuditSession | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [findings, setFindings] = useState<PIIFinding[]>([]);
  const [complianceObservations, setComplianceObservations] = useState<ComplianceObservation[]>([]);
  const [remediationActions, setRemediationActions] = useState<RemediationAction[]>([]);
  const [agentExecutions, setAgentExecutions] = useState<AgentExecution[]>([]);
  const [isDemoLoading, setIsDemoLoading] = useState<boolean>(false);

  // Load initial sessions & stats
  const refreshAllData = async (targetSessionId?: string) => {
    try {
      const sessionList = await api.listSessions();
      setSessions(sessionList);

      const sessId = targetSessionId || activeSessionId || (sessionList.length > 0 ? sessionList[0].id : "");
      if (sessId) {
        setActiveSessionId(sessId);
        const [
          sessDetails,
          dashboardStats,
          allFindings,
          allCompliance,
          allRemediation,
          allAgents
        ] = await Promise.all([
          api.getSession(sessId).catch(() => null),
          api.getDashboardStats(sessId).catch(() => null),
          api.getFindings({ sessionId: sessId }).catch(() => []),
          api.getComplianceObservations(sessId).catch(() => []),
          api.getRemediationActions(sessId).catch(() => []),
          api.getAgentsStatus(sessId).catch(() => [])
        ]);

        setActiveSession(sessDetails);
        setStats(dashboardStats);
        setFindings(allFindings);
        setComplianceObservations(allCompliance);
        setRemediationActions(allRemediation);
        setAgentExecutions(allAgents);
      } else {
        // No sessions exist yet; fetch general stats
        const generalStats = await api.getDashboardStats().catch(() => null);
        setStats(generalStats);
      }
    } catch (err) {
      console.error("Failed to load audit data:", err);
    }
  };

  useEffect(() => {
    refreshAllData();
  }, []);

  // When active session changes
  useEffect(() => {
    if (activeSessionId) {
      refreshAllData(activeSessionId);
    }
  }, [activeSessionId]);

  // One-Click Demo Audit
  const handleTriggerDemo = async () => {
    try {
      setIsDemoLoading(true);
      const finishedSession = await api.triggerDemoAudit();
      setIsDemoLoading(false);
      await refreshAllData(finishedSession.id);
      setCurrentTab("dashboard");
    } catch (err) {
      console.error("Demo audit failed:", err);
      setIsDemoLoading(false);
    }
  };

  const handleAuditCompleted = (newSession: AuditSession) => {
    refreshAllData(newSession.id);
    setCurrentTab("dashboard");
  };

  return (
    <div className="min-h-screen bg-[#080C16] text-slate-100 flex flex-col font-sans">
      
      {/* Top Navbar */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        sessions={sessions}
        activeSessionId={activeSessionId}
        setActiveSessionId={setActiveSessionId}
        onTriggerDemo={handleTriggerDemo}
        isDemoLoading={isDemoLoading}
      />

      {/* Main Container */}
      <main className="flex-1 mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8 pt-8">
        {currentTab === "landing" && (
          <LandingPage
            onStartAudit={() => setCurrentTab("scanner")}
            onOpenPlayground={() => setCurrentTab("playground")}
          />
        )}

        {currentTab === "dashboard" && (
          <CommandCenter
            stats={stats}
            onNavigateTab={setCurrentTab}
            onTriggerDemo={handleTriggerDemo}
          />
        )}

        {currentTab === "scanner" && (
          <DocumentScanner
            activeSession={activeSession}
            onAuditCompleted={handleAuditCompleted}
            onTriggerDemo={handleTriggerDemo}
            isDemoLoading={isDemoLoading}
          />
        )}

        {currentTab === "inventory" && (
          <DataInventoryReport
            activeSession={activeSession}
          />
        )}

        {currentTab === "agents" && (
          <AgentActivity
            executions={agentExecutions}
            activeSessionId={activeSessionId}
          />
        )}

        {currentTab === "findings" && (
          <FindingsExplorer
            findings={findings}
            activeSessionId={activeSessionId}
          />
        )}

        {currentTab === "compliance" && (
          <ComplianceCenter
            observations={complianceObservations}
            activeSessionId={activeSessionId}
          />
        )}

        {currentTab === "remediation" && (
          <RemediationCenter
            actions={remediationActions}
            activeSessionId={activeSessionId}
            onActionUpdated={() => refreshAllData(activeSessionId)}
          />
        )}

        {currentTab === "reports" && (
          <ReportGenerator
            activeSession={activeSession}
            stats={stats}
          />
        )}

        {currentTab === "playground" && (
          <ContextTesterModal />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#060911] py-6 text-xs text-slate-500 font-mono">
        <div className="mx-auto max-w-7xl px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
          <div>
            PRIVESCAN AI © 2026 | Built for Agentic AI Hackathon | India DPDP Act, 2023 Compliance
          </div>
          <div className="flex items-center space-x-4 text-slate-400">
            <span>LangGraph Multi-Agent</span>
            <span>•</span>
            <span>Gemini AI & Hybrid Engine</span>
            <span>•</span>
            <span>FastAPI + Next.js</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
