import random

from fastapi import Body, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.utils import classify_me_why

app = FastAPI()
app.mount("/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    # load a random example text
    with open(f"src/assets/example_text_{random.randint(1, 9)}.txt") as f:
        example_text = f.read().strip()
    return templates.TemplateResponse("index.html", {"request": request, "example_text": example_text})


@app.post("/", response_class=HTMLResponse)
def post_index(request: Request, text: str = Form(), label: str = Form()):
    # load a random example text
    with open(f"src/assets/example_text_{random.randint(1, 9)}.txt") as f:
        example_text = f.read().strip()
    # classify text if given
    if not text:
        pred_class, pred_score, htmlstr = "-", 0.0, "ERROR: You have to enter some text below..."
    else:
        pred_class, pred_score, htmlstr = classify_me_why(text, label)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "example_text": example_text,
            "pred_class": pred_class,
            "pred_score": pred_score,
            "text_div": htmlstr,
        },
    )


@app.post("/classify")
def classify_text(text: str = Body(), label: str = Body("keyword")):
    # classify text
    pred_class, pred_score, htmlstr = classify_me_why(text, label)
    return {"pred_class": pred_class, "pred_score": pred_score, "text_div": htmlstr}
