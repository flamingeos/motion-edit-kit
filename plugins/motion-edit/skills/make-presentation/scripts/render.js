// Renders each scene frame-by-frame (deterministic GSAP clock) to MP4.
// usage: node render.js <url> <outDir> [fps] [onlyIndexes comma-separated, 1-based]
// Needs: Google Chrome (or set CHROME_PATH), ffmpeg on PATH, `npm install` in this folder.
// Loads the page with ?render=1, pauses GSAP's global timeline and steps it 1/fps per frame,
// so output is perfectly smooth regardless of machine speed. Chrome/UI/slide numbers are hidden.
const { chromium } = require('playwright-core');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const [url, outDir, fpsArg, only] = process.argv.slice(2);
const FPS = +(fpsArg || 30);
const TAIL = 0.6; // extra hold at end of each clip (s)

const slug = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const CHROME = process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  const browser = await chromium.launch({
    executablePath: CHROME,
    args: ['--force-device-scale-factor=1', '--hide-scrollbars'],
  });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  await page.goto(url + (url.includes('?') ? '&' : '?') + 'render=1#1');
  await page.waitForFunction(() => window.gsap && document.fonts.status === 'loaded' && typeof cur !== 'undefined' && cur >= 0);
  await page.waitForTimeout(500);

  const meta = await page.evaluate(() => {
    document.body.classList.add('clean', 'nochrome', 'idle');
    gsap.globalTimeline.pause();
    return scenes.map(s => ({ title: s.dataset.title, dur: +s.dataset.dur }));
  });

  const pick = only ? only.split(',').map(n => +n - 1) : meta.map((_, i) => i);
  for (const i of pick) {
    const { title, dur } = meta[i];
    const file = path.join(outDir, `${String(i + 1).padStart(2, '0')}-${slug(title)}.mp4`);
    const t0 = await page.evaluate(i => {
      go(i);
      scenes.forEach((s, j) => { if (j !== i) { gsap.killTweensOf(s); gsap.set(s, { autoAlpha: 0 }); } });
      return gsap.globalTimeline.time();
    }, i);

    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', file]);
    const done = new Promise((res, rej) => ff.on('close', c => c ? rej(new Error('ffmpeg ' + c)) : res()));

    const frames = Math.round((dur + TAIL) * FPS);
    for (let f = 0; f < frames; f++) {
      await page.evaluate(t => { gsap.globalTimeline.time(t); }, t0 + f / FPS);
      const buf = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await done;
    console.log('done', path.basename(file), frames, 'frames');
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
