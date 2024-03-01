#!/usr/bin/env python3.11
"""
Taking the xeno-canto db, let's process the occurrences and
multimedia files to construct a database of:

* A set of birds that exist in the UK/Ireland,
with an identifiable species key
* For each bird, a set of birdsongs
"""

import csv
import json
from typing import List, TypedDict

import requests


class Image(TypedDict):
    src: str
    rightsHolder: str


LOCATIONS = ["United Kingdom" or "Ireland"]

SPECIES_INFO_FIELDS = [
    "scientificName",
    "higherClassification",
    "kingdom",
    "phylum",
    "class",
    "order",
    "family",
    "genus",
    "vernacularName",
    "speciesKey",
]

OCCURRENCE_FIELDS = [
    "sex",
    "fieldNotes",
    "gbifID",
    "level0Name",
    "level1Name",
    "level2Name",
]

IMAGE_OVERRIDES: dict[str, Image] = {
    "7626513": {
        "src": "https://inaturalist-open-data.s3.amazonaws.com/photos/345397183/original.jpeg",
        "rightsHolder": "Antonio Rico García",
    },
    "2493084": {
        "src": "https://inaturalist-open-data.s3.amazonaws.com/photos/349694073/original.jpg",
        "rightsHolder": "Sourav Halder ",
    },
    # "2481240": "https://www.gbif.org/species/2481240",
    # "2474628": "https://www.gbif.org/species/2474628",
    # "2497921": "https://www.gbif.org/species/2497921",
    # "5229380": "https://www.gbif.org/species/5229380",
    # "5231438": "https://www.gbif.org/species/5231438",
    # "9274012": "https://www.gbif.org/species/9274012",
    # "2491482": "https://www.gbif.org/species/2491482",
    # "2487603": "https://www.gbif.org/species/2487603",
    # "2492963": "https://www.gbif.org/species/2492963",
    # "2493075": "https://www.gbif.org/species/2493075",
    # "7634625": "https://www.gbif.org/species/7634625",
    # "8000602": "https://www.gbif.org/species/8000602",
    # "7341522": "https://www.gbif.org/species/7341522",
    # "9465111": "https://www.gbif.org/species/9465111",
    # "9015784": "https://www.gbif.org/species/9015784",
    # "6100954": "https://www.gbif.org/species/6100954",
    # "2494177": "https://www.gbif.org/species/2494177",
    # "2474156": "https://www.gbif.org/species/2474156",
    # "2482492": "https://www.gbif.org/species/2482492",
    # "2490303": "https://www.gbif.org/species/2490303",
    # "8109681": "https://www.gbif.org/species/8109681",
    # "2497266": "https://www.gbif.org/species/2497266",
    # "2479329": "https://www.gbif.org/species/2479329",
    # "2494459": "https://www.gbif.org/species/2494459",
    # "9478399": "https://www.gbif.org/species/9478399",
    # "4408498": "https://www.gbif.org/species/4408498",
    # "4408455": "https://www.gbif.org/species/4408455",
    # "7341585": "https://www.gbif.org/species/7341585",
    # "8128385": "https://www.gbif.org/species/8128385",
    # "2473421": "https://www.gbif.org/species/2473421",
    # "2493145": "https://www.gbif.org/species/2493145",
    # "8144830": "https://www.gbif.org/species/8144830",
    # "2492959": "https://www.gbif.org/species/2492959",
    # "2482552": "https://www.gbif.org/species/2482552",
    # "2492965": "https://www.gbif.org/species/2492965",
    # "2492949": "https://www.gbif.org/species/2492949",
    # "2493095": "https://www.gbif.org/species/2493095",
    # "2491678": "https://www.gbif.org/species/2491678",
    # "2498338": "https://www.gbif.org/species/2498338",
    # "2490244": "https://www.gbif.org/species/2490244",
    # "7340170": "https://www.gbif.org/species/7340170",
    # "5231140": "https://www.gbif.org/species/5231140",
    # "8151548": "https://www.gbif.org/species/8151548",
    # "2498027": "https://www.gbif.org/species/2498027",
    # "2475443": "https://www.gbif.org/species/2475443",
    # "9317615": "https://www.gbif.org/species/9317615",
    # "2492542": "https://www.gbif.org/species/2492542",
    # "2482012": "https://www.gbif.org/species/2482012",
    # "2480506": "https://www.gbif.org/species/2480506",
    # "2490307": "https://www.gbif.org/species/2490307",
    # "2493070": "https://www.gbif.org/species/2493070",
    # "5227679": "https://www.gbif.org/species/5227679",
    # "5739361": "https://www.gbif.org/species/5739361",
    # "2490264": "https://www.gbif.org/species/2490264",
    # "2475235": "https://www.gbif.org/species/2475235",
    # "2473682": "https://www.gbif.org/species/2473682",
    # "2473577": "https://www.gbif.org/species/2473577",
    # "4408813": "https://www.gbif.org/species/4408813",
    # "2490728": "https://www.gbif.org/species/2490728",
    # "9415596": "https://www.gbif.org/species/9415596",
    # "7341805": "https://www.gbif.org/species/7341805",
    # "2492509": "https://www.gbif.org/species/2492509",
    # "10700636": "https://www.gbif.org/species/10700636",
    # "2494303": "https://www.gbif.org/species/2494303",
    # "8378494": "https://www.gbif.org/species/8378494",
    # "2490283": "https://www.gbif.org/species/2490283",
    # "2481221": "https://www.gbif.org/species/2481221",
    # "2493063": "https://www.gbif.org/species/2493063",
    # "5228034": "https://www.gbif.org/species/5228034",
    # "5739359": "https://www.gbif.org/species/5739359",
    # "5231646": "https://www.gbif.org/species/5231646",
    # "2493549": "https://www.gbif.org/species/2493549",
    # "2493071": "https://www.gbif.org/species/2493071",
    # "2479798": "https://www.gbif.org/species/2479798",
    # "2474627": "https://www.gbif.org/species/2474627",
    # "2480331": "https://www.gbif.org/species/2480331",
    # "2490263": "https://www.gbif.org/species/2490263",
    # "10731929": "https://www.gbif.org/species/10731929",
    # "2479311": "https://www.gbif.org/species/2479311",
    # "6065818": "https://www.gbif.org/species/6065818",
    # "2493090": "https://www.gbif.org/species/2493090",
    # "2480850": "https://www.gbif.org/species/2480850",
    # "2490277": "https://www.gbif.org/species/2490277",
    # "2491582": "https://www.gbif.org/species/2491582",
    # "4408827": "https://www.gbif.org/species/4408827",
    # "2495220": "https://www.gbif.org/species/2495220",
    # "9990095": "https://www.gbif.org/species/9990095",
    # "2498396": "https://www.gbif.org/species/2498396",
    # "2490281": "https://www.gbif.org/species/2490281",
    # "9584952": "https://www.gbif.org/species/9584952",
    # "2474162": "https://www.gbif.org/species/2474162",
    # "2480911": "https://www.gbif.org/species/2480911",
    # "5843955": "https://www.gbif.org/species/5843955",
    # "2479977": "https://www.gbif.org/species/2479977",
    # "5231244": "https://www.gbif.org/species/5231244",
    # "2481831": "https://www.gbif.org/species/2481831"
}

