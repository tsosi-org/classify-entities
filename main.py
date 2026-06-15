import pandas as pd, json, requests
from modules import *


today_date = pd.Timestamp.today().strftime("%Y-%m-%d")


## ___1___ load data from TSOSI.org and classified entities


## get new entities
raw_entities = requests.get("https://tsosi.org/api/entities/all?format=json").json()

## flatten entities
[flatten_entities(item) for item in raw_entities]

df_raw  = pd.json_normalize(raw_entities)
## add tsosi_link field
df_raw["tsosi_link"] = "https://tsosi.org/entities/" + df_raw["id"].astype(str)

print(f"nb of entities {len(df_raw)}")

## remove entities already classified
df_known_entities = pd.read_csv("TSOSI-classified-entities.csv", encoding="utf-8")
print(f"nb of entities classified {len(df_known_entities)}")

#print(df_known_entities.columns)


## ___2___ remove known entities

# get sets of ROR and wiki id (dropna to avoid matching NaN)
known_ror = df_known_entities["ror_id"].dropna().unique()
known_wiki = df_known_entities["wiki_id"].dropna().unique()

mask = ~(
	df_raw["ror_id"].isin(known_ror) |
    df_raw["wiki_id"].isin(known_wiki)
)

df_new_entities = df_raw[mask].reset_index(drop=True)
print(f"nb of unknow entities {len(df_new_entities)}")


## ___3___ find new intermediary
df_intermed = df_new_entities[df_new_entities["is_agent"] == True ][["name", "country","ror_id", "wiki_id", "tsosi_link" ]].reset_index(drop=True)


if not df_intermed.empty: 
	## JSON output have problem with \ char so repalce is added
	verif_intermed = df_intermed.to_json(orient="records", force_ascii=False, indent=2).replace(r"\/", "/")
	with open(f"{today_date}--new-intermediaries.json", "w", encoding="utf-8") as temp_file:
		temp_file.write(verif_intermed)
	print(f"ToDo verify new intermed (n={len(df_intermed)})\t{today_date}--new-intermediaries.json")



# ___4___ find new funder

## enrich entities w ROR types
# df_new_entities["ror_types"] = df_new_entities.apply(
#     lambda x: get_ror_types(x["ror_id"]) if pd.notna(x["ror_id"]) else "",
#     axis=1
# )

df_new_entities = pd.read_csv("temp--new-entity-w-ror-types.csv", encoding="utf-8")
#df_new_entities.to_csv("temp--new-entity-w-ror-types.csv", index = False)

df_funders = df_new_entities[["name", "short_name", "country", "ror_id", "ror_types", "id", "tsosi_link"]].copy()

mask_gov = df_funders["ror_types"].str.contains(r"\bgovernment\b", case=False, na=False)
mask_funder = df_funders["ror_types"].str.contains(r"\bfunder\b", case=False, na=False)
mask_nonprofit = df_funders["ror_types"].str.contains(r"\bnonprofit\b", case=False, na=False)



df_possible_funders = df_funders[ mask_gov | (mask_funder & mask_nonprofit) ].reset_index(drop=True)
df_possible_funders.drop_duplicates(subset=["id"], keep="first", inplace = True)
print(len(df_possible_funders))

if not df_possible_funders.empty: 
	## JSON output have problem with \ char so repalce is added
	df_possible_funders_json  = df_possible_funders.to_json(orient="records", force_ascii=False, indent=2).replace(r"\/", "/")
	
	with open(f"{today_date}--new-funders.json", "w", encoding="utf-8") as temp_file:
		temp_file.write(df_possible_funders_json )

	print(f"\n\nToDo verify new funders (n={len(df_possible_funders)}):\t{today_date}--new-funders.json")


