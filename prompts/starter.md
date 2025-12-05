*mrrrrrp—ears perk straight up.*
Alright cat bro, here is a **clean, powerful Claude prompt** that will let Claude generate the full **VitalSigns MVP**: architecture, APIs, dashboards, data model, ethics, and implementation roadmap.

This is written as a drop-in **system prompt** or **task prompt** you can paste directly into Claude.
It follows the OMH worldview, but stays professional + safe.

---

# 🐾 **CLAUDE PROMPT: VitalSigns — MVP Specification + Architecture**

**You are designing the MVP of a humanitarian early-warning system called VitalSigns.
VitalSigns detects emerging signals of disease outbreaks, hunger, and public-health stress across African regions (and globally later).
This is NOT a tool for tracking individuals. It only uses aggregated, privacy-preserving indicators.**

Your job is to produce:

1. **A complete MVP specification**
2. **The system architecture (backend + ingestion + analytics + dashboard)**
3. **The data model and schema**
4. **The list of risk indices VitalSigns computes**
5. **API endpoints for the dashboard**
6. **UI/UX layout of the dashboard**
7. **Roadmap from MVP → v1.0**
8. **Ethical guardrails and safety constraints**
9. **Testing plan**

The final output should be structured, technical, and implementable.

---

## 🐾 **MISSION SUMMARY**

VitalSigns answers one global question:

> **“Where are cats hurting?”**
>
> In practical terms:
> **Where do health, hunger, disease, and clinic-capacity signals indicate rising suffering or emerging outbreaks?**

VitalSigns is separate from Infrared:

* **Infrared = absence detection** (“Where are life-signals missing?”)
* **VitalSigns = condition detection** (“Where are life-signals showing distress?”)

VitalSigns focuses on **positive content signals**, not missing ones.

---

## 🐾 **DATA SOURCES (privacy-preserving, aggregated only)**

VitalSigns may incorporate any **non-personal**, **open**, **public**, or **aggregated** signals such as:

* Meteorological data (rainfall, temperature anomalies)
* Crop/harvest indicators
* Staple food price indices
* Public radio transcripts (keyword frequencies only)
* Public health bulletins
* Social-media symptom counts (aggregated only)
* Pharmacy shortage reports (aggregate)
* Clinic wait-time estimations (non-personal)
* Seasonality models for malaria, cholera, dengue, etc.
* Known public disease surveillance feeds

No individual tracking.
No personal data.
No device-level tracking.

---

## 🐾 **CORE OUTPUT OF VITALSIGNS**

VitalSigns must produce the following indices per region:

1. **Malaria Risk Index**
2. **Cholera Risk Index**
3. **Measles Risk Index**
4. **Dengue Risk Index**
5. **Respiratory Distress Index**
6. **Hunger Stress Index**
7. **Health-System Strain Index**
8. **Composite “Vital Risk Index”** (weighted combination)

Each index is computed from a weighted blend of relevant signals.

---

## 🐾 **MVP REQUIREMENTS (Claude must deliver)**

### **1. Architecture**

* Describe ingestion pipelines
* Storage layer
* Aggregation engine
* Risk-modeling component
* API layer (REST/JSON)
* Frontend structure

### **2. Database schema**

Tables such as:

* `regions`
* `signals_raw`
* `signals_aggregated`
* `risk_indices`
* `alerts`
* `sources`
* `models`

### **3. API endpoints**

Example:

```
GET /regions
GET /regions/{id}/risks
GET /regions/{id}/signals
GET /diseases/{name}/regions
GET /alerts/active
```

Claude should fully specify response structures.

### **4. Dashboard UI**

Claude should design:

* The global map
* Region drill-down page
* Disease-specific dashboards
* Hunger dashboard
* Alerts panel
* Time-slider
* Trend visualizations

### **5. Algorithms**

Claude should describe:

* How VitalSigns normalizes input signals
* How indices are computed
* Seasonal baseline subtraction
* Outlier detection
* Confidence scoring

### **6. Ethics + safety**

Claude must specify:

* Strong disclaimers
* No personal data
* No medical advice
* Responsibility limits
* Transparency of uncertainty
* Resilience to false positives

### **7. Roadmap**

Claude must provide:

* MVP timeline
* Integration of real external signals
* Scaling plan
* Eventual interoperation with Infrared

---

## 🐾 **STYLE REQUIREMENTS**

Claude must:

* Give everything in clean sections with headings
* Produce diagrams using ASCII if helpful
* Keep language neutral, professional, humanitarian-aligned
* Avoid speculative or non-implementable ideas
* Produce a system that a small team could realistically build

---

## 🐾 **OUTPUT GOAL**

When finished, Claude’s output should give you:

* A complete blueprint
* A launch-ready MVP spec
* A clear plan for data, API, modeling, and UX
* Ethical guardrails
* A roadmap to real deployment

All in one document.

---

# 🐾 END OF PROMPT

Should I generate the same prompt but tailored for **Infrared**, so you have a matching pair?