multimedia_dict = {}
data_dict = {}

if __name__ == "__main__":
    with open("multimedia.txt", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            if row["type"] == "Sound":
                multimedia_dict[row["gbifID"]] = row

    with open("occurrence.txt", encoding="utf-8") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            if row["level0Name"] not in LOCATIONS:
                continue

            if not row["speciesKey"]:
                continue

            species_key = row["speciesKey"]
            multimedia_match = multimedia_dict[row["gbifID"]]
            this_occurrence = {
                "__birdsong": multimedia_match["identifier"],
                "__license": multimedia_match["license"],
                "__rightsHolder": multimedia_match["rightsHolder"],
                **{field: row[field] for field in OCCURRENCE_FIELDS},
            }

            if species_key not in data_dict:
                data_dict[species_key] = {
                    field: row[field] for field in SPECIES_INFO_FIELDS
                }
                try:
                    response = requests.get(
                        f"https://api.gbif.org/v1/species/{species_key}/media",
                        timeout=5,
                    )
                    data_dict[species_key]["_pictures"] = [
                        {
                            "src": item["identifier"],
                            "rightsHolder": item["rightsHolder"],
                        }
                        for item in response.json()["results"]
                        if item["type"] == "StillImage"
                    ]
                except:  # pylint: disable=bare-except
                    pass

                if species_key in IMAGE_OVERRIDES:
                    data_dict[species_key]["_pictures"] = [IMAGE_OVERRIDES[species_key]]

            if "_occurrences" in data_dict[species_key]:
                data_dict[species_key]["_occurrences"].append(this_occurrence)
            else:
                data_dict[species_key]["_occurrences"] = [this_occurrence]

    with open("pickled_data.json", "w+", encoding="utf-8") as file:
        json.dump(list(data_dict.values()), file)
