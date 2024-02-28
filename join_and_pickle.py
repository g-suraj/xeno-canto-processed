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
import requests

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

IMAGE_OVERRIDES = {
    "2481240": "https://upload.wikimedia.org/wikipedia/commons/4/4b/Sandwich_tern_%28Thalasseus_sandvicensis%29_in_flight_with_lesser_sand_eel_%28Ammodytes_tobianus%29_Brownsea.jpg" # Sandwich Tern
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
                        item["identifier"] for item in response.json()["results"]
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
