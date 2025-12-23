# vtf_app/app.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, ContentSwitcher, Static, Label
from textual.containers import Horizontal
from textual.worker import Worker, WorkerState

from .views.process_view import ProcessView
from .views.network_view import NetworkView
from .volatility_runner import run_volatility_plugin

class VTFApp(App):
    TITLE = "Volatility Terminal Frontend (VTF)"
    CSS_PATH = "main.css"

    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_cache = {}
        self.current_view = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main-container"):
            yield ListView(id="nav-list")
            with ContentSwitcher(id="content-switcher"):
                yield ProcessView(id="processes")
                yield NetworkView(id="network")
        yield Footer()

    def on_mount(self) -> None:
        nav_list = self.query_one("#nav-list", ListView)
        nav_list.append(ListItem(Label("Processes")))
        nav_list.append(ListItem(Label("Network")))
        nav_list.index = 0
        

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_text = event.item.children[0].render().plain.strip()
        
        if item_text == "Processes":
            self.switch_to_view("processes", "psscan", "windows.psscan.PsScan")
        elif item_text == "Network":
            self.switch_to_view("network", "netscan", "windows.netscan.NetScan")

    def switch_to_view(self, view_id: str, cache_key: str, plugin: str) -> None:
        content_switcher = self.query_one("#content-switcher", ContentSwitcher)
        content_switcher.current = view_id
        self.current_view = view_id
        
        if cache_key not in self.data_cache:
            self.sub_title = f"Loading {cache_key} data..."
            self.run_volatility_worker(cache_key, plugin)
        else:
            view = self.query_one(f"#{view_id}")
            view.show_data(self.data_cache[cache_key])
            self.sub_title = f"{cache_key.capitalize()} data loaded from cache. Found {len(self.data_cache[cache_key])} entries."
    def run_volatility_worker(self, cache_key: str, plugin: str) -> None:
        image_path = "image.vmem"

        def volatility_task():
            return run_volatility_plugin(image_path, plugin)
        
        self.run_worker(
            volatility_task,
            name=cache_key,
            group="volatility_tasks",
            exclusive=True,
            thread=True
        )
   

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            cache_key = event.worker.name
            result_data = event.worker.result
            print(f"Worker '{cache_key}' completed with {len(result_data)} entries.")
            self.data_cache[cache_key] = result_data

            target_view_id = None
            if cache_key == "psscan":
                target_view_id = "processes"
            elif cache_key == "netscan":
                target_view_id = "network"

            active_view_id = self.query_one(ContentSwitcher).current
            print(f"Active view: {active_view_id}, Target view: {target_view_id}")
            if active_view_id == target_view_id:
                view_widget = self.query_one(f"#{target_view_id}")
                print(f"Found view widget: {view_widget}")
                if result_data:
                    print(f"Calling show_data with {len(result_data)} entries")
                    view_widget.show_data(result_data)
                    self.sub_title = f"Analysis complete. Found {len(result_data)} entries."
                else:
                    self.sub_title = f"Analysis complete, but no data found for {cache_key}."
        
        elif event.state == WorkerState.ERROR:
            self.sub_title = "Worker failed. See console for details."

