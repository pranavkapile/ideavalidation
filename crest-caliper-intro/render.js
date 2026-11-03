// Usage: node render.js <w> <h> <fps> <outdir> [t1,t2,...]   (times => stills only)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const [w, h, fps, out, stills] = [+process.argv[2], +process.argv[3], +process.argv[4], process.argv[5], process.argv[6]];
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(__dirname, 'intro.html') + `?capture&w=${w}&h=${h}`);
  await page.evaluate(() => window.ready);
  const dur = await page.evaluate(() => window.DURATION);
  const times = stills ? stills.split(',').map(Number) : Array.from({ length: Math.round(dur * fps) + 1 }, (_, i) => i / fps);
  for (let i = 0; i < times.length; i++) {
    await page.evaluate(t => window.renderAt(t), times[i]);
    const name = stills ? `t${times[i].toFixed(2)}.png` : `f${String(i).padStart(5, '0')}.png`;
    await page.screenshot({ path: path.join(out, name), type: 'png' });
    if (!stills && i % 60 === 0) console.log(`frame ${i}/${times.length}`);
  }
  await browser.close();
})();
