import subprocess
import json
from typing import List, Dict, Any

def run_volatility_plugin(image_path: str, plugin_name: str) -> List[Dict[str, Any]]:
    """
    Spustí zadaný Volatility 3 plugin a vrátí jeho výstup jako JSON.
    """
    command = [
        "vol.exe",
        "-r", "json",
        "-f", image_path,
        plugin_name,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            print(f"CHYBA: Volatility skončila s chybovým kódem {result.returncode}.")
            print(f"STDERR: {result.stderr}")
            return []

        stdout = result.stdout
        json_start_index = stdout.find('[')
        
        if json_start_index == -1:
            return []
            
        json_data = json.loads(stdout[json_start_index:])
        return json_data

    except Exception as e:
        print(f"CHYBA: Neočekávaná chyba při spouštění pluginu: {e}")
        return []