import pandas as pd, json, requests
from modules import *


today_date = pd.Timestamp.today().strftime("%Y-%m-%d")


## ___1___ load data from TSOSI.org 

## get new entities
raw_entities = requests.get("https://tsosi.org/api/entities/all?format=json").json()

## flatten entities
[flatten_entities(item) for item in raw_entities]

df_raw  = pd.json_normalize(raw_entities)

## 2026-06-20 field types correspond to ror_types, make it explicit
if "types" in df_raw.columns : 
	df_raw.rename(columns={'types': 'ror_types'}, inplace=True) 

## add tsosi_link field
df_raw["tsosi_link"] = "https://tsosi.org/entities/" + df_raw["id"].astype(str)

print(f"nb of entities {len(df_raw)}")


## ___2___ remove known entities
df_known_entities = pd.read_csv("TSOSI-classified-entities.csv", encoding="utf-8")
print(f"nb of entities classified {len(df_known_entities)}")

#print(df_known_entities.columns)

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

# print(len(df_intermed))

if not df_intermed.empty: 

	md_output = df_to_custom_markdown(df_intermed, "md")
	with open(f"{today_date}--new-intermediaries.md", "w", encoding="utf-8") as temp_file: 
		temp_file.write(md_output)
	print(f"ToDo verify new intermed (n={len(df_intermed)})\t{today_date}--new-intermediaries.md")


# ___4___ find new funder


df_funders = df_new_entities[["name", "short_name", "country", "ror_id", "ror_types", "id", "tsosi_link"]].copy()


# deal with ror_types to use it as a list 
def norm_list(lst):
    if not isinstance(lst, (list, tuple)):
        return []
    return [str(item).strip().lower() for item in lst]
parsed = df_funders["ror_types"].apply(norm_list)

mask_gov = parsed.apply(lambda lst: "government" in lst)
mask_funder = parsed.apply(lambda lst: ("funder" in lst) & ("nonprofit" in lst))


df_possible_funders = df_funders[ mask_gov | mask_funder ].reset_index(drop=True)
df_possible_funders.drop_duplicates(subset=["id"], keep="first", inplace = True)
print(f"nb of possible funder\t {len(df_possible_funders)}")


if not df_possible_funders.empty: 

	md_output = df_to_custom_markdown(df_possible_funders, "md")
	with open(f"{today_date}--new-funders.md", "w", encoding="utf-8") as temp_file: 
		temp_file.write(md_output)
	print(f"ToDo verify new funders (n={len(df_possible_funders)})\t{today_date}--new-funders.md")



exit()

mask_gov = df_funders["ror_types"].str.contains(r"\bgovernment\b", case=False, na=False)
mask_funder = df_funders["ror_types"].str.contains(r"\bfunder\b", case=False, na=False)
mask_nonprofit = df_funders["ror_types"].str.contains(r"\bnonprofit\b", case=False, na=False)

df_possible_funders = df_funders[ mask_gov | (mask_funder & mask_nonprofit) ].reset_index(drop=True)
df_possible_funders.drop_duplicates(subset=["id"], keep="first", inplace = True)
print(f"nb of possible funder\t {len(df_possible_funders)}")


if not df_possible_funders.empty: 

	md_output = df_to_custom_markdown(df_possible_funders, "md")
	with open(f"{today_date}--new-funders.md", "w", encoding="utf-8") as temp_file: 
		temp_file.write(md_output)
	print(f"ToDo verify new funders (n={len(df_possible_funders)})\t{today_date}--new-funders.md")



# if not df_possible_funders.empty: 
# 	## JSON output have problem with \ char so repalce is added
# 	df_possible_funders_json  = df_possible_funders.to_json(orient="records", force_ascii=False, indent=2).replace(r"\/", "/")
	
# 	with open(f"{today_date}--new-funders.json", "w", encoding="utf-8") as temp_file:
# 		temp_file.write(df_possible_funders_json )

# 	print(f"\n\nToDo verify new funders (n={len(df_possible_funders)}):\t{today_date}--new-funders.json")


