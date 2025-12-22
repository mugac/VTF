from textual.widgets import DataTable, Static
from textual.app import ComposeResult
from typing import List, Dict, Any

class ProcessTable(Static):
    def compose(self) -> ComposeResult:
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        display_names = ["PID", "PPID", "Process", "Offset(V)", "Threads", "Handles", "Create Time"]
        for name in display_names:
            table.add_column(name, key=name)

    def populate_data(self, data: List[Dict[str, Any]]):
        table = self.query_one(DataTable)
        table.clear()

        json_keys = [
            "PID", 
            "PPID", 
            "ImageFileName", 
            "Offset(V)",
            "Threads", 
            "Handles",
            "CreateTime"
        ]
        
        for row_data in data:
            cells = [str(row_data.get(key, 'N/A')) for key in json_keys]
            
            # =========== FINÁLNÍ OPRAVA ZDE ===========
            # Jako unikátní klíč použijeme Offset(V), který je vždy unikátní.
            table.add_row(*cells, key=str(row_data.get("Offset(V)")))
            # ==========================================```
