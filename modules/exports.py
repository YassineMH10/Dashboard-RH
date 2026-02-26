# modules/exports.py
import pandas as pd
import io
from modules.pda_store import load_actions


def export_excel(df):
    buffer = io.BytesIO()
    actions = load_actions()
    df_actions = pd.DataFrame(actions) if actions else pd.DataFrame()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Données KPI", index=False)
        df_actions.to_excel(writer, sheet_name="PDA", index=False)

    buffer.seek(0)
    return buffer
