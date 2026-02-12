import os

try:
    import dash
    from dash import dcc, html
    import plotly.express as px
    import pandas as pd
except ImportError as exc:
    raise SystemExit("Dash/Plotly not installed. Run: pip install dash plotly pandas") from exc

DATA_PATH = os.getenv("DASH_DATA_PATH", "phase2_shap_top3_fold1.csv")

df = pd.read_csv(DATA_PATH)
fig = px.histogram(df, x="score_1", nbins=30, title="Top-1 SHAP Score Distribution")

app = dash.Dash(__name__)
app.layout = html.Div(
    children=[
        html.H2("Risk Intervention Dashboard (Dash Stub)"),
        dcc.Graph(figure=fig),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
