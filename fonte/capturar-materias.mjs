// Fotografa a manchete de cada matéria (evidência visual) e baixa a imagem principal (og:image).
//   node fonte/capturar-materias.mjs <pasta bruta> <pasta webp>
//   SO=cnc,viva refaz só essas; RECUO=300 deixa mais espaço acima da manchete (cabeçalho fixo)
import { chromium } from '/Volumes/hd caique becker/Mac Caique/Projetos/ariuno-videos/node_modules/playwright/index.mjs';
import { writeFileSync, mkdirSync } from 'node:fs';

const [BRUTO, SAIDA] = process.argv.slice(2);
mkdirSync(BRUTO, { recursive: true });
mkdirSync(SAIDA, { recursive: true });
const MATERIAS = [
  ['cnc', 'https://diariodocomercio.com.br/economia/dia-maes-deve-movimentar-r-144-bilhoes-2026/'],
  ['abecs', 'https://gironews.com/negocios/dia-das-maes-deve-movimentar-r-17-bilhoes-no-varejo-em-2026/'],
  ['abiacom', 'https://gironews.com/varejo-digital/e-commerce-deve-faturar-r-11-bilhoes-no-dia-das-maes-de-2026/'],
  ['viva', 'https://viva.com.br/dinheiro/roupas-calcados-e-acessorios-lideram-os-presentes-do-dia-das-maes.html'],
  ['globo', 'https://propmark.com.br/mercado/dia-das-maes-83-dos-brasileiros-vao-comemorar-a-data-mesmo-com-orcamento-apertado/'],
  ['mindminers', 'https://mercadoeconsumo.com.br/06/05/2025/noticias-varejo/o-boticario-e-natura-sao-as-marcas-mais-lembradas-pelos-consumidores-neste-dia-das-maes/'],
  ['gestaoclick', 'https://www.abcdacomunicacao.com.br/pesquisa-revela-mudanca-no-consumo-do-dia-das-maes-brasileiros-compram-mais-mas-gastam-menos/'],
  ['meio', 'https://www.meioemensagem.com.br/womentowatch/o-que-marca-as-campanhas-de-dia-das-maes-em-2026'],
  ['boticario', 'https://propmark.com.br/anunciantes/dia-das-maes-o-boticario-aposta-no-ninho-vazio-e-viraliza-nas-redes-sociais/'],
  ['renner', 'https://propmark.com.br/anunciantes/renner-une-sabrina-sato-tais-araujo-e-suas-maes-em-novo-filme/'],
  ['hering', 'https://propmark.com.br/anunciantes/grazi-massafera-e-sophie-charlotte-estrelam-campanha-de-dia-das-maes-da-hering/'],
  ['kopenhagen', 'https://propmark.com.br/anunciantes/campanha-de-dia-das-maes-da-kopenhagen-foca-na-identidade-feminina-para-presentear/'],
  ['cacau', 'https://www.dgabc.com.br/Noticia/4294824/cacau-show-lanca-produtos-para-dia-das-maes-com-itens-a-partir-de-rs-3-49'],
  ['havaianas26', 'https://forbes.com.br/forbes-life/2026/04/havaianas-no-tapete-vermelho-marca-brasileira-anuncia-parceria-com-diabo-veste-prada-2/'],
  ['havaianas26b', 'https://www.meioemensagem.com.br/marketing/o-diabo-veste-prada-e-havaianas-em-nova-colecao'],
  ['havaianas25', 'https://acontecendoaqui.com.br/propaganda/havaianas-lanca-campanha-de-dia-das-maes-com-foco-no-ato-de-presentear/'],
];

const nav = await chromium.launch({ channel: 'chrome' });
const ctx = await nav.newContext({ viewport: { width: 1280, height: 1000 }, deviceScaleFactor: 1.5, locale: 'pt-BR',
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36' });
const SO = process.env.SO ? process.env.SO.split(',') : null;
const RECUO = +(process.env.RECUO || 140);
for (const [nome, url] of MATERIAS) {
  if (SO && !SO.includes(nome)) continue;
  const pg = await ctx.newPage();
  try {
    await pg.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await pg.waitForTimeout(3500);
    // some com faixas de cookie, pop-ups e anúncios fixos (sem aceitar nada)
    await pg.evaluate((RECUO) => {
      const ruim = /cookie|consent|lgpd|gdpr|popup|modal|newsletter|onesignal|push|paywall|overlay|interstitial|banner-?fixo|adsbygoogle|taboola|outbrain/i;
      document.querySelectorAll('body *').forEach((el) => {
        const cs = getComputedStyle(el);
        const marca = (el.id + ' ' + el.className).toString();
        if ((cs.position === 'fixed' || cs.position === 'sticky') && el.tagName !== 'HEADER') el.remove();
        else if (ruim.test(marca) && el.offsetHeight < innerHeight * 0.9) el.remove();
      });
      document.documentElement.style.overflow = 'auto'; document.body.style.overflow = 'auto';
      const h1 = document.querySelector('article h1, h1.entry-title, h1');
      if (h1) window.scrollTo(0, Math.max(0, h1.getBoundingClientRect().top + window.scrollY - RECUO));
    }, RECUO);
    await pg.waitForTimeout(800);
    const tela = await pg.screenshot({ type: 'jpeg', quality: 85 });
    writeFileSync(`${BRUTO}/${nome}-tela.jpg`, tela);
    const og = await pg.evaluate(() => (document.querySelector('meta[property="og:image"]') || {}).content || '');
    const titulo = await pg.evaluate(() => ((document.querySelector('h1') || {}).textContent || document.title).trim());
    let okImg = false;
    if (og) {
      try { const r = await ctx.request.get(og, { timeout: 30000 }); if (r.ok()) { writeFileSync(`${BRUTO}/${nome}-img.bin`, await r.body()); okImg = true; } } catch (e) {}
    }
    console.log(JSON.stringify({ nome, ok: true, img: okImg, titulo: titulo.slice(0, 120) }));
  } catch (e) {
    console.log(JSON.stringify({ nome, ok: false, erro: String(e).slice(0, 120) }));
  }
  await pg.close();
}
await nav.close();
