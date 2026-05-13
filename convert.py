import sys
try:
    import pandas as pd
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
    import pandas as pd

df = pd.read_excel("local_llm_hardware_options_ledger.xlsx")
df.to_csv("local_llm_hardware_options_ledger.csv", index=False)
