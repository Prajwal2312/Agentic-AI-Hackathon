"use client";

import React, { useState, useRef } from "react";
import {
  UploadCloud, FileSpreadsheet, FileText, CheckCircle2, AlertCircle,
  RefreshCw, Play, ShieldAlert, Check, X, File, Sparkles
} from "lucide-react";
import { api } from "../lib/api";
import { AuditSession, ScannedFile } from "../lib/types";

interface DocumentScannerProps {
  activeSession: AuditSession | null;
  onAuditCompleted: (session: AuditSession) => void;
  onTriggerDemo: () => void;
  isDemoLoading: boolean;
}

export const DocumentScanner: React.FC<DocumentScannerProps> = ({
  activeSession,
  onAuditCompleted,
  onTriggerDemo,
  isDemoLoading
}) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isAuditing, setIsAuditing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [scannedFilesList, setScannedFilesList] = useState<ScannedFile[]>([]);
  const [scanStep, setScanStep] = useState<string>("Ready to scan");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const folderInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const filesArray = Array.from(e.target.files);
      setSelectedFiles((prev) => [...prev, ...filesArray]);
      setErrorMessage(null);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files) {
      const filesArray = Array.from(e.dataTransfer.files);
      setSelectedFiles((prev) => [...prev, ...filesArray]);
      setErrorMessage(null);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleUploadAndScan = async () => {
    if (selectedFiles.length === 0) {
      setErrorMessage("Please select at least one document to scan.");
      return;
    }

    try {
      setIsUploading(true);
      setErrorMessage(null);
      setScanStep("Uploading files to secure audit boundary...");

      // 1. Always create a dedicated audit session for this upload batch
      const sessionTitle = selectedFiles.length === 1
        ? `Audit: ${selectedFiles[0].name}`
        : `Upload Batch (${selectedFiles.length} files) - ${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
      const newSession = await api.createSession(sessionTitle);
      const sessionId = newSession.id;

      // 2. Upload files
      const uploaded = await api.uploadFiles(sessionId, selectedFiles);
      setScannedFilesList(uploaded);
      setIsUploading(false);

      // 3. Initiate multi-agent LangGraph execution
      setIsAuditing(true);
      setScanStep("Discovery Agent: Extracting structured text and table schemas...");
      
      const finishedSession = await api.executeAudit(sessionId);
      setScanStep("Audit completed successfully!");
      setIsAuditing(false);
      onAuditCompleted(finishedSession);

    } catch (err: any) {
      setIsUploading(false);
      setIsAuditing(false);
      setErrorMessage(err.message || "Failed to complete document audit.");
    }
  };

  return (
    <div className="space-y-8 pb-12">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center space-x-2">
            <UploadCloud className="h-6 w-6 text-blue-400" />
            <span>Document Discovery Scanner</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Multimodal Extractor: Synthetic PDFs, Scanned Images (OCR), & Spreadsheets (Max 50MB per file)
          </p>
        </div>

        {/* Quick Demo Button */}
        <button
          onClick={onTriggerDemo}
          disabled={isDemoLoading || isAuditing}
          className="flex items-center space-x-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-purple-500/20 hover:from-purple-500 hover:to-indigo-500 transition-all disabled:opacity-50"
        >
          {isDemoLoading ? (
            <RefreshCw className="h-4 w-4 animate-spin" />
          ) : (
            <Sparkles className="h-4 w-4" />
          )}
          <span>Load Synthetic Benchmark Suite (PDF, Scanned KYC Image, Spreadsheets)</span>
        </button>
      </div>

      {/* Multimodal Router Capability Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 flex items-center space-x-2.5">
          <div className="rounded bg-red-500/10 p-1.5 text-red-400 border border-red-500/20">
            <FileText className="h-4 w-4" />
          </div>
          <div>
            <p className="text-xs font-semibold text-white">Synthetic PDFs</p>
            <p className="text-[10px] text-slate-400 font-mono">PyMuPDF Extractor</p>
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 flex items-center space-x-2.5">
          <div className="rounded bg-purple-500/10 p-1.5 text-purple-400 border border-purple-500/20">
            <FileText className="h-4 w-4" />
          </div>
          <div>
            <p className="text-xs font-semibold text-white">Scanned Images</p>
            <p className="text-[10px] text-slate-400 font-mono">Multimodal AI OCR</p>
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 flex items-center space-x-2.5">
          <div className="rounded bg-emerald-500/10 p-1.5 text-emerald-400 border border-emerald-500/20">
            <FileSpreadsheet className="h-4 w-4" />
          </div>
          <div>
            <p className="text-xs font-semibold text-white">Spreadsheets</p>
            <p className="text-[10px] text-slate-400 font-mono">Pandas & Openpyxl</p>
          </div>
        </div>

        <div className="rounded-lg border border-slate-800 bg-slate-900/60 p-3 flex items-center space-x-2.5">
          <div className="rounded bg-blue-500/10 p-1.5 text-blue-400 border border-blue-500/20">
            <File className="h-4 w-4" />
          </div>
          <div>
            <p className="text-xs font-semibold text-white">Documents & Logs</p>
            <p className="text-[10px] text-slate-400 font-mono">Docx & CSV Parser</p>
          </div>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        className="rounded-2xl border-2 border-dashed border-slate-700 bg-[#0E1626]/50 p-8 text-center transition-all hover:border-blue-500/50 hover:bg-[#0E1626]/80"
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.xlsx,.xls,.csv,.txt,.png,.jpg,.jpeg,.tiff,.bmp,.webp"
          onChange={handleFileChange}
          className="hidden"
        />
        {/* HTML5 WebKit folder input */}
        <input
          ref={folderInputRef}
          type="file"
          // @ts-ignore
          webkitdirectory="true"
          directory="true"
          multiple
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-400 mb-4 border border-blue-500/20">
          <UploadCloud className="h-7 w-7" />
        </div>
        <h3 className="text-base font-semibold text-white">
          Drop enterprise files or folder here
        </h3>
        <p className="text-xs text-slate-400 mt-2 max-w-md mx-auto">
          Upload spreadsheets, scanned KYC images, PDF archives, or employee directories.
          Context Intelligence separates true personal data from Order IDs and system identifiers.
        </p>

        <div className="mt-5 flex items-center justify-center space-x-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-xs font-medium text-white hover:bg-blue-500 transition shadow-sm"
          >
            Select Files
          </button>
          <button
            type="button"
            onClick={() => folderInputRef.current?.click()}
            className="rounded-lg border border-slate-700 bg-slate-800/80 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700 transition"
          >
            Select Entire Folder
          </button>
        </div>
      </div>

      {/* Error Message */}
      {errorMessage && (
        <div className="rounded-xl border border-red-500/30 bg-red-950/20 p-4 text-xs text-red-300 flex items-center space-x-2">
          <AlertCircle className="h-4 w-4 text-red-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Selected Files Queue */}
      {selectedFiles.length > 0 && (
        <div className="rounded-xl border border-slate-800 bg-[#0E1626]/70 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white">
              Selected Documents Queue ({selectedFiles.length})
            </h3>
            <button
              onClick={() => setSelectedFiles([])}
              className="text-xs text-slate-400 hover:text-red-400 transition-colors"
            >
              Clear All
            </button>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            {selectedFiles.map((file, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-3 text-xs"
              >
                <div className="flex items-center space-x-2.5 truncate">
                  <File className="h-4 w-4 text-blue-400 shrink-0" />
                  <div className="truncate">
                    <p className="font-semibold text-slate-200 truncate">{file.name}</p>
                    <p className="text-[10px] text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(idx);
                  }}
                  className="text-slate-500 hover:text-red-400 ml-2"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>

          {/* Action Trigger */}
          <div className="pt-2 flex justify-end">
            <button
              onClick={handleUploadAndScan}
              disabled={isUploading || isAuditing}
              className="flex items-center space-x-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-2.5 text-xs font-bold text-white shadow-lg shadow-blue-500/25 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 transition-all"
            >
              {isUploading || isAuditing ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>{scanStep}</span>
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 fill-current" />
                  <span>Start Autonomous Audit</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Progress & Live Agent Execution Banner */}
      {(isUploading || isAuditing) && (
        <div className="rounded-xl border border-blue-500/30 bg-blue-950/20 p-5 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-blue-300 flex items-center space-x-2">
              <RefreshCw className="h-4 w-4 animate-spin text-blue-400" />
              <span>Multi-Agent Orchestrator in Progress...</span>
            </span>
            <span className="font-mono text-blue-400">{scanStep}</span>
          </div>

          <div className="grid grid-cols-5 gap-2 text-center text-[10px] font-mono pt-2">
            <div className="rounded bg-blue-500/20 p-2 text-blue-300 border border-blue-500/30">
              1. Discovery
            </div>
            <div className="rounded bg-purple-500/20 p-2 text-purple-300 border border-purple-500/30">
              2. Context
            </div>
            <div className="rounded bg-amber-500/20 p-2 text-amber-300 border border-amber-500/30">
              3. Risk
            </div>
            <div className="rounded bg-emerald-500/20 p-2 text-emerald-300 border border-emerald-500/30">
              4. DPDP
            </div>
            <div className="rounded bg-cyan-500/20 p-2 text-cyan-300 border border-cyan-500/30">
              5. Remediate
            </div>
          </div>
        </div>
      )}

      {/* Benchmark Files Info Card */}
      <div className="rounded-xl border border-slate-800 bg-[#0E1626]/50 p-5 space-y-3">
        <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-400">
          Demo Benchmark Files Ready:
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs text-slate-300">
          <div className="rounded-lg border border-slate-800/80 bg-slate-900/60 p-3 space-y-1">
            <div className="font-semibold text-emerald-400">customer_database.xlsx</div>
            <p className="text-[11px] text-slate-400">Contains 10-digit Order IDs next to 10-digit Phone numbers, PAN numbers, and Bank Accounts.</p>
          </div>
          <div className="rounded-lg border border-slate-800/80 bg-slate-900/60 p-3 space-y-1">
            <div className="font-semibold text-blue-400">employee_records.pdf</div>
            <p className="text-[11px] text-slate-400">Personnel records with Aadhaar, PAN, Bank Details, and Phone numbers requiring access restriction.</p>
          </div>
          <div className="rounded-lg border border-slate-800/80 bg-slate-900/60 p-3 space-y-1">
            <div className="font-semibold text-amber-400">old_customer_export.csv</div>
            <p className="text-[11px] text-slate-400">Unmonitored historical export containing transaction references and sensitive customer Aadhaar numbers.</p>
          </div>
        </div>
      </div>

    </div>
  );
};
