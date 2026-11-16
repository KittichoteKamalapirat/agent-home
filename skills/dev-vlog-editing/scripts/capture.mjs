// Captures a time-driven HTML page as transparent PNG frames with the installed Chrome. No dependencies (Node 22+).
// The page must define seek(t) (draw the frame for second t, return a promise) and window.ready (a promise resolving to the length in seconds).
//
// Usage: node capture.mjs --page <dir> [--out <dir>] [--size 1920x1080] [--fps 30] [--query "?p=x"]
//                         [--mount /url-prefix=<dir>]... [--file /url=<file>]...  (all [from to] | <seconds>...)
//   all            every frame, or frames from..to, as <out>/frames/00000.png
//   <seconds>...   single stills as <out>/stills/<time>.png, for checking a design before a full capture
// --page is served at /, --mount adds asset folders (app recordings, a project's stylesheets), --file adds single files (timeline.json).
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { readFile, mkdir, writeFile, rm } from "node:fs/promises";
import { extname, join, normalize, resolve } from "node:path";

const argv = process.argv.slice(2), opt = { mount: [], file: [] }, rest = [];
for (let i = 0; i < argv.length; i++) {
  const m = /^--(page|out|size|fps|query|mount|file)$/.exec(argv[i]);
  if (!m) rest.push(argv[i]);
  else if (m[1] === "mount" || m[1] === "file") opt[m[1]].push(argv[++i].split("="));
  else opt[m[1]] = argv[++i];
}
if (!opt.page || !rest.length) { console.error("usage: node capture.mjs --page <dir> ... (all [from to] | <seconds>...)"); process.exit(2); }
const page = resolve(opt.page), out = resolve(opt.out ?? opt.page);
const [W, H] = (opt.size ?? "1920x1080").split("x").map(Number), FPS = Number(opt.fps ?? 30);
const types = { ".html": "text/html", ".css": "text/css", ".js": "text/javascript", ".mjs": "text/javascript", ".svg": "image/svg+xml",
  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".json": "application/json", ".woff2": "font/woff2" };

const inside = (root, rel) => { const f = join(root, normalize("/" + rel)); return f.startsWith(root) ? f : null; };
const server = createServer(async (req, res) => {
  const path = normalize(decodeURIComponent(new URL(req.url, "http://x").pathname));
  let file = opt.file.find(([url]) => url === path)?.[1];
  const mount = opt.mount.find(([prefix]) => path.startsWith(prefix.replace(/\/?$/, "/")));
  if (!file && mount) file = inside(resolve(mount[1]), path.slice(mount[0].replace(/\/?$/, "/").length));
  if (!file) file = inside(page, path === "/" ? "index.html" : path);
  try {
    const body = await readFile(file);
    res.writeHead(200, { "content-type": types[extname(file)] ?? "application/octet-stream" }).end(body);
  } catch {
    console.error("404", path);
    res.writeHead(404).end();
  }
});
await new Promise((ok) => server.listen(0, "127.0.0.1", ok));
const origin = `http://127.0.0.1:${server.address().port}`;

const profile = join(out, "chrome-profile-" + process.pid);
const chrome = spawn("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", [
  "--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, `--window-size=${W},${H}`,
  "--force-device-scale-factor=1", "--hide-scrollbars", "--no-first-run", "--disable-extensions", "about:blank",
]);
const port = await new Promise((ok) => {
  chrome.stderr.on("data", (d) => { const m = /DevTools listening on ws:\/\/[^:]+:(\d+)/.exec(String(d)); if (m) ok(m[1]); });
});
const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
const ws = new WebSocket(targets.find((t) => t.type === "page").webSocketDebuggerUrl);
await new Promise((ok) => ws.addEventListener("open", ok));
let id = 0;
const pending = new Map();
ws.addEventListener("message", (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { const { ok, bad } = pending.get(m.id); pending.delete(m.id); m.error ? bad(new Error(m.error.message)) : ok(m.result); }
});
const send = (method, params = {}) => new Promise((ok, bad) => { pending.set(++id, { ok, bad }); ws.send(JSON.stringify({ id, method, params })); });
const run = async (expression) => {
  const r = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.exception?.description ?? r.exceptionDetails.text);
  return r.result.value;
};
const close = async () => { ws.close(); chrome.kill(); server.close(); await new Promise((ok) => setTimeout(ok, 300)); await rm(profile, { recursive: true, force: true }); };

try {
  await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
  await send("Emulation.setDefaultBackgroundColorOverride", { color: { r: 0, g: 0, b: 0, a: 0 } });
  await send("Page.enable");
  await send("Page.navigate", { url: origin + "/" + (opt.query ?? "") });
  await new Promise((ok) => setTimeout(ok, 800));
  const total = await run("window.ready");
  const shot = async (time, file) => {
    await run(`seek(${time})`);
    const { data } = await send("Page.captureScreenshot", { format: "png" });
    await writeFile(file, Buffer.from(data, "base64"));
  };
  if (rest[0] === "all") {
    await mkdir(join(out, "frames"), { recursive: true });
    const from = Number(rest[1] ?? 0), to = Number(rest[2] ?? Math.round(total * FPS));
    for (let i = from; i < to; i++) {
      await shot(i / FPS, join(out, "frames", String(i).padStart(5, "0") + ".png"));
      if (i % 300 === 0) console.log("frame", i, "of", to);
    }
  } else {
    await mkdir(join(out, "stills"), { recursive: true });
    for (const a of rest) await shot(Number(a), join(out, "stills", Number(a).toFixed(2) + ".png"));
  }
  console.log("done");
} finally {
  await close();
}
