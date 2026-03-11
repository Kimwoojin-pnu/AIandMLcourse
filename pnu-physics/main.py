import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="PNU Physics Department")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Data directory
DATA_DIR = Path("data")


def load_json(filename: str) -> list:
    with open(DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    faculty = load_json("faculty.json")
    research = load_json("research.json")
    news = load_json("news.json")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "faculty": faculty,
            "research": research,
            "news": news,
            "stats": {
                "professors": len(faculty),
                "papers": sum(r.get("papers", 0) for r in research),
                "research_groups": len(research),
                "years": 60,
            },
        },
    )


@app.get("/api/faculty")
async def get_faculty():
    return load_json("faculty.json")


@app.get("/api/research")
async def get_research():
    return load_json("research.json")


@app.get("/api/news")
async def get_news():
    return load_json("news.json")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
