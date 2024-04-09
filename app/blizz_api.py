from blizzardapi import BlizzardApi


blzapi_client = BlizzardApi("7ce044fe2c414253b5f7c19fa9538181", "qlei4yrlDDfJSiNpoOA4NxZSERsGE9xY")


def get_blizz_data(char_name: str):
    char_profile = blzapi_client.wow.profile.get_character_profile_summary("eu", "en_GB", "burning-legion", char_name.lower())

    if "code" in char_profile.keys() and char_profile["code"] == 404:
        return {"error": "Character not found"}

    if "guild" not in char_profile.keys() or char_profile["guild"]["name"] != "Mordorownia":
        return {"error": "Character's in the wrong guild"}
    profile = {
        "name": char_profile["name"],
        "equipped_item_level": char_profile["equipped_item_level"]
    }
    return profile