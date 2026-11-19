"use client";

import React, { useState } from "react";
import {
  Sliders, Play, RefreshCw, CheckCircle2, AlertTriangle,
  HelpCircle, Eye, ArrowRight, ShieldCheck, Sparkles
} from "lucide-react";
import { api } from "../lib/api";
import { ContextClassificationResult } from "../lib/types";

export const ContextTesterModal: React.FC = () => {
  const [columnName, setColumnName] = useState("Order_ID");
  const [value, setValue] = useState("9876543210");
  const [documentType, setDocumentType] = useState("customer_orders");
  const [surroundingText, setSurroundingText] = useState("Invoice #9876543210, Item: Enterprise Server, Total: INR 45,000");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<ContextClassificationResult | null>(null);

  const presets = [
    {
      label: "Order ID (10 Digits)",
      col: "Order_ID",
      val: "9876543210",
      doc: "customer_orders",
      text: "Invoice #9876543210, Item: Enterprise Server"
    },
    {
      label: "Mobile Phone (10 Digits)",
      col: "Mobile_Number",
      val: "9876543210",
      doc: "customer_database",
      text: "Billing Contact: Aarav Sharma, SMS Alert: Enabled"
    },
    {
      label: "Individual PAN (ABCDE1234F)",
      col: "PAN_Number",
      val: "AAAPS1234K",
      doc: "kyc_records",
      text: "Tax ID Document: Form 16 Individual Assessment"
    },
    {
      label: "Aadhaar Card (12 Digits)",
      col: "Aadhaar_Number",
      val: "9876 5432 1098",
      doc: "personnel_records",
      text: "UIDAI Statutory Identity Verification"
    },
    {
      label: "Support Email (Non-Personal)",
      col: "Contact_Email",
      val: "support@enterprise.com",
      doc: "website_footer",
      text: "Reach out to support@enterprise.com for help"
    }
  ];

  const handleTest = async () => {
    try {
      setIsLoading(true);
      const res = await api.testContext({
        column_name: columnName,
        value: value,
        document_type: documentType,
        surrounding_text: surroundingText
      });
      setResult(res);
      setIsLoading(false);
    } catch (err) {
      console.error(err);
      setIsLoading(false);
    }
  };

  const applyPreset = (p: typeof presets[0]) => {
    setColumnName(p.col);
    setValue(p.val);
    setDocumentType(p.doc);
    setSurroundingText(p.text);
    setResult(null);
  };

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
          <Sliders className="h-6 w-6 text-purple-400" />
          <span>Context Intelligence Interactive Playground</span>
        </h1>
        <p className="text-xs text-slate-400 mt-1 font-mono">
          Live laboratory testing the primary differentiator: True PII vs Misleading Operational Identifiers
        </p>
      </div>

      {/* Preset Buttons */}
      <div className="space-y-2">
        <span className="text-xs font-mono text-slate-400">Quick Test Benchmark Scenarios:</span>
        <div className="flex flex-wrap gap-2">
          {presets.map((p, idx) => (
            <button
              key={idx}
              onClick={() => applyPreset(p)}
              className="rounded-lg border border-slate-800 bg-slate-900/80 px-3 py-1.5 text-xs font-medium text-slate-300 hover:border-purple-500/40 hover:text-white transition-all"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Input Form */}
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/80 p-6 space-y-4">
          <h3 className="text-sm font-bold text-white">Input Context Parameters</h3>

          <div className="space-y-3 text-xs">
            <div>
              <label className="block text-slate-400 mb-1 font-mono">Column Header / Field Label</label>
              <input
                type="text"
                value={columnName}
                onChange={(e) => setColumnName(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1 font-mono">Candidate Value</label>
              <input
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1 font-mono">Document Type / Schema Category</label>
              <input
                type="text"
                value={documentType}
                onChange={(e) => setDocumentType(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>

            <div>
              <label className="block text-slate-400 mb-1 font-mono">Surrounding Contextual Text (Optional)</label>
              <textarea
                rows={3}
                value={surroundingText}
                onChange={(e) => setSurroundingText(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-900 px-3 py-2 text-white focus:border-purple-500 focus:outline-none font-mono"
              />
            </div>
          </div>

          <div className="pt-2">
            <button
              onClick={handleTest}
              disabled={isLoading}
              className="w-full flex items-center justify-center space-x-2 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 py-3 text-xs font-bold text-white shadow-lg shadow-purple-500/25 hover:from-purple-500 hover:to-indigo-500 disabled:opacity-50 transition-all"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Evaluating Contextual Semantics...</span>
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 fill-current" />
                  <span>Execute Context Intelligence Evaluation</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Live Evaluation Result Output */}
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/80 p-6 space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Sparkles className="h-4 w-4 text-purple-400" />
            <span>Agent Classification Verdict</span>
          </h3>

          {result ? (
            <div className="space-y-4 animate-fadeIn">
              
              {/* Verdict Banner */}
              <div className={`rounded-xl border p-4 text-xs space-y-2 ${
                result.is_personal_data
                  ? "border-red-500/30 bg-red-950/20 text-red-300"
                  : "border-emerald-500/30 bg-emerald-950/20 text-emerald-300"
              }`}>
                <div className="flex items-center justify-between font-mono text-[11px]">
                  <span>VERDICT STATUS:</span>
                  <span className="font-bold">
                    {result.is_personal_data ? "⚠️ CONFIRMED PERSONAL DATA" : "✓ NON-PERSONAL IDENTIFIER"}
                  </span>
                </div>
                <div className="text-lg font-mono font-bold text-white">
                  {result.classification}
                </div>
              </div>

              {/* Confidence & Entity */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
                  <span className="text-[10px] text-slate-500 font-mono block">RESOLVED ENTITY TYPE</span>
                  <span className="text-sm font-bold text-white">{result.entity_type}</span>
                </div>

                <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3">
                  <span className="text-[10px] text-slate-500 font-mono block">CONFIDENCE METRIC</span>
                  <span className="text-sm font-bold text-emerald-400">
                    {(result.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Evidence Reason */}
              <div className="rounded-xl border border-slate-800 bg-slate-950/70 p-4 space-y-1.5 text-xs">
                <span className="text-[10px] font-mono text-purple-400 uppercase font-bold block">
                  AGENT EVIDENCE & EXPLANATION
                </span>
                <p className="text-slate-200 leading-relaxed font-sans">
                  {result.reason}
                </p>
              </div>

            </div>
          ) : (
            <div className="flex h-64 items-center justify-center text-center p-6 text-xs text-slate-500 border border-dashed border-slate-800 rounded-xl">
              Choose a preset or enter custom attributes, then click Execute to inspect live agent reasoning.
            </div>
          )}
        </div>

      </div>

    </div>
  );
};
