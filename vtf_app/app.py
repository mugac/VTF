# vtf_app/app.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.worker import Worker, WorkerState

from .widgets.process_table import ProcessTable
from .volatility_runner import run_volatility_plugin

class VTFApp(App):
    TITLE = "Volatility Terminal Frontend (VTF)"
    CSS_PATH = "main.css"

    BINDINGS = [
        ("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield ProcessTable(id="process_table")
        yield Footer()

    def on_mount(self) -> None:
        self.run_volatility_worker()

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        if event.state == WorkerState.SUCCESS:
            process_data = event.worker.result
            if process_data:
                table_widget = self.query_one(ProcessTable)
                table_widget.populate_data(process_data)
                self.sub_title = f"Analysis complete. Found {len(process_data)} processes."
            else:
                self.sub_title = "Analysis complete, but no processes were found."
        elif event.state == WorkerState.ERROR:
            self.sub_title = "Worker failed. See console for details."

    def run_volatility_worker(self) -> None:
        image_path = "image.vmem"
        plugin = "windows.psscan.PsScan"
        
        self.sub_title = f"Analyzing {plugin} on {image_path}..."

        def volatility_task():
            """Pomocná funkce, která se spustí na pozadí."""
            return run_volatility_plugin(image_path, plugin)

        # Spustíme worker s explicitním příznakem, že jde o thread
        self.run_worker(
            volatility_task,
            name="Volatility Runner",
            group="volatility_tasks",
            exclusive=True,
            thread=True  # <-- TOTO JE KLÍČOVÁ A FINÁLNÍ OPRAVA
        )