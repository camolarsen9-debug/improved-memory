// Vercel serverless function: reads activities + wellness from Intervals.icu and returns a compact JSON.
// Intervals.icu already merges COROS (swim/run), Garmin/Zwift (bike) and WHOOP (HRV/sleep/resting HR),
// so one API key is all the app needs.
//
// Environment variables (set in Vercel project settings):
//   INTERVALS_API_KEY      required   Intervals.icu -> Settings -> Developer Settings -> API Key
//   INTERVALS_ATHLETE_ID   optional   defaults to "0" (the owner of the key)
//   DASHBOARD_PASSWORD     recommended  if set, requests must send header x-dashboard-password

const SPORT = (type = "") => {
  if (/swim/i.test(type)) return "swim";
  if (/ride|cycl|bike/i.test(type)) return "bike";
  if (/run/i.test(type)) return "run";
  return "other";
};

const iso = (d) => d.toISOString().slice(0, 10);

async function intervals(path, key) {
  const auth = "Basic " + Buffer.from("API_KEY:" + key).toString("base64");
  const r = await fetch("https://intervals.icu/api/v1" + path, { headers: { Authorization: auth } });
  if (!r.ok) throw new Error(`Intervals.icu ${r.status} on ${path.split("?")[0]}`);
  return r.json();
}

module.exports = async (req, res) => {
  const pw = process.env.DASHBOARD_PASSWORD;
  if (pw && req.headers["x-dashboard-password"] !== pw) {
    res.status(401).json({ error: "password required" });
    return;
  }
  const key = process.env.INTERVALS_API_KEY;
  if (!key) {
    res.status(500).json({ error: "INTERVALS_API_KEY is not set" });
    return;
  }
  const athlete = process.env.INTERVALS_ATHLETE_ID || "0";
  const days = Math.min(parseInt(req.query?.days || "400", 10) || 400, 800);
  const newest = new Date();
  const oldest = new Date(Date.now() - days * 864e5);
  const q = `?oldest=${iso(oldest)}&newest=${iso(newest)}`;

  try {
    const [acts, well] = await Promise.all([
      intervals(`/athlete/${athlete}/activities${q}`, key),
      intervals(`/athlete/${athlete}/wellness${q}`, key),
    ]);
    const activities = acts.map((a) => ({
      id: a.id,
      date: (a.start_date_local || "").slice(0, 10),
      name: a.name,
      sport: SPORT(a.type),
      type: a.type,
      minutes: Math.round((a.moving_time || 0) / 60),
      km: a.distance ? Math.round(a.distance / 100) / 10 : null,
      load: a.icu_training_load ?? null,
      avgHr: a.average_heartrate ?? null,
      watts: a.icu_average_watts ?? a.average_watts ?? null,
      np: a.icu_weighted_avg_watts ?? null,
      ftp: a.icu_ftp ?? null,
      source: a.source ?? null,
    }));
    const wellness = well.map((w) => ({
      date: w.id,
      hrv: w.hrv ?? null,
      restingHR: w.restingHR ?? null,
      sleepHours: w.sleepSecs ? Math.round(w.sleepSecs / 360) / 10 : null,
      sleepScore: w.sleepScore ?? null,
      ctl: w.ctl != null ? Math.round(w.ctl * 10) / 10 : null,
      atl: w.atl != null ? Math.round(w.atl * 10) / 10 : null,
    }));
    res.setHeader("Cache-Control", "private, max-age=300");
    res.status(200).json({ updated: new Date().toISOString(), activities, wellness });
  } catch (e) {
    res.status(502).json({ error: String(e.message || e) });
  }
};
