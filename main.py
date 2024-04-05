from subprocess import Popen, PIPE, CalledProcessError
import subprocess
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from blizzardapi import BlizzardApi


app = FastAPI()

templates = Jinja2Templates(directory="templates")

blzapi_client = BlizzardApi("7ce044fe2c414253b5f7c19fa9538181", "qlei4yrlDDfJSiNpoOA4NxZSERsGE9xY")

simc = "./simc_bin"

def sim_it(name):
    args = " armory=eu,burning-legion," + name
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

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/sim/", response_class=HTMLResponse)
async def read_root(request: Request, name: str | None = None):
    context = {"request": request}
    dps = False
    if name:
        char_profile = blzapi_client.wow.profile.get_character_profile_summary("eu", "en_GB", "burning-legion", name.lower())
        profile = {
            "name": char_profile["name"],
            "guild": char_profile["guild"]
        }
        context["profile"] = profile
        if profile["name"]:
            dps = sim_it(profile["name"])            

    if dps:
        context["dps"] = dps
        return templates.TemplateResponse(
            name="sim.html", context=context
        )
    return templates.TemplateResponse(
        name="sim.html", context=context
    )