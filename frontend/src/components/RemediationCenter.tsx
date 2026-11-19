"use client";

import React, { useState } from "react";
import {
  FileCheck, ShieldCheck, Lock, Download, Check, X, AlertCircle,
  FileSpreadsheet, FileText, CheckCircle2, Clock, RefreshCw, Eye
} from "lucide-react";
import { RemediationAction } from "../lib/types";
import { api } from "../lib/api";

interface RemediationCenterProps {
  actions: RemediationAction[];
  activeSessionId: string;
  onActionUpdated: () => void;
}

export const RemediationCenter: React.FC<RemediationCenterProps> = ({
  actions,
  activeSessionId,
  onActionUpdated
}) => {
  const [processingId, setProcessingId] = useState<number | null>(null);
  const [adminNote, setAdminNote] = useState<string>("");

  const handleApproval = async (actionId: number, approve: boolean) => {
    try {
      setProcessingId(actionId);
      await api.approveRemediation(actionId, approve, adminNote || undefined);
      setProcessingId(null);
      setAdminNote("");
      onActionUpdated();
    } catch (err) {
      console.error("Failed to update approval", err);
      setProcessingId(null);
    }
  };

  const getActionTypeBadge = (type: string) => {
    switch (type) {
      case "MASK_DOCUMENT":
        return "bg-cyan-500/20 text-cyan-400 border-cyan-500/30";
      case "RESTRICT_ACCESS":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case "RETENTION_REVIEW":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      default:
        return "bg-slate-700 text-slate-300";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "APPROVED":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "REJECTED":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      default:
        return "bg-amber-500/20 text-amber-300 border-amber-500/30";
    }
  };

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
            <FileCheck className="h-6 w-6 text-cyan-400" />
            <span>Remediation & Masking Center</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Human-in-the-Loop Governance | Cryptographic Redaction & Original File Preservation
          </p>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900/80 px-3 py-1.5 text-xs font-mono text-slate-300">
          Pending Approvals: <strong className="text-amber-400">{actions.filter(a => a.status === "PENDING_APPROVAL").length}</strong>
        </div>
      </div>

      {/* Safety Policy Banner */}
      <div className="rounded-2xl border border-blue-500/30 bg-blue-950/20 p-5 space-y-2">
        <div className="flex items-center space-x-2 text-xs font-bold text-blue-300">
          <ShieldCheck className="h-4 w-4" />
          <span>ENTERPRISE INTEGRITY GUARANTEE</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          Original files are <strong className="text-white">never permanently overwritten or deleted</strong> automatically.
          Redacted copies are generated in isolated storage with sensitive personal data masked while maintaining operational non-personal identifiers (e.g. Order IDs). All destructive actions require explicit administrator sign-off.
        </p>
      </div>

      {/* Actions Queue */}
      <div className="space-y-4">
        {actions.length > 0 ? (
          actions.map((act) => (
            <div
              key={act.id}
              className="rounded-xl border border-slate-800 bg-[#0E1626]/80 p-5 space-y-4 transition-all hover:border-slate-700"
            >
              {/* Row 1: Action Type and Status */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div className="flex items-center space-x-3">
                  <span className={`rounded-lg px-2.5 py-1 text-xs font-bold border ${getActionTypeBadge(act.action_type)}`}>
                    {act.action_type.replace(/_/g, " ")}
                  </span>
                  <span className="font-semibold text-white text-sm">
                    {act.file_name || "Document"}
                  </span>
                </div>

                <div className="flex items-center space-x-3">
                  <span className={`rounded px-2.5 py-0.5 text-[10px] font-bold border ${getStatusBadge(act.status)}`}>
                    {act.status.replace(/_/g, " ")}
                  </span>

                  {/* Redacted Download Button */}
                  {act.has_redacted_copy && (
                    <a
                      href={api.getRedactedDownloadUrl(act.id)}
                      download
                      className="flex items-center space-x-1.5 rounded-lg bg-cyan-600/20 border border-cyan-500/30 px-3 py-1 text-xs font-semibold text-cyan-400 hover:bg-cyan-600/30 transition-all"
                    >
                      <Download className="h-3.5 w-3.5" />
                      <span>Download Redacted Copy</span>
                    </a>
                  )}
                </div>
              </div>

              {/* Row 2: Details & Proposed Actions */}
              <div className="rounded-lg border border-slate-800/80 bg-slate-950/60 p-3.5 text-xs space-y-1.5">
                <span className="text-[10px] font-mono text-slate-500 uppercase block">PROPOSED ACTION DETAILS</span>
                <p className="text-slate-200">{act.proposed_details}</p>
                <div className="font-mono text-[10px] text-slate-500 pt-1">
                  Original: {act.original_file_path}
                </div>
              </div>

              {/* Row 3: Admin Review & Human Approval Section */}
              {act.status === "PENDING_APPROVAL" ? (
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pt-2 border-t border-slate-800/80">
                  <input
                    type="text"
                    placeholder="Enter compliance administrator notes (optional)..."
                    value={adminNote}
                    onChange={(e) => setAdminNote(e.target.value)}
                    className="w-full sm:w-80 rounded-lg border border-slate-800 bg-slate-900/90 px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:border-cyan-500 focus:outline-none"
                  />

                  <div className="flex items-center space-x-2 shrink-0">
                    <button
                      onClick={() => handleApproval(act.id, false)}
                      disabled={processingId === act.id}
                      className="flex items-center space-x-1.5 rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-1.5 text-xs font-semibold text-red-400 hover:bg-red-500/20 disabled:opacity-50"
                    >
                      <X className="h-3.5 w-3.5" />
                      <span>Reject</span>
                    </button>

                    <button
                      onClick={() => handleApproval(act.id, true)}
                      disabled={processingId === act.id}
                      className="flex items-center space-x-1.5 rounded-lg bg-emerald-600 px-4 py-1.5 text-xs font-bold text-white shadow-md shadow-emerald-600/20 hover:bg-emerald-500 disabled:opacity-50"
                    >
                      {processingId === act.id ? (
                        <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <Check className="h-3.5 w-3.5" />
                      )}
                      <span>Approve Remediation</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-xs text-slate-400 flex items-center space-x-2 pt-1">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  <span>
                    Decision recorded: <strong className="text-white">{act.status}</strong>
                    {act.admin_notes && ` — "${act.admin_notes}"`}
                  </span>
                </div>
              )}

            </div>
          ))
        ) : (
          <div className="rounded-xl border border-slate-800 bg-[#0E1626]/50 p-10 text-center space-y-3">
            <FileCheck className="h-8 w-8 text-slate-600 mx-auto" />
            <h4 className="text-sm font-semibold text-slate-300">No Remediation Proposals</h4>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              Proposals are generated automatically when unmasked personal data is discovered.
            </p>
          </div>
        )}
      </div>

    </div>
  );
};
