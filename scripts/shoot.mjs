// Echtzeit-Screenshots per Playwright (wird von screenshot.py aufgerufen).
//
// Aufruf: node scripts/shoot.mjs jobs.json
// jobs.json: { "executablePath": "...optional...", "jobs": [
//   { "url": "file:///...", "out": "/.../x.png", "width": 900, "height": 480,
//     "at": 6000, "reduced": false } ] }
//
// Jede Seite wird geladen, dann wird "at" Millisekunden echte Zeit gewartet.
// Mehrere Jobs laufen parallel in einem Browser.

import { readFileSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const config = JSON.parse(readFileSync(process.argv[2], "utf8"));
const browser = await chromium.launch(
  config.executablePath ? { executablePath: config.executablePath } : {}
);

const PARALLEL = 6;
const queue = [...config.jobs];

async function worker() {
  for (let job = queue.shift(); job; job = queue.shift()) {
    const page = await browser.newPage({
      viewport: { width: job.width, height: job.height },
      deviceScaleFactor: 1,
    });
    await page.emulateMedia({ reducedMotion: job.reduced ? "reduce" : "no-preference" });
    await page.goto(job.url, { waitUntil: "load" });
    await page.waitForTimeout(job.at);
    await page.screenshot({ path: job.out });
    await page.close();
  }
}

await Promise.all(Array.from({ length: PARALLEL }, worker));
await browser.close();
