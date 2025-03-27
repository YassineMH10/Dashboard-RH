# modules/exports.py

import pandas as pd
import io

def export_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name="Données KPI", index=False)
    buffer.seek(0)
    return buffer
