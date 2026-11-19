"use client";

import React, { useState } from "react";
import {
  ShieldAlert, Search, Filter, Eye, ArrowUpDown, ChevronRight,
  CheckCircle2, AlertTriangle, ShieldCheck, Database, HelpCircle
} from "lucide-react";
import { PIIFinding } from "../lib/types";
import { InvestigationModal } from "./InvestigationModal";

interface FindingsExplorerProps {
  findings: PIIFinding[];
  activeSessionId: string;
}

export const FindingsExplorer: React.FC<FindingsExplorerProps> = ({
  findings,
  activeSessionId
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [categoryFilter, setCategoryFilter] = useState("ALL");
  const [classificationFilter, setClassificationFilter] = useState("ALL");
  const [selectedFinding, setSelectedFinding] = useState<PIIFinding | null>(null);

  // Filter findings
  const filteredFindings = findings.filter((f) => {
    const matchesSearch =
      searchTerm === "" ||
      f.entity_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (f.col_name && f.col_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (f.file_name && f.file_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (f.explanation && f.explanation.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesRisk = riskFilter === "ALL" || f.risk_level === riskFilter;
    const matchesCategory = categoryFilter === "ALL" || f.entity_type === categoryFilter;
    const matchesClass = classificationFilter === "ALL" || f.classification === classificationFilter;

    return matchesSearch && matchesRisk && matchesCategory && matchesClass;
  });

  const getRiskBadge = (level: string) => {
    switch (level) {
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

  const getClassificationBadge = (cls: string) => {
    switch (cls) {
      case "CONFIRMED_PERSONAL_DATA":
        return "bg-purple-500/20 text-purple-300 border-purple-500/30";
      case "LIKELY_PERSONAL_DATA":
        return "bg-blue-500/20 text-blue-300 border-blue-500/30";
      case "NON_PERSONAL_IDENTIFIER":
        return "bg-slate-700/60 text-slate-300 border-slate-600";
      case "AMBIGUOUS":
        return "bg-amber-500/20 text-amber-300 border-amber-500/30";
      default:
        return "bg-slate-800 text-slate-400";
    }
  };

  return (
    <div className="space-y-6 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
            <ShieldAlert className="h-6 w-6 text-indigo-400" />
            <span>Discovered Findings Explorer</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Granular PII taxonomy & contextual intelligence verification
          </p>
        </div>

        <div className="text-xs font-mono text-slate-400">
          Showing <strong className="text-white">{filteredFindings.length}</strong> of {findings.length} findings
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="rounded-xl border border-slate-800 bg-[#0E1626]/70 p-4 space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input
              type="text"
              placeholder="Search value, column, file, or rationale..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900/90 pl-9 pr-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* Risk Filter */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-mono">Risk:</span>
            <select
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900/90 px-3 py-2 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="HIGH">High Only</option>
              <option value="MEDIUM">Medium Only</option>
              <option value="LOW">Low Only</option>
            </select>
          </div>

          {/* Category Filter */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-mono">Category:</span>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900/90 px-3 py-2 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
            >
              <option value="ALL">All Categories</option>
              <option value="PHONE">Phone Number</option>
              <option value="EMAIL">Email Address</option>
              <option value="PAN">PAN (Income Tax)</option>
              <option value="AADHAAR">Aadhaar (UIDAI)</option>
              <option value="BANK_ACC">Bank Account</option>
              <option value="PERSON_NAME">Person Name</option>
              <option value="SYSTEM_IDENTIFIER">System Identifier</option>
              <option value="AMBIGUOUS_NUMERIC_10">Ambiguous 10-Digit</option>
            </select>
          </div>

          {/* Classification Filter */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-mono">Classification:</span>
            <select
              value={classificationFilter}
              onChange={(e) => setClassificationFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-800 bg-slate-900/90 px-3 py-2 text-xs text-slate-200 focus:border-blue-500 focus:outline-none"
            >
              <option value="ALL">All Classifications</option>
              <option value="CONFIRMED_PERSONAL_DATA">Confirmed Personal Data</option>
              <option value="LIKELY_PERSONAL_DATA">Likely Personal Data</option>
              <option value="NON_PERSONAL_IDENTIFIER">Non-Personal Identifier</option>
              <option value="AMBIGUOUS">Ambiguous (Human Review)</option>
            </select>
          </div>

        </div>
      </div>

      {/* Findings Data Table */}
      <div className="rounded-xl border border-slate-800 bg-[#0E1626]/80 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="border-b border-slate-800 bg-slate-900/90 font-mono text-[11px] text-slate-400">
              <tr>
                <th className="px-4 py-3">File / Coordinate</th>
                <th className="px-4 py-3">Detected Value (Masked)</th>
                <th className="px-4 py-3">Entity Category</th>
                <th className="px-4 py-3">Context Classification</th>
                <th className="px-4 py-3">Risk Level</th>
                <th className="px-4 py-3">Confidence</th>
                <th className="px-4 py-3">Agent Context Rationale</th>
                <th className="px-4 py-3 text-right">Investigation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredFindings.length > 0 ? (
                filteredFindings.map((f) => (
                  <tr
                    key={f.id}
                    onClick={() => setSelectedFinding(f)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div className="font-semibold text-white truncate max-w-[150px]">{f.file_name}</div>
                      <div className="text-[10px] text-slate-500 font-mono">{f.location || "Record"}</div>
                    </td>

                    <td className="px-4 py-3 font-mono font-semibold text-slate-200">
                      {f.masked_value}
                    </td>

                    <td className="px-4 py-3">
                      <span className="font-semibold text-blue-300">{f.entity_type}</span>
                      {f.col_name && (
                        <span className="block text-[10px] text-slate-500 font-mono">col: {f.col_name}</span>
                      )}
                    </td>

                    <td className="px-4 py-3">
                      <span className={`rounded px-2 py-0.5 text-[10px] font-bold border ${getClassificationBadge(f.classification)}`}>
                        {f.classification.replace(/_/g, " ")}
                      </span>
                    </td>

                    <td className="px-4 py-3">
                      <span className={`rounded px-2 py-0.5 text-[10px] font-bold border ${getRiskBadge(f.risk_level)}`}>
                        {f.risk_level}
                      </span>
                    </td>

                    <td className="px-4 py-3 font-mono text-emerald-400 font-semibold">
                      {(f.confidence * 100).toFixed(0)}%
                    </td>

                    <td className="px-4 py-3 text-slate-400 max-w-xs truncate text-[11px]">
                      {f.explanation}
                    </td>

                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedFinding(f);
                        }}
                        className="rounded-lg bg-blue-600/10 border border-blue-500/20 px-2.5 py-1 text-[11px] font-medium text-blue-400 hover:bg-blue-600/20 transition-all"
                      >
                        Investigate
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="px-4 py-12 text-center text-slate-500">
                    No findings match your filter criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Investigation Dossier Modal */}
      {selectedFinding && (
        <InvestigationModal
          finding={selectedFinding}
          onClose={() => setSelectedFinding(null)}
        />
      )}

    </div>
  );
};
