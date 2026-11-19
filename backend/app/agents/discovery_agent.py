"""
Agent 1: Discovery Agent
Responsibilities:
- Accept uploaded files / authorized directory scans
- Identify file types and extract document metadata
- Extract document text, tables, and structured records
- Generate file inventory
- Send extracted content to Context Agent
"""

import time
import os
from pathlib import Path
from typing import Dict, Any, List
from backend.app.agents.state import AgentState
from backend.app.engine.document_extractor import DocumentExtractor

class DiscoveryAgent:
    def __init__(self):
        self.name = "Discovery Agent"

    def run(self, state: AgentState) -> Dict[str, Any]:
        start_time = time.time()
        logs: List[str] = []
        logs.append(f"Discovery Agent initiated for session {state.session_id}.")
        logs.append(f"Scanning {len(state.file_paths)} submitted document(s)...")

        inventory: List[Dict[str, Any]] = []
        all_records: List[Dict[str, Any]] = []

        for idx, file_path_str in enumerate(state.file_paths):
            fpath = Path(file_path_str)
            if not fpath.exists():
                logs.append(f"WARNING: File {fpath.name} does not exist on disk.")
                continue

            file_id = state.file_ids[idx] if idx < len(state.file_ids) else idx + 1
            file_stat = fpath.stat()
            file_type = fpath.suffix.upper().replace(".", "")

            logs.append(f"Analyzing structure of {fpath.name} ({file_type}, {file_stat.st_size} bytes)...")

            try:
                extracted = DocumentExtractor.extract(str(fpath))
                logs.append(f"Extracted {len(extracted)} granular records/elements from {fpath.name}.")

                file_meta = {
                    "file_id": file_id,
                    "filename": fpath.name,
                    "file_path": str(fpath),
                    "file_type": file_type,
                    "file_size_bytes": file_stat.st_size,
                    "records_count": len(extracted),
                    "status": "PARSED"
                }
                inventory.append(file_meta)

                for rec in extracted:
                    all_records.append({
                        "file_id": file_id,
                        "file_name": fpath.name,
                        "value": rec.value,
                        "column_name": rec.column_name,
                        "row_idx": rec.row_idx,
                        "col_idx": rec.col_idx,
                        "page_number": rec.page_number,
                        "location_desc": rec.location_desc,
                        "surrounding_text": rec.surrounding_text,
                        "document_type": rec.document_type,
                        "entity_hint": rec.entity_hint
                    })

            except Exception as e:
                logs.append(f"ERROR: Failed to extract from {fpath.name}: {str(e)}")
                inventory.append({
                    "file_id": file_id,
                    "filename": fpath.name,
                    "file_path": str(fpath),
                    "file_type": file_type,
                    "file_size_bytes": file_stat.st_size,
                    "records_count": 0,
                    "status": "ERROR",
                    "error": str(e)
                })

        duration_ms = int((time.time() - start_time) * 1000)
        logs.append(f"Discovery phase completed in {duration_ms}ms. Total inventory count: {len(all_records)} elements.")

        return {
            "current_phase": "CONTEXT_ANALYSIS",
            "file_inventory": inventory,
            "discovered_records": all_records,
            "audit_logs": [{
                "agent_name": self.name,
                "action": "DOCUMENT_DISCOVERY_COMPLETED",
                "details": f"Inventoried {len(inventory)} files and extracted {len(all_records)} candidate fields."
            }],
            "agent_executions": {
                self.name: {
                    "status": "COMPLETED",
                    "task_description": f"Extracted document metadata and structured records across {len(inventory)} files.",
                    "execution_duration_ms": duration_ms,
                    "findings_count": len(all_records),
                    "logs": logs
                }
            }
        }
