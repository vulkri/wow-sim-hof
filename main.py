import subprocess
from blizzardapi import BlizzardApi
from sqlalchemy.orm import Session
import datetime
from typing import Any
import json

from fastapi import Body, Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates

from database import SessionLocal, engine
import models



app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

models.Base.metadata.create_all(bind=engine)

blzapi_client = BlizzardApi("7ce044fe2c414253b5f7c19fa9538181", "qlei4yrlDDfJSiNpoOA4NxZSERsGE9xY")

simc = "./simc_bin"



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_blizz_data(char_name: str):
    char_profile = blzapi_client.wow.profile.get_character_profile_summary("eu", "en_GB", "burning-legion", char_name.lower())

    if "guild" not in char_profile.keys() or char_profile["guild"]["name"] != "Mordorownia":
        return {"error": "wrong guild"}
    profile = {
        "name": char_profile["name"],
        "equipped_item_level": char_profile["equipped_item_level"]
    }
    return profile


async def sim_it(name: str = None, profile_filename: str = None):
    if name:
        args = " armory=eu,burning-legion," + name
    if profile_filename:
        args = " " + profile_filename

    cmd = simc + args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()

    p_status = p.wait()
    if p_status != 0:
        return
    output_text = output.splitlines()
    dps_next = False
    for line in output_text:
        if dps_next:
            dps = line.split()[0].decode("utf-8")
            break
        if line.startswith(b"DPS Ranking:"):
            dps_next = True

    return dps


def update_leaderboard(entry_data: dict, db: Session):
    new_entry = False
    current_entry = db.query(models.LeaderboardEntry).filter(models.LeaderboardEntry.char_name==entry_data["char_name"]).one_or_none()

    if not current_entry:
        new_entry = True
        entry = models.LeaderboardEntry

    if new_entry:
        current_entry = db.add(entry(**entry_data))
    else:
        for key, value in entry_data.items():
            setattr(current_entry, key, value)
        

    db.commit()
    if not new_entry: 
        db.refresh(current_entry)
    
    return current_entry


@app.get("/hampter/", response_class=HTMLResponse)
async def read_root(request: Request):

    return templates.TemplateResponse(
        request=request, name="hampter.html"
    )


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    return templates.TemplateResponse(
        request=request, name="index.html"
    )


@app.get("/sim/", response_class=HTMLResponse)
def read_root(request: Request):
    context = {"request": request}

    return templates.TemplateResponse(
        name="sim.html", context=context
    )


@app.post("/sim/", response_class=HTMLResponse)
async def read_root(request: Request, 
                    payload: Any = Body(None), 
                    db: Session=Depends(get_db)
                    ):
    context = {"request": request}
    dps = False
    #context["dps"] = 200100
    #context["item_level"] = 487
    #return templates.TemplateResponse(
    #    name="/partials/quick_sim_score.html", context=context
    #)

    if not payload:
        return templates.TemplateResponse(
        name="sim.html", context=context
    )

    payload = payload.decode("utf-8").split("=")

    if payload[0] == "char_name":
        char_name = payload[1]

    profile = get_blizz_data(char_name)

    if profile["name"]:
        dps = await sim_it(profile["name"])            

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
async def read_root(request: Request, char_name):
    profile = get_blizz_data(char_name)
    if "error" in profile.keys():
        return profile["error"]
    
    return "ok"