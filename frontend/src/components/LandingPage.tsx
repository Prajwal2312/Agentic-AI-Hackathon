"use client";

import React from "react";
import {
  ShieldCheck, ShieldAlert, Cpu, Eye, FileSpreadsheet, Lock, ArrowRight,
  CheckCircle2, Sparkles, Scale, AlertTriangle, Layers, Database, FileText
} from "lucide-react";

interface LandingPageProps {
  onStartAudit: () => void;
  onOpenPlayground: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onStartAudit, onOpenPlayground }) => {
  return (
    <div className="space-y-16 pb-16">
      
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 text-center">
        {/* Ambient Gradient Background Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-blue-600/15 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-1/3 left-1/3 w-[300px] h-[250px] bg-purple-600/10 rounded-full blur-[100px] pointer-events-none" />

        <div className="relative mx-auto max-w-4xl px-4">
          
          {/* Badge */}
          <div className="inline-flex items-center space-x-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-xs font-semibold text-blue-400 mb-6 backdrop-blur-md">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Autonomous Multi-Agent DPDP Compliance Auditor</span>
          </div>

          {/* Heading */}
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-6xl sm:leading-tight">
            Discover. Understand. <br />
            <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Protect Personal Data.
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mx-auto mt-6 max-w-2xl text-base text-slate-300 sm:text-lg leading-relaxed">
            Organisations store sensitive personal records across shared drives, emails, and legacy exports without visibility.
            India&apos;s <span className="text-white font-medium">Digital Personal Data Protection Act, 2023</span> imposes statutory penalties up to ₹250 Crores.
            PRIVESCAN AI autonomously uncovers data, verifies context, evaluates exposure risk, and automates remediation.
          </p>

          {/* CTAs */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={onStartAudit}
              className="flex items-center space-x-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-blue-500/25 transition-all hover:from-blue-500 hover:to-indigo-500 hover:scale-105"
            >
              <span>Launch Privacy Audit</span>
              <ArrowRight className="h-4 w-4" />
            </button>
            <button
              onClick={onOpenPlayground}
              className="flex items-center space-x-2 rounded-xl border border-slate-700 bg-slate-900/60 px-6 py-3.5 text-sm font-semibold text-slate-200 backdrop-blur-md transition-all hover:bg-slate-800 hover:border-slate-600"
            >
              <Cpu className="h-4 w-4 text-blue-400" />
              <span>Test Context Engine (Order ID vs Phone)</span>
            </button>
          </div>

        </div>
      </section>

      {/* Primary Differentiator Card: Context Intelligence */}
      <section className="mx-auto max-w-6xl px-4">
        <div className="rounded-2xl border border-blue-500/30 bg-gradient-to-b from-[#0F172A] to-[#0A0F1D] p-6 sm:p-10 shadow-2xl relative overflow-hidden">
          <div className="absolute -top-12 -right-12 h-48 w-48 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />
          
          <div className="flex flex-col lg:flex-row gap-8 items-center">
            <div className="lg:w-1/2 space-y-4">
              <span className="text-xs font-mono font-bold tracking-wider uppercase text-blue-400">
                Core Differentiator
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-white leading-snug">
                Why Regex & Traditional PII Scanners Fail
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                Traditional tools rely on rigid regex patterns. When an order management system stores an Order ID like{" "}
                <code className="text-amber-300 font-mono bg-slate-800/80 px-1 py-0.5 rounded">9876543210</code>, pattern tools raise a false-alarm for a personal phone number.
              </p>
              <p className="text-sm text-slate-300 leading-relaxed">
                <span className="text-blue-400 font-semibold">PRIVESCAN AI</span> investigates column semantics, nearby field relationships, document schemas, and LLM reasoning to distinguish true personal identities from operational numbers.
              </p>
            </div>

            {/* Visual Comparison Box */}
            <div className="lg:w-1/2 w-full space-y-3 font-mono text-xs">
              {/* Item 1: Order ID */}
              <div className="rounded-xl border border-emerald-500/30 bg-emerald-950/20 p-4">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span>Column: <strong className="text-white">Order_ID</strong></span>
                  <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-emerald-400 text-[10px] font-bold">
                    NON-PERSONAL IDENTIFIER (0.98)
                  </span>
                </div>
                <div className="text-slate-200 text-sm">Value: &quot;9876543210&quot;</div>
                <p className="mt-2 text-[11px] text-emerald-300 font-sans">
                  ✓ Resolved: Column header and transactional structure confirm an operational order reference. False alarm averted!
                </p>
              </div>

              {/* Item 2: Mobile Number */}
              <div className="rounded-xl border border-red-500/30 bg-red-950/20 p-4">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span>Column: <strong className="text-white">Mobile_Number</strong></span>
                  <span className="rounded bg-red-500/20 px-2 py-0.5 text-red-400 text-[10px] font-bold">
                    CONFIRMED PERSONAL DATA (0.97)
                  </span>
                </div>
                <div className="text-slate-200 text-sm">Value: &quot;9876543210&quot;</div>
                <p className="mt-2 text-[11px] text-red-300 font-sans">
                  ⚠️ Confirmed: Mobile series prefix, customer master context, and identity attributes confirm individual PII.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Multi-Agent Architecture Section */}
      <section className="mx-auto max-w-6xl px-4">
        <div className="text-center space-y-3 mb-12">
          <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-purple-400">
            Autonomous Collaboration
          </h2>
          <h3 className="text-3xl font-bold text-white">
            5 Specialised Autonomous AI Agents
          </h3>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            Orchestrated via LangGraph with shared agent state, conditional decision boundaries, and human-in-the-loop governance.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Agent 1 */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-3 hover:border-blue-500/30 transition-all">
            <div className="h-10 w-10 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20">
              <Database className="h-5 w-5" />
            </div>
            <h4 className="text-lg font-bold text-white">1. Discovery Agent</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Recursively parses PDF, DOCX, XLSX, CSV, and TXT files. Extracts layout schemas, table structures, and candidate text tokens.
            </p>
          </div>

          {/* Agent 2 */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-3 hover:border-purple-500/30 transition-all">
            <div className="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400 border border-purple-500/20">
              <Eye className="h-5 w-5" />
            </div>
            <h4 className="text-lg font-bold text-white">2. Context Intelligence Agent</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Examines column headers, data types, and surrounding text. Segregates personal data from misleading system identifiers.
            </p>
          </div>

          {/* Agent 3 */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-3 hover:border-amber-500/30 transition-all">
            <div className="h-10 w-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400 border border-amber-500/20">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <h4 className="text-lg font-bold text-white">3. Risk Assessment Agent</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Computes a 0–100 privacy risk score. Evaluates statutory sensitivity, volume concentration, and storage exposure multipliers.
            </p>
          </div>

          {/* Agent 4 */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-3 hover:border-emerald-500/30 transition-all">
            <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 border border-emerald-500/20">
              <Scale className="h-5 w-5" />
            </div>
            <h4 className="text-lg font-bold text-white">4. DPDP Compliance Agent</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Curated legal knowledge base mapping findings to Sections 4, 5, 6, 8(5), 8(7), 12 of India&apos;s DPDP Act 2023 and Rules 2025.
            </p>
          </div>

          {/* Agent 5 */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-3 hover:border-cyan-500/30 transition-all">
            <div className="h-10 w-10 rounded-lg bg-cyan-500/10 flex items-center justify-center text-cyan-400 border border-cyan-500/20">
              <Lock className="h-5 w-5" />
            </div>
            <h4 className="text-lg font-bold text-white">5. Remediation Agent</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Generates genuine masked document copies without modifying original files. Proposes access restrictions and retention reviews.
            </p>
          </div>

          {/* Orchestrator */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-6 space-y-3 hover:border-indigo-500/30 transition-all">
            <div className="h-10 w-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 border border-indigo-500/20">
              <Layers className="h-5 w-5" />
            </div>
            <h4 className="text-lg font-bold text-white">LangGraph Orchestrator</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              Coordinates autonomous flow with conditional verification gates for ambiguous candidates and complete audit trail persistence.
            </p>
          </div>

        </div>
      </section>

      {/* DPDP Act Pillars Section */}
      <section className="mx-auto max-w-6xl px-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-8 sm:p-10">
          <div className="max-w-2xl mb-8">
            <span className="text-xs font-mono font-bold text-blue-400 uppercase">
              Regulatory Alignment
            </span>
            <h3 className="text-2xl font-bold text-white mt-1">
              India&apos;s Digital Personal Data Protection Act, 2023
            </h3>
            <p className="text-xs text-slate-400 mt-2">
              Verifiable statutory knowledge base ensuring accurate legal mapping without hallucinations.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
            <div className="space-y-2 border-l-2 border-blue-500 pl-4">
              <h5 className="font-bold text-white text-sm">Section 8(5) - Reasonable Safeguards</h5>
              <p className="text-slate-300 leading-relaxed">
                Mandates technical & organizational safeguards to prevent personal data breaches. Penalties up to ₹250 Crores in Schedule 1.
              </p>
            </div>
            <div className="space-y-2 border-l-2 border-purple-500 pl-4">
              <h5 className="font-bold text-white text-sm">Section 8(7) - Storage Limitation</h5>
              <p className="text-slate-300 leading-relaxed">
                Cease retention as soon as specified purpose is fulfilled. Historical exports and unmonitored backups require retention reviews.
              </p>
            </div>
            <div className="space-y-2 border-l-2 border-emerald-500 pl-4">
              <h5 className="font-bold text-white text-sm">Section 12 - Right to Erasure</h5>
              <p className="text-slate-300 leading-relaxed">
                Data Principals have statutory rights to correction and erasure. Requires centralized visibility over all unindexed files.
              </p>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};
