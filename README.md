# Ironman 2027 dashboard

Training calendar and analysis for the 70.3 (27 Jun 2027) and the Ironman (22 Aug 2027).

Data path: COROS (swim/run), Garmin/Zwift (bike) and WHOOP (HRV, resting HR, sleep) all sync into **Intervals.icu**; this app reads Intervals.icu through one API key. No Strava subscription needed.

## 1. Connect your devices in Intervals.icu (free account)
Settings -> Connections: connect COROS, Garmin, Zwift and WHOOP (check that WHOOP is listed for your account; it feeds HRV/sleep/resting HR).
Then Settings -> Developer Settings -> generate an **API key**.

## 2. Deploy on Vercel (free)
1. Put this folder in a GitHub repo (or run `npx vercel` in the folder).
2. Import it in Vercel. No build settings needed: `public/` is served, `api/data.js` becomes `/api/data`.
3. Add environment variables:
   - `INTERVALS_API_KEY` (required)
   - `DASHBOARD_PASSWORD` (strongly recommended: your training and health data would otherwise be readable by anyone with the URL)
   - `INTERVALS_ATHLETE_ID` (optional, defaults to the key's owner)
4. Open the URL. Enter the password once; it is remembered in your browser.

## Preview without data
Open `/?demo=2027-03-10` to see every chart filled with synthetic data as of that date.

## Run locally
`INTERVALS_API_KEY=... node dev.js` then open http://localhost:3000

## Changing the plan
`python3 build_plan.py` regenerates `public/plan.json` (phases, weekly hours, sport split are at the top of the script). The Sunday chat adjusts weeks; send the new plan.json and redeploy.
