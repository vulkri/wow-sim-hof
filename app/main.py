import os
import uuid
import datetime
from typing import Any
from urllib.parse import unquote

import starlette.status as status
from sqlalchemy.orm import Session

from fastapi import Body, Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sim import sim_it
from chksum import parse_simc_string
from database import engine, SessionLocal
from blizz_api import get_blizz_data
import models



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add new entry or update existing one after running quick sim
def update_leaderboard(entry_data: dict, db: Session) -> models.LeaderboardEntry:
    new_entry = False
    current_entry = db.query(models.LeaderboardEntry).filter(models.LeaderboardEntry.char_name==entry_data["char_name"]).one_or_none()

    if not current_entry:
        new_entry = True
        entry = models.LeaderboardEntry
        current_entry = db.add(entry(**entry_data))
    else:
        for key, value in entry_data.items():
            setattr(current_entry, key, value)
        
    db.commit()
    if not new_entry: 
        db.refresh(current_entry)
    
    return current_entry


# Read leaderboard entries
def read_leaderboard(db: Session) -> dict:
    entries = db.query(models.LeaderboardEntry).order_by(models.LeaderboardEntry.dps.desc()).all()
    entries_dict = [{column.name: getattr(row, column.name) for column in models.LeaderboardEntry.__table__.columns} for row in entries]
    return entries_dict


@app.get("/hampter/", response_class=HTMLResponse)
async def show_hampter(request: Request):

    return templates.TemplateResponse(
        request=request, name="hampter.html"
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session=Depends(get_db)):
    leaderboard = read_leaderboard(db)
    new_leaderboard = []

    for i, entry in enumerate(leaderboard, start=1):
        entry["pos"] = i
        new_leaderboard.append(entry)

    context = {"leaderboard": new_leaderboard}

    return templates.TemplateResponse(
        request=request, name="index.html", context=context
    )


@app.get("/sim/", response_class=HTMLResponse)
def sim_character_import(request: Request):
    context = {"request": request}

    return templates.TemplateResponse(
        name="sim.html", context=context
    )


@app.post("/sim/", response_class=HTMLResponse)
async def start_quick_sim(request: Request, 
                    payload: Any = Body(None), 
                    db: Session=Depends(get_db)
                    ):
    context = {"request": request}
    dps = False

    if not payload:
        return templates.TemplateResponse(
        name="sim.html", context=context
    )

    payload = payload.decode("utf-8").split("=")

    # TODO error handling (front's doing validation anyway)
    if payload[0] == "char_name":
        char_name = payload[1]
        profile = get_blizz_data(char_name)
        if "error" in profile.keys():
            return RedirectResponse(url="/sim/", status_code=status.HTTP_302_FOUND)
        if profile["name"]:
            dps = await sim_it(name = profile["name"])   

    if payload[0] == "simc_string":
        simc_string = unquote(payload[1])
        parsed_simc = parse_simc_string(simc_string=simc_string)
        if not parsed_simc:
            return RedirectResponse(url="/sim/", status_code=status.HTTP_302_FOUND)
        
        profile = get_blizz_data(parsed_simc["character_name"])
        if "error" in profile.keys():
            return RedirectResponse(url="/sim/", status_code=status.HTTP_302_FOUND)

        filename = "simc_profiles/" + str(uuid.uuid4()) + ".simc"
        with open (filename, 'w') as f:
            f.write(simc_string)
        dps = await sim_it(simc_filename=filename)

        os.remove(filename)   

    if dps:
        context["dps"] = dps
        context["item_level"] = profile["equipped_item_level"]
        entry_data = {
            "char_name": profile["name"],
            "dps": context["dps"],
            "item_level": profile["equipped_item_level"],
            "last_sim": datetime.datetime.now()
        }
        update_leaderboard(entry_data, db)

    return templates.TemplateResponse(
        name="/partials/quick_sim_score.html", context=context
    )


@app.get("/sim/check-name/", response_class=PlainTextResponse)
async def check_char_name(request: Request, char_name):
    profile = get_blizz_data(char_name)
    if "error" in profile.keys():
        return profile["error"]
    
    return "ok"


@app.post("/sim/check-simc-string/", response_class=PlainTextResponse)
async def check_simc_string(request: Request, payload: Any = Body(None)):
    simc_string = payload.decode("utf-8")
    parsed_simc = parse_simc_string(simc_string=simc_string)
    if not parsed_simc:
        return "ok"

    profile = get_blizz_data(parsed_simc["character_name"])
    if "error" in profile.keys():
        return profile["error"]
    
    return "ok"