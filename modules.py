import requests
def get_ror_types(ror_id) :
    """
    return the ror types of the entity as string seperated with comma
    """
    ror_data = requests.get(f"https://api.ror.org/v2/organizations/{ror_id}").json()
    if ror_data.get("types") : 
        return ", ".join(ror_data.get("types"))


def flatten_entities(item) :
    """
    output one field per identifier ror_id and wiki_id
    """
    if item.get("identifiers") :
        for ids in item["identifiers"] : 
            if ids["registry"] == "ror" : 
                item["ror_id"] = ids["value"]
            if ids["registry"] == "wikidata" : 
                item["wiki_id"] = ids["value"]
        return item

    # memo to call [flatten_entities(item) for item in raw_entities]
