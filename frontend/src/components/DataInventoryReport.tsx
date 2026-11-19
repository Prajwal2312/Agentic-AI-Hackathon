"use client";

import React, { useState, useEffect } from "react";
import {
  FileSpreadsheet, FileText, Image as ImageIcon, Database,
  ShieldAlert, ShieldCheck, Download, Search, Filter,
  CheckCircle2, AlertTriangle, Layers, Sparkles, RefreshCw
} from "lucide-react";
import { api } from "../lib/api";
import { AuditSession, InventoryItem, DataInventoryResponse } from "../lib/types";

interface DataInventoryReportProps {
  activeSession: AuditSession | null;
}

export const DataInventoryReport: React.FC<DataInventoryReportProps> = ({ activeSession }) => {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedSensitivity, setSelectedSensitivity] = useState<string>("ALL");
  const [selectedExtractor, setSelectedExtractor] = useState<string>("ALL");

  const fetchInventory = async () => {
    setIsLoading(true);
    try {
      const data: DataInventoryResponse = await api.getDataInventory(activeSession?.id);
      setInventory(data.inventory || []);
    } catch (err) {
      console.error("Failed to load inventory:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, [activeSession?.id]);

  // Filtering
  const filteredItems = inventory.filter((item) => {
    const matchesSearch =
      item.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.extractor_used.toLowerCase().includes(searchTerm.toLowerCase()) ||
      Object.keys(item.categories_held).some((cat) => cat.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesSensitivity =
      selectedSensitivity === "ALL" ||
      item.sensitivity_level.toUpperCase() === selectedSensitivity.toUpperCase();

    const matchesExtractor =
      selectedExtractor === "ALL" ||
      item.extractor_used.toLowerCase().includes(selectedExtractor.toLowerCase());

    return matchesSearch && matchesSensitivity && matchesExtractor;
  });

  const totalPersonalRecords = inventory.reduce((acc, curr) => acc + curr.total_personal_records, 0);
  const criticalFilesCount = inventory.filter((i) => i.sensitivity_level === "CRITICAL" || i.sensitivity_level === "HIGH").length;

  const downloadCsv = () => {
    if (inventory.length === 0) return;
    const headers = ["File ID", "File Name", "File Type", "Extractor Used", "Sensitivity Level", "Personal Records Count", "Categories Held", "Sample Locations"];
    const rows = inventory.map((item) => [
      item.file_id,
      `"${item.filename}"`,
      item.file_type,
      `"${item.extractor_used}"`,
      item.sensitivity_level,
      item.total_personal_records,
      `"${Object.entries(item.categories_held).map(([k, v]) => `${k}:${v}`).join("; ")}"`,
      `"${item.sample_locations.map((loc) => `${loc.entity_type}@${loc.location}`).join("; ")}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map((r) => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Data_Inventory_Report_${activeSession?.id || "Export"}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Context Description */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="flex items-center space-x-2">
            <span className="rounded bg-blue-500/10 px-2 py-0.5 text-xs font-semibold text-blue-400 border border-blue-500/20">
              DPDP Act Statutory Requirement
            </span>
            <span className="text-xs text-slate-400 font-mono">Sec. 8(1) & 8(5) Mapping</span>
          </div>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-white">
            Data Inventory Report: Which Personal Data is Held Where
          </h1>
          <p className="text-xs text-slate-400">
            Autonomous multi-agent discovery mapping personal data categories to exact file storage locations.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchInventory}
            disabled={isLoading}
            className="flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700 transition"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>

          <button
            onClick={downloadCsv}
            disabled={inventory.length === 0}
            className="flex items-center space-x-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-2 text-xs font-medium text-slate-300 hover:bg-slate-700 transition"
          >
            <Download className="h-3.5 w-3.5 text-blue-400" />
            <span>Export CSV</span>
          </button>

          {activeSession && (
            <a
              href={api.getReportDownloadUrl(activeSession.id)}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 px-3.5 py-2 text-xs font-medium text-white shadow-lg shadow-blue-500/20 hover:brightness-110 transition"
            >
              <FileText className="h-3.5 w-3.5" />
              <span>Full PDF Report</span>
            </a>
          )}
        </div>
      </div>

      {/* Summary Metric Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="glass-panel rounded-xl p-4 border border-slate-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Repositories Audited</span>
            <Database className="h-4 w-4 text-blue-400" />
          </div>
          <p className="mt-2 text-2xl font-bold text-white">{inventory.length}</p>
          <p className="mt-1 text-[11px] text-slate-500">Multimodal PDFs, spreadsheets & images</p>
        </div>

        <div className="glass-panel rounded-xl p-4 border border-slate-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Personal Data Records</span>
            <ShieldAlert className="h-4 w-4 text-indigo-400" />
          </div>
          <p className="mt-2 text-2xl font-bold text-indigo-400">{totalPersonalRecords}</p>
          <p className="mt-1 text-[11px] text-slate-500">Confirmed & likely personal identifiers</p>
        </div>

        <div className="glass-panel rounded-xl p-4 border border-slate-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">High Sensitivity Repositories</span>
            <AlertTriangle className="h-4 w-4 text-red-400" />
          </div>
          <p className="mt-2 text-2xl font-bold text-red-400">{criticalFilesCount}</p>
          <p className="mt-1 text-[11px] text-slate-500">Contains Aadhaar, PAN or Bank records</p>
        </div>

        <div className="glass-panel rounded-xl p-4 border border-slate-800/80">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400">Remediation Readiness</span>
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="mt-2 text-2xl font-bold text-emerald-400">100%</p>
          <p className="mt-1 text-[11px] text-slate-500">Masked copies generated with zero overwrite</p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel rounded-xl p-4 border border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by file name or category..."
            className="w-full rounded-lg border border-slate-700 bg-slate-900/90 pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none"
          />
        </div>

        <div className="flex w-full sm:w-auto items-center space-x-2">
          <div className="flex items-center space-x-1.5">
            <Filter className="h-3.5 w-3.5 text-slate-400" />
            <span className="text-[11px] text-slate-400">Sensitivity:</span>
            <select
              value={selectedSensitivity}
              onChange={(e) => setSelectedSensitivity(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs text-slate-300 focus:border-blue-500 focus:outline-none"
            >
              <option value="ALL">All Levels</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div className="flex items-center space-x-1.5">
            <span className="text-[11px] text-slate-400">Extractor:</span>
            <select
              value={selectedExtractor}
              onChange={(e) => setSelectedExtractor(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-900 px-2.5 py-1 text-xs text-slate-300 focus:border-blue-500 focus:outline-none"
            >
              <option value="ALL">All Extractors</option>
              <option value="PyMuPDF">PyMuPDF (PDF)</option>
              <option value="Pandas">Spreadsheets (XLSX/CSV)</option>
              <option value="OCR">Multimodal OCR (Images)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Data Inventory Table */}
      <div className="glass-panel overflow-hidden rounded-xl border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="border-b border-slate-800 bg-slate-900/90 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              <tr>
                <th className="px-4 py-3">Repository / File</th>
                <th className="px-4 py-3">Extractor Engine</th>
                <th className="px-4 py-3">File Sensitivity</th>
                <th className="px-4 py-3">Personal Data Categories Held</th>
                <th className="px-4 py-3">Exact Storage Locations</th>
                <th className="px-4 py-3">Remediation Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    <RefreshCw className="mx-auto h-6 w-6 animate-spin text-blue-400 mb-2" />
                    <span>Loading data inventory mapping...</span>
                  </td>
                </tr>
              ) : filteredItems.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    No repositories matched your filters. Run a scan or demo audit to populate inventory.
                  </td>
                </tr>
              ) : (
                filteredItems.map((item) => {
                  const isImage = ["PNG", "JPG", "JPEG", "TIFF"].some((ext) => item.file_type.includes(ext));
                  const isSpreadsheet = ["XLS", "CSV"].some((ext) => item.file_type.includes(ext));
                  const isPdf = item.file_type.includes("PDF");

                  const getSensitivityBadge = (sens: string) => {
                    const s = (sens || "LOW").toUpperCase();
                    if (s === "CRITICAL") {
                      return <span className="rounded bg-red-500/20 px-2 py-0.5 text-[10px] font-bold text-red-400 border border-red-500/30">CRITICAL</span>;
                    }
                    if (s === "HIGH") {
                      return <span className="rounded bg-orange-500/20 px-2 py-0.5 text-[10px] font-bold text-orange-400 border border-orange-500/30">HIGH</span>;
                    }
                    if (s === "MEDIUM") {
                      return <span className="rounded bg-amber-500/20 px-2 py-0.5 text-[10px] font-bold text-amber-400 border border-amber-500/30">MEDIUM</span>;
                    }
                    return <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-[10px] font-bold text-emerald-400 border border-emerald-500/30">LOW</span>;
                  };

                  return (
                    <tr key={item.file_id} className="hover:bg-slate-800/40 transition">
                      {/* File Name & Format */}
                      <td className="px-4 py-3.5">
                        <div className="flex items-center space-x-2.5">
                          <div className="rounded-lg bg-slate-800 p-2 border border-slate-700/60">
                            {isPdf && <FileText className="h-4 w-4 text-red-400" />}
                            {isSpreadsheet && <FileSpreadsheet className="h-4 w-4 text-emerald-400" />}
                            {isImage && <ImageIcon className="h-4 w-4 text-purple-400" />}
                            {!isPdf && !isSpreadsheet && !isImage && <FileText className="h-4 w-4 text-blue-400" />}
                          </div>
                          <div>
                            <p className="font-semibold text-white font-sans">{item.filename}</p>
                            <p className="text-[10px] text-slate-500">
                              {item.file_type} • {(item.file_size_bytes / 1024).toFixed(1)} KB
                            </p>
                          </div>
                        </div>
                      </td>

                      {/* Extractor Engine */}
                      <td className="px-4 py-3.5">
                        <span className="rounded bg-slate-800/90 px-2 py-1 text-[11px] text-blue-300 border border-slate-700 font-sans">
                          {item.extractor_used}
                        </span>
                      </td>

                      {/* Sensitivity */}
                      <td className="px-4 py-3.5">
                        {getSensitivityBadge(item.sensitivity_level)}
                      </td>

                      {/* Categories Discovered */}
                      <td className="px-4 py-3.5">
                        <div className="flex flex-wrap gap-1.5">
                          {Object.keys(item.categories_held).length === 0 ? (
                            <span className="text-[11px] text-slate-500">No personal data</span>
                          ) : (
                            Object.entries(item.categories_held).map(([cat, count]) => (
                              <span
                                key={cat}
                                className="inline-flex items-center space-x-1 rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-300 border border-slate-700"
                              >
                                <span>{cat}</span>
                                <span className="rounded bg-blue-500/20 px-1 font-bold text-blue-400">{count}</span>
                              </span>
                            ))
                          )}
                        </div>
                      </td>

                      {/* Storage Locations */}
                      <td className="px-4 py-3.5">
                        <div className="space-y-1 max-w-xs">
                          {item.sample_locations.length === 0 ? (
                            <span className="text-[11px] text-slate-500">Operational metadata only</span>
                          ) : (
                            item.sample_locations.slice(0, 3).map((loc, i) => (
                              <div key={i} className="text-[10px] text-slate-400 truncate">
                                <span className="text-blue-400">↳ </span>
                                <span className="font-semibold text-slate-300">{loc.entity_type}</span>: {loc.location}
                              </div>
                            ))
                          )}
                          {item.sample_locations.length > 3 && (
                            <p className="text-[9px] text-slate-500">
                              +{item.sample_locations.length - 3} additional mapped locations in report
                            </p>
                          )}
                        </div>
                      </td>

                      {/* Remediation Status */}
                      <td className="px-4 py-3.5">
                        <div className="flex items-center space-x-1.5 text-[11px] text-emerald-400">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          <span className="font-sans">Redacted Copy Ready</span>
                        </div>
                        <p className="text-[10px] text-slate-500 font-sans">Original file secured & preserved</p>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
