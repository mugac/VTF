from textual.widgets import DataTable, Static
from textual.app import ComposeResult
from typing import List, Dict, Any

class NetworkView(Static):
    def compose(self) -> ComposeResult:
        table = DataTable()
        table.cursor_type = "row"
        yield table

    def show_data(self, data: List[Dict[str, Any]]):
        table = self.query_one(DataTable)
        table.clear(columns=True)

        display_names = ["Proto", "LocalAddr", "LocalPort", "ForeignAddr", "ForeignPort", "State", "PID", "Owner", "Created"]
        for name in display_names:
            table.add_column(name, key=name)


        json_keys = ["Proto", "LocalAddr", "LocalPort", "ForeignAddr", "ForeignPort", "State", "PID", "Owner", "Created"]
        
        for row_data in data:
            cells = [str(row_data.get(key, 'N/A')) for key in json_keys]

            offset = row_data.get("Offset", "N/A")
            proto = row_data.get("Proto", "").lower()
            if offset != "N/A" and proto in ["tcp", "udp"]:
                unique_key = f"{proto}_{offset}"
            else:
                unique_key = None
            if not unique_key:
                unique_key = str(row_data)

            table.add_row(*cells, key=unique_key)
        
        table.refresh()
        self.refresh()
