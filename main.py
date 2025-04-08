from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import json
from datetime import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from typing import List, Optional
import uvicorn
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")
DATA_FILE = "data/data.json"


def load_data() -> List[dict]:
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_data(data: List[dict]):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def create_plot(data: List[dict], show_glucose=True, show_uric=True):
    dates = [datetime.strptime(d["date"], "%Y-%m-%d").strftime("%Y-%m-%d") for d in data]
    glucose = [d["glucose"] for d in data]
    uric = [d["uric_acid"] for d in data]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if show_glucose:
        fig.add_trace(
            go.Scatter(
                x=dates, y=glucose, name="血糖 (mmol/L)", mode="lines+markers",
                marker=dict(symbol='circle', size=10, color='blue')
            ),
            secondary_y=False,
        )
    if show_uric:
        fig.add_trace(
            go.Scatter(
                x=dates, y=uric, name="尿酸 (μmol/L)", mode="lines+markers",
                marker=dict(symbol='circle', size=5, color='red'),
            ),
            secondary_y=True,
        )

    fig.update_layout(title="血糖 & 尿酸 变化图", height=500)
    fig.update_yaxes(title_text="血糖 (mmol/L)", secondary_y=False)
    fig.update_yaxes(title_text="尿酸 (μmol/L)", secondary_y=True)

    return fig.to_html(full_html=False, include_plotlyjs="cdn")


@app.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        show_glucose: Optional[str] = None,
        show_uric: Optional[str] = None,
):
    data = sorted(load_data(), key=lambda x: x["date"])
    show_glucose_flag = show_glucose is not None
    show_uric_flag = show_uric is not None
    plot_html = create_plot(data, show_glucose_flag, show_uric_flag)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "plot_div": plot_html,
        "show_glucose": show_glucose_flag,
        "show_uric": show_uric_flag
    })


@app.post("/add")
async def add_data(
        date: str = Form(...),
        glucose: float = Form(...),
        uric_acid: float = Form(...)
):
    data = load_data()
    data.append({
        "date": date,
        "glucose": glucose,
        "uric_acid": uric_acid
    })
    data = sorted(data, key=lambda x: x["date"])
    save_data(data)
    return RedirectResponse("/", status_code=303)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)