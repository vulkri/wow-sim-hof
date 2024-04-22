import os
from dotenv import load_dotenv
from blizzardapi import BlizzardApi

load_dotenv()

blzapi_client = BlizzardApi(os.getenv("API_ID"), os.getenv("API_KEY"))


# Get character data from blizz api
# We're supporting only characters from guild mordorownia, burning-legion realm
def get_blizz_data(char_name: str):
    char_profile = blzapi_client.wow.profile.get_character_profile_summary("eu", "en_GB", "burning-legion", char_name.lower())

    if "code" in char_profile.keys() and char_profile["code"] == 404:
        return {"error": "Character not found"}
    if "guild" not in char_profile.keys() or char_profile["guild"]["name"] != "Mordorownia":
        return {"error": "Character's in the wrong guild"}
    
    profile = {
        "name": char_profile["name"],
        "equipped_item_level": char_profile["equipped_item_level"],
        "char_class": char_profile["character_class"]["name"],
        "specialization_name": char_profile["active_spec"]["name"],
        "specialization_id": char_profile["active_spec"]["id"]
    }
    
    return profile