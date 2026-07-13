# Fuel Fraud Detection System

An n8n-based pipeline that reconciles truck GPS trip data (via Traccar) against driver fuel-claim forms, flags high-variance trips, and reports on them daily, weekly, and in real time.

## Status (as of this commit)

- **Solution design, Google Sheets schema, and all three n8n workflows' reconciliation logic: built.**
- **End-to-end verification: blocked.** The Traccar server needed to feed real GPS data into the pipeline has been throwing errors; two troubleshooting attempts have not resolved it yet. As a result, the real 20-truck dataset, a real PKR variance figure, and a demo video do not exist yet.
- The workflow JSON exports in `workflows/` reflect the built logic, not a verified live run. Treat them as ready for testing once the Traccar issue is resolved, not as confirmed-working in production.

## What this is

Trucks report GPS position (and, where a sensor is fitted, fuel level) to **Traccar**. Drivers separately log claimed distance and fuel added via a **Google Form**. Three **n8n** workflows reconcile the two sources, compute a variance in km/litres/PKR, flag risk level, and store everything in **Google Sheets**, with reports and alerts pushed to **Slack**.

Full design details, the complete Google Sheets schema, and — importantly — the known limitations of this system (see below) are documented in [`docs/Solution_Design_File.docx`](./docs/Solution_Design_File.docx). Read that before deploying this anywhere real.

## Repo structure

```
fuel-fraud-detection/
├── workflows/     n8n workflow exports (import these into n8n)
│   ├── Fuel_Fraud_Audit_Daily_Reconcile.json   -- WF1: daily GPS/claim reconciliation
│   ├── WF2_Weekly_Driver_Summary.json          -- WF2: weekly driver rollup + Slack report
│   └── WF3_RealTime_Alert.json                 -- WF3: real-time high-variance alerts
├── docs/
│   └── Solution_Design_File.docx               -- architecture, schema, limitations
├── data/          Google Sheets schema export (.xlsx) -- to be added
└── simulator/     Python GPS/trip data simulator for demos -- to be added
```

## Setup

### 1. Google Sheets
Create a Google Sheet with the following tabs (full field list in the Solution Design File, Section 2):
`Master_Trucks`, `Form_Responses`, `Driver_ID_Lookup`, `Config`, `Trip_Data`, `DLQ_Log`, `Traccar_Trips_Raw`, `Workflow_Run_Log`, `Driver_Summary`.

### 2. Traccar
You need a running Traccar instance with your trucks registered as devices, and an API bearer token.

### 3. Slack
Create a Slack app / bot token with `chat:write` permission for the channel WF2 and WF3 should post to.

### 4. Import the workflows into n8n
For each file in `workflows/`:
1. n8n → **Workflows** → **Add workflow** → **⋯** → **Import from File**
2. Select the JSON file
3. Re-point every node's credentials (they'll show a red warning icon until you do):
   - **Google Sheets** nodes → your own Google Sheets OAuth2 credential, connected to the account that owns the sheet above
   - **Traccar GET Trips** node (WF1 only) → your own HTTP Bearer Auth credential + update the base URL to your Traccar server
   - **Slack** nodes (WF2, WF3) → your own Slack credential
4. Set `Config.Reconciliation_Date_Override` for testing, leave it blank for production
5. Toggle each workflow **Active**

## Known limitations (short version)

- **Fuel data**: `Traccar_Fuel_Consumed_Litres` is only real if the truck has a wired fuel sensor. Without one, it's null — not "zero consumed."
- **Odometer fields**: `GPS_Start_Odometer_Km` / `GPS_End_Odometer_Km` are not GPS-sourced. They're only populated in `Demo_Mode`, and even then come from the driver's own form.

Full disclosure and reasoning for both are in the Solution Design File, Section 4.

## Status

Workflow exports are finalized. The `.xlsx` schema export and Python simulator are still being finalized and will be added to `data/` and `simulator/` respectively.
