"use client";

import React, { useState } from "react";
import {
  X, ShieldAlert, Eye, EyeOff, ShieldCheck, AlertTriangle,
  FileSpreadsheet, Scale, Lock, ArrowRight, HelpCircle
} from "lucide-react";
import { PIIFinding } from "../lib/types";

interface InvestigationModalProps {
  finding: PIIFinding | null;
  onClose: () => void;
}

export const InvestigationModal: React.FC<InvestigationModalProps> = ({
  finding,
  onClose
}) => {
  const [showRaw, setShowRaw] = useState(false);

  if (!finding) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="relative w-full max-w-2xl rounded-2xl border border-slate-700 bg-[#0E1626] p-6 shadow-2xl space-y-6">
        
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="h-9 w-9 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-400 border border-blue-500/20">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">
                Finding Investigation Dossier #{finding.id}
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                Contextual verification & exposure impact
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          
          {/* Main Value Display */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
              <span>DETECTED CANDIDATE VALUE</span>
              <button
                onClick={() => setShowRaw(!showRaw)}
                className="flex items-center space-x-1 text-blue-400 hover:underline"
              >
                {showRaw ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                <span>{showRaw ? "Mask Value" : "Reveal Raw"}</span>
              </button>
            </div>
            <div className="font-mono text-lg font-bold text-white tracking-wide">
              {showRaw ? (finding.raw_value || finding.masked_value) : finding.masked_value}
            </div>
          </div>

          {/* Key Attribute Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
              <span className="text-[10px] text-slate-500 block font-mono">ENTITY CATEGORY</span>
              <span className="font-bold text-white">{finding.entity_type}</span>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
              <span className="text-[10px] text-slate-500 block font-mono">CLASSIFICATION</span>
              <span className="font-bold text-blue-400">{finding.classification.replace(/_/g, " ")}</span>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
              <span className="text-[10px] text-slate-500 block font-mono">CONFIDENCE SCORE</span>
              <span className="font-bold text-emerald-400">{(finding.confidence * 100).toFixed(0)}%</span>
            </div>

            <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-2.5">
              <span className="text-[10px] text-slate-500 block font-mono">RISK SEVERITY</span>
              <span className={`font-bold ${
                finding.risk_level === "CRITICAL" ? "text-red-400" :
                finding.risk_level === "HIGH" ? "text-orange-400" :
                finding.risk_level === "MEDIUM" ? "text-amber-400" : "text-emerald-400"
              }`}>
                {finding.risk_level}
              </span>
            </div>
          </div>

          {/* Location & Context Source */}
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-4 space-y-2 text-xs">
            <h4 className="font-bold text-slate-300">Document Source & Location Coordinates</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-400 font-mono text-[11px]">
              <div>File: <strong className="text-white">{finding.file_name || "Document"}</strong></div>
              <div>Location: <strong className="text-white">{finding.location || "N/A"}</strong></div>
              <div>Column Header: <strong className="text-white">{finding.col_name || "Unlabeled"}</strong></div>
              <div>Detection Engine: <strong className="text-white">{finding.detection_method}</strong></div>
            </div>
          </div>

          {/* Agent Contextual Reasoning Explanation */}
          <div className="rounded-xl border border-blue-500/30 bg-blue-950/20 p-4 space-y-2">
            <h4 className="text-xs font-bold text-blue-300 flex items-center space-x-1.5">
              <Eye className="h-4 w-4" />
              <span>Context Intelligence Agent Reasoning</span>
            </h4>
            <p className="text-xs text-slate-200 leading-relaxed font-sans">
              {finding.explanation || "Classified using structural column semantics and verified data boundaries."}
            </p>
          </div>

          {/* Surrounding Context Snippet */}
          {finding.surrounding_context && (
            <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 space-y-1.5 font-mono text-[11px]">
              <span className="text-slate-500 block">SURROUNDING RECORD SNIPPET</span>
              <p className="text-slate-300 overflow-x-auto whitespace-pre-wrap">
                {finding.surrounding_context}
              </p>
            </div>
          )}

          {/* DPDP Legal Relevance */}
          <div className="rounded-xl border border-purple-500/30 bg-purple-950/20 p-4 space-y-2 text-xs">
            <h4 className="font-bold text-purple-300 flex items-center space-x-1.5">
              <Scale className="h-4 w-4" />
              <span>Applicable DPDP Act 2023 Provision</span>
            </h4>
            <p className="text-slate-300 leading-relaxed">
              Section 8(5) mandates reasonable security safeguards to prevent personal data breaches.
              Plaintext exposure of verified personal identifiers without role-based access control or redaction increases non-compliance liability under Schedule 1.
            </p>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="flex justify-end pt-2 border-t border-slate-800">
          <button
            onClick={onClose}
            className="rounded-xl bg-slate-800 px-5 py-2 text-xs font-semibold text-white hover:bg-slate-700"
          >
            Close Dossier
          </button>
        </div>

      </div>
    </div>
  );
};
