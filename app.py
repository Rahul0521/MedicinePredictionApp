from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Drug Information API"}

@app.get("/search_drug/{drug_name}")
def search_drug(drug_name: str):
    try:
        response = requests.get(f"https://rxnav.nlm.nih.gov/REST/drugs.json?name={drug_name}")
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search_adverse_events/{drug_name}")
def search_adverse_events(drug_name: str):
    try:
        response = requests.get(f"https://api.fda.gov/drug/event.json?search=patient.drug.medicinalproduct:{drug_name}")
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search_dailymed/{drug_name}")
def search_dailymed(drug_name: str):
    try:
        response = requests.get(f"https://dailymed.nlm.nih.gov/dailymed/services/v2/drugname/{drug_name}.json")
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search_alternatives/{drug_name}")
def search_alternatives(drug_name: str):
    try:
        # Step 1: Get the RxCUI of the given drug
        response = requests.get(f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}")
        response.raise_for_status()
        rxcui_data = response.json()
        rxcui = rxcui_data.get("idGroup", {}).get("rxnormId", [])[0]

        # Step 2: Use the RxCUI to find similar drugs
        response = requests.get(f"https://rxnav.nlm.nih.gov/REST/related.json?rxcui={rxcui}&tty=SCD+SBD")
        response.raise_for_status()
        related_data = response.json()
        alternatives = related_data.get("relatedGroup", {}).get("conceptGroup", [])

        # Step 3: Extract relevant alternative drug names
        alternative_drugs = []
        for group in alternatives:
            for concept in group.get("conceptProperties", []):
                alternative_drugs.append({
                    "name": concept.get("name"),
                    "rxcui": concept.get("rxcui")
                })

        return {"alternatives": alternative_drugs}
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="137.0.0.1", port=8000, reload=True)
