// Tiny local dev server: serves ./public and routes /api/data to the same handler Vercel uses.
// Usage: INTERVALS_API_KEY=xxx node dev.js   (then open http://localhost:3000)
const http = require("http");
const fs = require("fs");
const path = require("path");
const handler = require("./api/data.js");

const types = { ".html": "text/html", ".json": "application/json", ".js": "text/javascript", ".css": "text/css" };
http.createServer((req, res) => {
  const url = new URL(req.url, "http://localhost");
  if (url.pathname === "/api/data") {
    req.query = Object.fromEntries(url.searchParams);
    res.status = (c) => { res.statusCode = c; return res; };
    res.json = (o) => { res.setHeader("Content-Type", "application/json"); res.end(JSON.stringify(o)); };
    return handler(req, res);
  }
  const rel = url.pathname === "/" ? "index.html" : url.pathname.slice(1);
  const file = path.join(__dirname, "public", path.normalize(rel).replace(/^(\.\.[/\\])+/, ""));
  fs.readFile(file, (err, buf) => {
    if (err) { res.statusCode = 404; return res.end("not found"); }
    res.setHeader("Content-Type", types[path.extname(file)] || "application/octet-stream");
    res.end(buf);
  });
}).listen(process.env.PORT || 3000, () => console.log("http://localhost:" + (process.env.PORT || 3000)));
