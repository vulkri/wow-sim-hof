import os
from dotenv import load_dotenv
from blizzardapi import BlizzardApi

load_dotenv()
API_ID = os.getenv("API_ID")
API_KEY = os.getenv("API_KEY")
blzapi_client = BlizzardApi(API_ID, API_KEY)
# Create apikey.txt with current api id and secret
with open("apikey.txt", "w+") as f:
    f.write(API_ID+":"+API_KEY)

names_whitelist = ("Eilysa", "Eilyss", "Eilyssa",)

# Get character data from blizz api
# We're supporting only characters from guild Horde of Hamsters, burning-legion realm
def get_blizz_data(char_name: str):
    char_profile = blzapi_client.wow.profile.get_character_profile_summary("eu", "en_GB", "burning-legion", char_name.lower())

    if "code" in char_profile.keys() and char_profile["code"] == 404:
        return {"error": "Character not found"}
    if (("guild" not in char_profile.keys() or char_profile["guild"]["name"] != "Horde of Hamsters") and 
        char_profile["name"] not in names_whitelist):
        return {"error": "Character's in the wrong guild"}
    
    profile = {
        "name": char_profile["name"],
        "equipped_item_level": char_profile["equipped_item_level"],
        "char_class": char_profile["character_class"]["name"],
        "specialization_name": char_profile["active_spec"]["name"],
        "specialization_id": char_profile["active_spec"]["id"]
    }
    
    return profile
