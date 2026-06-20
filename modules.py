import requests, pandas as pd

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


def df_to_custom_markdown(df, out_format):
    """
    export df as md
    Expected columns: name, country, ror_id, wiki_id, tsosi_link
    """

    if out_format != "md" : 
        pass

    lines = []
    for _, row in df.iterrows():
        name = row.get("name", "")
        country = row.get("country", "")
        ror = row.get("ror_id", None)
        wiki = row.get("wiki_id", None)
        ror_types = row.get("ror_types", None)
        tsosi_link = row.get("tsosi_link", None)

        # First line: bold name and country in parentheses
        first = f"**{name}** ({country})" if country and not pd.isna(country) else f"**{name}**"
        entry_lines = [first]

        # Optional lines if present and not NaN/empty
        if ror is not None and not (pd.isna(ror) or str(ror).strip() == ""):
            ror_url = str("https://ror.org/" + ror)
            entry_lines.append(f"[{ror_url}]({ror_url})")
        
        if wiki is not None and not (pd.isna(wiki) or str(wiki).strip() == ""):
            entry_lines.append(str(wiki))
        
        if ror_types :
            ror_types_str = str(",".join(ror_types))
            entry_lines.append(ror_types_str)

        if tsosi_link is not None and not (pd.isna(tsosi_link) or str(tsosi_link).strip() == ""):
            url = str(tsosi_link).strip()
            # make link clickable
            entry_lines.append(f"[{url}]({url})")

        lines.append("\n".join(entry_lines))

    return "\n\n".join(lines)



def get_ror_types(ror_id) :
    """
    return the ror types of the entity as string seperated with comma
    2026-06-20 : unused, ror_types have been added to the API
    """
    ror_data = requests.get(f"https://api.ror.org/v2/organizations/{ror_id}").json()
    if ror_data.get("types") : 
        return ", ".join(ror_data.get("types"))

