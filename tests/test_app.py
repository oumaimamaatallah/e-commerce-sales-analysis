from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_dashboard_runs_and_filters_change_totals():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not app.exception
    initial = app.metric[0].value
    app.multiselect(key="countries").set_value(["Germany"]).run()
    assert not app.exception
    assert app.metric[0].value != initial
    assert len(app.get("plotly_chart")) >= 5


def test_empty_filter_selection_is_handled():
    app = AppTest.from_file(str(APP), default_timeout=30).run()
    app.multiselect(key="categories").set_value([]).run()
    assert not app.exception
    assert any("No records" in item.value for item in app.info)
