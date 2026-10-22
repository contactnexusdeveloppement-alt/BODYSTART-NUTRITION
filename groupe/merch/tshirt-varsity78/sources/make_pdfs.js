// Convertit chaque SVG de ../impression en PDF vectoriel à la même taille réelle.
// Usage : node make_pdfs.js   (Chromium via playwright-core ; CHROMIUM_PATH pour un autre binaire)
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname, '..', 'impression');
const exe = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

(async () => {
  const browser = await chromium.launch({ executablePath: exe });
  const page = await browser.newPage();
  for (const f of fs.readdirSync(dir).filter((n) => n.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8').replace(/^<\?xml[^>]*>\s*/, '');
    const w = svg.match(/width="([\d.]+)mm"/)[1];
    const h = svg.match(/height="([\d.]+)mm"/)[1];
    const html = `<!doctype html><html><head><meta charset="utf-8"><style>
      @page { size: ${w}mm ${h}mm; margin: 0 }
      html, body { margin: 0; padding: 0; background: transparent }
      svg { display: block; width: ${w}mm; height: ${h}mm }
    </style></head><body>${svg}</body></html>`;
    await page.setContent(html);
    const out = path.join(dir, f.replace(/\.svg$/, '.pdf'));
    await page.pdf({ path: out, width: `${w}mm`, height: `${h}mm`, margin: { top: 0, right: 0, bottom: 0, left: 0 }, preferCSSPageSize: true, pageRanges: '1' });
    console.log(`${f} -> ${path.basename(out)} (${w} × ${h} mm)`);
  }
  await browser.close();
})();
