# vtf_app/views/process_view.py
from textual.widgets import DataTable, Static
from textual.app import ComposeResult
from typing import List, Dict, Any

class ProcessView(Static):
    def compose(self) -> ComposeResult:
        table = DataTable()
        table.cursor_type = "row"
        yield table

    def show_data(self, data: List[Dict[str, Any]]):
        print(f"ProcessView.show_data called with {len(data)} rows")
        table = self.query_one(DataTable)
        print(f"Found table: {table}")
        table.clear(columns=True)

        display_names = ["PID", "PPID", "Process", "Offset(V)", "Threads", "Handles", "Create Time"]
        for name in display_names:
            table.add_column(name, key=name)
        print(f"Added {len(display_names)} columns")
        
        json_keys = ["PID", "PPID", "ImageFileName", "Offset(V)", "Threads", "Handles", "CreateTime"]
        
        row_count = 0
        for row_data in data:
            cells = [str(row_data.get(key, 'N/A')) for key in json_keys]
            table.add_row(*cells, key=str(row_data.get("Offset(V)")))
            row_count += 1
        
        print(f"Added {row_count} rows to table")
        print(f"Table now has {table.row_count} rows and {len(table.columns)} columns")
        table.refresh()
        self.refresh()
        print("ProcessView refreshed")