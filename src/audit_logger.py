"""
FinPilot AI — Persistent Audit Logging Engine
Stores user interactions, approval decisions, dataset uploads, and system events
to local JSON storage for compliance and auditability.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any


class AuditLogger:
    def __init__(self, log_filepath: str = "data/audit_log.json"):
        self.log_filepath = log_filepath
        self._ensure_log_file_exists()

    def _ensure_log_file_exists(self):
        """Creates data folder and initial JSON file if missing."""
        os.makedirs(os.path.dirname(self.log_filepath), exist_ok=True)
        if not os.path.exists(self.log_filepath):
            initial_entry = [{
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "event": "Audit Log Engine Initialized",
                "status": "Success",
                "user": "System"
            }]
            with open(self.log_filepath, "w", encoding="utf-8") as f:
                json.dump(initial_entry, f, indent=4)

    def log_event(self, event: str, status: str = "Success", user: str = "SME Admin") -> Dict[str, Any]:
        """Appends a new audit event and updates disk storage."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": event,
            "status": status,
            "user": user
        }
        logs = self.get_all_logs()
        logs.append(entry)

        with open(self.log_filepath, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=4)

        return entry

    def get_all_logs(self) -> List[Dict[str, Any]]:
        """Reads all historical audit records."""
        try:
            with open(self.log_filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []


if __name__ == "__main__":
    print("--- Testing Audit Logger Engine ---")
    logger = AuditLogger()
    logger.log_event("Test Verification Action Approved", status="Approved")
    all_logs = logger.get_all_logs()
    print(f"Total Persistent Logs Recorded: {len(all_logs)}")
    print("Latest Record:", all_logs[-1])