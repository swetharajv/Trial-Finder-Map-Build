import requests
import pandas as pd
import streamlit as st
 
st.set_page_config(page_title="Trial Finder Map", page_icon="MAP", layout="wide")
st.title("Clinical Trial Finder")
st.caption("Find recruiting clinical trials for a condition and see where they run.")
 
condition = st.text_input("Condition", "psoriasis")
 
if st.button("Find trials", type="primary") and condition:
    url = "https://clinicaltrials.gov/api/v2/studies"
    params = {"query.cond": condition,
              "filter.overallStatus": "RECRUITING",
              "pageSize": 100}
    r = requests.get(url, params=params).json()
 
    rows = []
    for s in r.get("studies", []):
        ps = s["protocolSection"]
        title = ps["identificationModule"].get("briefTitle", "")
        phases = ps.get("designModule", {}).get("phases", [])
        phase = ", ".join(phases) if phases else "N/A"
        sponsor = ps.get("sponsorCollaboratorsModule", {}) \
                    .get("leadSponsor", {}).get("name", "")
        for loc in ps.get("contactsLocationsModule", {}).get("locations", []):
            gp = loc.get("geoPoint")
            if gp:
                rows.append({"title": title, "phase": phase, "sponsor": sponsor,
                             "city": loc.get("city", ""),
                             "country": loc.get("country", ""),
                             "lat": gp["lat"], "lon": gp["lon"]})
 
    df = pd.DataFrame(rows)
    if df.empty:
        st.warning("No recruiting trials with mapped locations found.")
    else:
        st.subheader(f"{df['title'].nunique()} trials across {len(df)} sites")
        st.map(df[["lat", "lon"]])
        st.dataframe(df[["title", "phase", "sponsor", "city", "country"]])
 
st.caption("Data: ClinicalTrials.gov API v2. Shows recruiting studies that "
           "include map coordinates.")
