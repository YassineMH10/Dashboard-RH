# modules/preprocessing.py

import pandas as pd

def calcul_ecarts_objectifs(df_resultats, df_objectifs, params):
    kpis = params["kpi"]
    agents = params["agents"]
    mois = params["mois"]

    df_type = df_objectifs[df_objectifs["Mois"] == "Type"]
    df_objectifs = df_objectifs[df_objectifs["Mois"] != "Type"]

    type_obj = {k: df_type.iloc[0][k].strip().lower() for k in kpis}

    df_r = df_resultats[df_resultats["Agent"].isin(agents) & df_resultats["Mois"].isin(mois)]
    df_o = df_objectifs[df_objectifs["Mois"].isin(mois)]

    df = df_r.merge(df_o, on="Mois", suffixes=("", "_obj"))
    rows = []

    for _, row in df.iterrows():
        entry = {"Agent": row["Agent"], "Mois": row["Mois"]}
        for kpi in kpis:
            val = row[kpi]
            obj = row[f"{kpi}_obj"]
            type_kpi = type_obj[kpi]

            if obj == 0:
                ecart = 0
            elif type_kpi == "min":
                ecart = (val - obj) / obj
            elif type_kpi == "max":
                ecart = (obj - val) / obj
            else:  # "target"
                ecart = (val - obj) / obj

            entry[f"Ecart_{kpi}"] = round(ecart, 4)

        rows.append(entry)

    df_ecarts = pd.DataFrame(rows)

    for kpi in kpis:
        df_ecarts[f"Pond_{kpi}"] = df_ecarts[f"Ecart_{kpi}"] * params["pondérations"][kpi]

    df_ecarts["Score_Global"] = df_ecarts[[f"Pond_{k}" for k in kpis]].sum(axis=1)

    return df_ecarts
