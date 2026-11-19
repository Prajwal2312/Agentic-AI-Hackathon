"use client";

import React, { useState } from "react";
import {
  Scale, ShieldCheck, AlertTriangle, FileText, CheckCircle2,
  ExternalLink, Info, Filter, ArrowUpRight
} from "lucide-react";
import { ComplianceObservation } from "../lib/types";

interface ComplianceCenterProps {
  observations: ComplianceObservation[];
  activeSessionId: string;
}

export const ComplianceCenter: React.FC<ComplianceCenterProps> = ({
  observations,
  activeSessionId
}) => {
  const [severityFilter, setSeverityFilter] = useState("ALL");

  const filtered = observations.filter(
    (obs) => severityFilter === "ALL" || obs.severity === severityFilter
  );

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "COMMENCED":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "PHASED_COMMENCEMENT":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      case "DRAFT_RULES_2025":
        return "bg-purple-500/20 text-purple-400 border-purple-500/30";
      default:
        return "bg-slate-700 text-slate-300";
    }
  };

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case "CRITICAL":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      case "HIGH":
        return "bg-orange-500/20 text-orange-400 border-orange-500/30";
      case "MEDIUM":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      default:
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    }
  };

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
            <Scale className="h-6 w-6 text-emerald-400" />
            <span>DPDP Statutory Compliance Center</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            India&apos;s Digital Personal Data Protection Act, 2023 & Draft DPDP Rules, 2025
          </p>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-400 font-mono">Filter Severity:</span>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="rounded-lg border border-slate-800 bg-slate-900/90 px-3 py-1.5 text-xs text-slate-200 focus:border-emerald-500 focus:outline-none"
          >
            <option value="ALL">All Observations ({observations.length})</option>
            <option value="CRITICAL">Critical Severity</option>
            <option value="HIGH">High Severity</option>
            <option value="MEDIUM">Medium Severity</option>
            <option value="LOW">Low Severity</option>
          </select>
        </div>
      </div>

      {/* Statutory Knowledge-Base Reference Summary Banner */}
      <div className="rounded-2xl border border-emerald-500/30 bg-emerald-950/20 p-6 space-y-4">
        <div className="flex items-start space-x-3">
          <ShieldCheck className="h-6 w-6 text-emerald-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-white">
              Verifiable Legal Baseline: DPDPA 2023 & Rules 2025
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Every compliance gap below is mapped to an authentic statutory provision of India&apos;s data protection framework.
              The system does not equate the presence of personal data alone with an unlawful violation, but pinpoints specific safeguarding and storage limitation obligations.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 pt-2 text-xs">
          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <div className="text-[10px] text-slate-500 font-mono">SECTION 8(5)</div>
            <div className="font-bold text-white mt-0.5">Reasonable Safeguards</div>
            <div className="text-[10px] text-red-400 mt-1">Penalty: Up to ₹250 Crores</div>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <div className="text-[10px] text-slate-500 font-mono">SECTION 8(7)</div>
            <div className="font-bold text-white mt-0.5">Storage Limitation</div>
            <div className="text-[10px] text-amber-400 mt-1">Penalty: Up to ₹100 Crores</div>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <div className="text-[10px] text-slate-500 font-mono">SECTION 12</div>
            <div className="font-bold text-white mt-0.5">Right to Erasure</div>
            <div className="text-[10px] text-blue-400 mt-1">Penalty: Up to ₹50 Crores</div>
          </div>

          <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
            <div className="text-[10px] text-slate-500 font-mono">RULES 2025</div>
            <div className="font-bold text-white mt-0.5">Technical Safeguards</div>
            <div className="text-[10px] text-purple-400 mt-1">Mandatory Redaction</div>
          </div>
        </div>
      </div>

      {/* Observations List */}
      <div className="space-y-4">
        {filtered.length > 0 ? (
          filtered.map((obs, idx) => (
            <div
              key={idx}
              className="rounded-xl border border-slate-800 bg-[#0E1626]/80 p-5 space-y-3 transition-all hover:border-slate-700"
            >
              {/* Provision Header */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div className="flex items-center space-x-2.5">
                  <span className="font-bold text-white text-sm">
                    {obs.provision_section}
                  </span>
                  <span className="text-slate-400 text-xs">| {obs.provision_title}</span>
                </div>

                <div className="flex items-center space-x-2 font-mono text-[10px]">
                  <span className={`rounded px-2 py-0.5 font-bold border ${getStatusBadge(obs.status_in_force)}`}>
                    {obs.status_in_force}
                  </span>
                  <span className={`rounded px-2 py-0.5 font-bold border ${getSeverityBadge(obs.severity)}`}>
                    {obs.severity} IMPACT
                  </span>
                </div>
              </div>

              {/* Observation & Evidence */}
              <div className="rounded-lg border border-slate-800/80 bg-slate-950/60 p-3.5 space-y-2 text-xs">
                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">AUDIT OBSERVATION</span>
                  <p className="text-slate-200 mt-0.5 font-medium">{obs.observation}</p>
                </div>

                <div>
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">SUPPORTING EVIDENCE</span>
                  <p className="text-slate-400 mt-0.5 font-mono text-[11px]">{obs.evidence}</p>
                </div>
              </div>

              {/* Actionable Statutory Recommendation */}
              <div className="flex items-start space-x-2 text-xs text-emerald-300 bg-emerald-950/20 rounded-lg p-3 border border-emerald-500/20">
                <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold text-white">Recommended Remediation: </span>
                  <span>{obs.recommendation}</span>
                </div>
              </div>

            </div>
          ))
        ) : (
          <div className="rounded-xl border border-slate-800 bg-[#0E1626]/50 p-10 text-center space-y-3">
            <Scale className="h-8 w-8 text-slate-600 mx-auto" />
            <h4 className="text-sm font-semibold text-slate-300">No Compliance Observations</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Run an audit to evaluate file repositories against India&apos;s DPDP Act 2023 requirements.
            </p>
          </div>
        )}
      </div>

      {/* Statutory Legal Disclaimer Banner */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/40 p-4 text-[11px] text-slate-400 space-y-1">
        <div className="flex items-center space-x-1.5 font-bold text-slate-300">
          <Info className="h-3.5 w-3.5 text-blue-400" />
          <span>STATUTORY DISCLAIMER</span>
        </div>
        <p className="leading-relaxed">
          PRIVESCAN AI provides automated data discovery, semantic risk scoring, and compliance workflow assistance.
          This software does not provide formal legal advice, guarantee regulatory immunity, or substitute for formal certification by an accredited Data Protection Officer or counsel.
        </p>
      </div>

    </div>
  );
};
