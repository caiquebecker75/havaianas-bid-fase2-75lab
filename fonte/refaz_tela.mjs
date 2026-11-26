// Refaz as páginas de uma tela do PDF (com um JPG por botão), sem gerar o PDF inteiro.
//   node refaz_tela.mjs <url base> <número da tela> <pasta das páginas> <primeira página>
import { chromium } from '/Volumes/hd caique becker/Mac Caique/Projetos/ariuno-videos/node_modules/playwright/index.mjs';
import { writeFileSync } from 'node:fs';

const [BASE, TELA, PASTA, PRIMEIRA] = process.argv.slice(2);
const nav = await chromium.launch({ channel: 'chrome', args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const pg = await nav.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 });
await pg.goto(BASE + '?pdf=1#' + TELA, { waitUntil: 'networkidle' });
await pg.evaluate(() => document.fonts.ready);
await pg.waitForTimeout(1500);
const estados = await pg.evaluate(() => window.__pdfEstados());
let n = +PRIMEIRA;
const salva = async () => {
  await pg.waitForTimeout(800);
  const jpg = await pg.screenshot({ type: 'jpeg', quality: 86 });
  writeFileSync(`${PASTA}/${String(n).padStart(2, '0')}.jpg`, jpg);
  console.log('página', n);
  n++;
};
if (!estados) await salva();
else {
  await pg.evaluate(() => document.documentElement.classList.add('estados'));
  for (let k = 0; k < estados; k++) { await pg.evaluate((k) => window.__pdfEstado(k), k); await salva(); }
}
await nav.close();
