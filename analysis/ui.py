import plotly.graph_objects as go
import streamlit as st

NAVY = "#1B314A"
TEAL = "#197873"
GOLD = "#D5A448"
COLORS = [TEAL, NAVY, GOLD, "#93B9B3", "#AD7D79", "#8B92AA"]


def setup(title, subtitle, icon):
    st.set_page_config(page_title=title, page_icon=icon, layout="wide")
    st.markdown("""<style>
    .block-container, [data-testid="stMainBlockContainer"] {padding-top:4.5rem !important; padding-bottom:2rem; max-width:1540px;}
    h1 {font-size:2.05rem !important; font-weight:650 !important; letter-spacing:-.04em;}
    h2, h3 {letter-spacing:-.025em;}
    [data-testid="stMetric"] {background:white; border:1px solid #E2E6EB; border-radius:9px;
        padding:18px 20px; border-top:3px solid #197873;}
    [data-testid="stMetricLabel"] {color:#596B7D; font-size:.8rem;}
    [data-testid="stMetricValue"] {font-size:1.85rem; font-weight:600; letter-spacing:-.03em;}
    [data-testid="stSidebar"] {border-right:1px solid #E2E6EB;}
    [data-testid="stTabs"] {margin-top:1rem;}
    [data-testid="stCaptionContainer"] {color:#637386;}
    [data-testid="stPlotlyChart"] {border:1px solid #E2E6EB; border-radius:9px; overflow:hidden;}
    </style>""", unsafe_allow_html=True)
    st.caption("OUMAIMA MAATALLAH  /  DATA PROJECTS")
    st.title(title)
    st.caption(subtitle)


def chart(fig, key=None, height=340):
    fig.update_layout(template="plotly_white", font={"family": "Arial", "size": 12, "color": NAVY},
                      colorway=COLORS, height=height, paper_bgcolor="white", plot_bgcolor="white",
                      margin={"l": 22, "r": 22, "t": 48, "b": 30},
                      title_font={"size": 15}, legend_title_text="", hovermode="closest")
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#EEF1F4", zeroline=False)
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False, "scrollZoom": False})


def metric_row(items):
    for column, (label, value, help_text) in zip(st.columns(len(items)), items):
        column.metric(label, value, help=help_text)


def money(value):
    return f"€{value:,.0f}"


def empty():
    st.info("No records in this selection. Widen the dates or reset the filters.")
    st.stop()
