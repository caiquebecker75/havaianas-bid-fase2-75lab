(function(){
  'use strict';
  const $=(s,r=document)=>r.querySelector(s), $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const stage=$('#stage'), telas=$$('.tela'), wipe=$('#wipe'), prog=$('#prog i'), cont=$('#cont'), capTxt=$('#capTxt');
  const SVGNS='http://www.w3.org/2000/svg';
  // ?pdf=1: cada tela já no estado final, sem transição nem temporizador (usado para gerar o PDF)
  const modoPdf=new URLSearchParams(location.search).has('pdf');
  if(modoPdf)document.documentElement.classList.add('pdf');
  const reduz=matchMedia('(prefers-reduced-motion: reduce)').matches||modoPdf;
  let atual=0, escalaAtual=1, emTransicao=false, pendente=null;
  const total=telas.length, dd=n=>String(n).padStart(2,'0');
  const autos={};let autoAtivos=[];
  const TEMAS={claro:'claro',claro2:'claro',escuro:'escuro',lime:'lime',foto:'foto',aura:'aura',planta:'escuro'};

  /* ---------------------------------------------------------- trilha das capas de capítulo (gerada a partir dos data-cap) */
  (function(){
    const caps=[];
    telas.forEach(t=>{const c=(t.dataset.cap||'').match(/^\((\d+)\) (.*)$/);if(c&&!caps.some(x=>x[0]===c[1]))caps.push([c[1],c[2]]);});
    $$('.trilha-cap').forEach(tr=>{tr.innerHTML='';caps.forEach(([n,nome])=>{const s=document.createElement('span');s.dataset.c=n;s.innerHTML=n+'<b></b>';s.querySelector('b').textContent=nome;tr.appendChild(s);});});
  })();

  /* ---------------------------------------------------------- miolo: o conteúdo de cada tela encolhe por igual, centralizado */
  telas.forEach(t=>{
    const m=document.createElement('div');m.className='miolo';
    [...t.childNodes].forEach(n=>{if(!(n.nodeType===1&&n.classList.contains('sangra')))m.appendChild(n);});
    t.appendChild(m);
  });

  /* ---------------------------------------------------------- palco */
  function escala(){escalaAtual=Math.min(innerWidth/1600,innerHeight/900);stage.style.transform='scale('+escalaAtual+')';}
  addEventListener('resize',escala);escala();

  /* ---------------------------------------------------------- contadores */
  function contar(el){
    const alvo=parseFloat(el.dataset.conta),casas=+el.dataset.casas||0,t0=performance.now(),dur=1300;
    const fmt=new Intl.NumberFormat('pt-BR',{minimumFractionDigits:casas,maximumFractionDigits:casas});
    if(reduz){el.textContent=fmt.format(alvo);return;}
    (function passo(t){const p=Math.min(1,(t-t0)/dur),v=alvo*(1-Math.pow(1-p,3));el.textContent=fmt.format(v);if(p<1)requestAnimationFrame(passo);})(t0);
  }

  /* ---------------------------------------------------------- navegação */
  const aoEntrar={};
  function aplicar(n){
    telas[atual].querySelectorAll('video').forEach(v=>v.pause());
    pararAutos();
    telas[atual].classList.remove('ativa');
    atual=n;const t=telas[n];
    t.classList.add('ativa');
    stage.className='t-'+(TEMAS[t.dataset.tema]||'escuro')+(n===0?' capa':'');
    capTxt.textContent=t.dataset.cap||'';
    prog.style.width=((n+1)/total*100)+'%';
    cont.textContent=dd(n+1)+' / '+dd(total);
    $('#ant').disabled=n===0;$('#prox').disabled=n===total-1;
    t.querySelectorAll('[data-conta]').forEach(contar);
    $$('#sumLista button').forEach(b=>b.classList.toggle('atual',+b.dataset.i===n));
    history.replaceState(null,'','#'+(n+1));
    const fn=aoEntrar[t.classList[1]];if(fn)fn(t);
    ligas(t);
    iniciarAutos(t);
  }
  function ir(n){
    n=Math.max(0,Math.min(total-1,n));
    if(emTransicao){pendente=n;return;}
    if(n===atual)return;
    if(reduz||!wipe.animate){aplicar(n);return;}
    const dir=n>atual?1:-1, tema=telas[n].dataset.tema;
    wipe.classList.toggle('ink',tema==='lime');wipe.classList.toggle('aura',tema==='aura');
    wipe.querySelector('img').src=tema==='lime'?'assets/75lab-lime.png':'assets/75lab-black.png';
    const de=dir>0?'inset(0 0 0 100%)':'inset(0 100% 0 0)', meio='inset(0 0 0 0)', para=dir>0?'inset(0 100% 0 0)':'inset(0 0 0 100%)';
    emTransicao=true;
    const ease='cubic-bezier(.7,0,.3,1)';
    wipe.animate([{clipPath:de},{clipPath:meio}],{duration:360,easing:ease,fill:'forwards'}).onfinish=()=>{
      aplicar(n);
      wipe.animate([{clipPath:meio},{clipPath:para}],{duration:420,easing:ease,fill:'forwards'}).onfinish=()=>{emTransicao=false;if(pendente!==null){const p=pendente;pendente=null;ir(p);}};
    };
  }
  addEventListener('hashchange',()=>{const n=parseInt(location.hash.slice(1),10);if(!isNaN(n))ir(n-1);});
  $('#ant').addEventListener('click',e=>{e.stopPropagation();ir(atual-1);});
  $('#prox').addEventListener('click',e=>{e.stopPropagation();ir(atual+1);});
  const indice=v=>/^\d+$/.test(v)?+v-1:telas.findIndex(t=>t.id===v);
  $$('[data-ir]').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();ir(indice(b.dataset.ir));}));

  /* sumário */
  const sum=$('#sumario'), lista=$('#sumLista');
  let capAnt='';
  telas.forEach((t,i)=>{
    const c=(t.dataset.cap||'').match(/^\((\d+)\) (.*)$/);
    if(c&&c[1]!==capAnt){capAnt=c[1];const h=document.createElement('li');h.className='cap-s';h.textContent=c[1]+' · '+c[2];lista.appendChild(h);}
    if(t.classList.contains('s-cap'))return;
    const li=document.createElement('li'), b=document.createElement('button');
    b.innerHTML='<b>'+dd(i+1)+'</b>';b.appendChild(document.createTextNode(t.dataset.titulo));b.dataset.cursor='Ir';b.dataset.i=i;
    b.addEventListener('click',e=>{e.stopPropagation();fecharSum();setTimeout(()=>ir(i),60);});
    li.appendChild(b);lista.appendChild(li);
  });
  function abrirSum(){sum.classList.add('aberto');}
  function fecharSum(){sum.classList.remove('aberto');}
  $$('[data-sumario]').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation();abrirSum();}));
  $('.fechar',sum).addEventListener('click',e=>{e.stopPropagation();fecharSum();});

  /* teclado, clique e toque */
  addEventListener('keydown',e=>{
    if(caixa.classList.contains('aberta')){if(e.key==='Escape')fecharCaixa();return;}
    if(sum.classList.contains('aberto')){if(e.key==='Escape')fecharSum();return;}
    if(['ArrowRight','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();ir(atual+1);}
    else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();ir(atual-1);}
    else if(e.key==='Home')ir(0);else if(e.key==='End')ir(total-1);
    else if(e.key==='m'||e.key==='M')sum.classList.contains('aberto')?fecharSum():abrirSum();
  });
  const INTERATIVO='a,button,input,.amplia,[data-cursor],#sumario,.janela,.tela-s,.janela-c,.dentro li,.trilha-cap span,.mk,.hs,.gantt-c,.vista-pl img,.comp';
  $('#wrap').addEventListener('click',e=>{
    if(e.target.closest(INTERATIVO))return;
    if(sum.classList.contains('aberto'))return;
    ir(e.clientX>innerWidth/2?atual+1:atual-1);
  });
  let x0=null,y0=null;
  addEventListener('touchstart',e=>{x0=e.touches[0].clientX;y0=e.touches[0].clientY;},{passive:true});
  addEventListener('touchend',e=>{
    if(x0===null)return;const dx=e.changedTouches[0].clientX-x0,dy=e.changedTouches[0].clientY-y0;
    if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy))ir(dx<0?atual+1:atual-1);x0=null;
  });

  /* lightbox (delegado: vale também para o que é criado depois) */
  const caixa=$('#caixa');
  function abrirCaixa(src,leg){$('#cxImg').src=src;$('#cxTxt').textContent=leg||'';caixa.classList.add('aberta');}
  function fecharCaixa(){caixa.classList.remove('aberta');}
  stage.addEventListener('click',e=>{const el=e.target.closest('[data-amplia]');if(!el)return;e.stopPropagation();abrirCaixa(el.dataset.amplia,el.dataset.legenda);});
  caixa.addEventListener('click',e=>{if(e.target===caixa||e.target.closest('.fechar'))fecharCaixa();});

  /* ---------------------------------------------------------- cursor e luz */
  const cur=$('#cursor'),anel=$('#anel'),anelTxt=$('#anelTxt');
  let mx=innerWidth/2,my=innerHeight/2,ax=mx,ay=my;
  addEventListener('mousemove',e=>{
    document.body.classList.add('tem-mouse');mx=e.clientX;my=e.clientY;
    cur.style.transform='translate('+mx+'px,'+my+'px)';
    const alvo=e.target.closest('[data-cursor],a,button,.amplia,.mk,.hs');
    anel.classList.toggle('sobre',!!alvo);
    anelTxt.textContent=alvo?(alvo.dataset.cursor||'Ver'):'';
    const r=stage.getBoundingClientRect();
    stage.style.setProperty('--mx',((mx-r.left)/escalaAtual)+'px');stage.style.setProperty('--my',((my-r.top)/escalaAtual)+'px');
  },{passive:true});
  (function segue(){ax+=(mx-ax)*.2;ay+=(my-ay)*.2;anel.style.transform='translate('+ax+'px,'+ay+'px)';requestAnimationFrame(segue);})();
  addEventListener('mousedown',()=>document.body.classList.add('clicou'));
  addEventListener('mouseup',()=>document.body.classList.remove('clicou'));
  addEventListener('touchstart',()=>document.body.classList.remove('tem-mouse'),{passive:true});
  $('#verAssim').addEventListener('click',()=>document.body.classList.add('forcar'));

  /* ---------------------------------------------------------- capas de capítulo: trilha e itens levam à tela */
  telas.filter(t=>t.classList.contains('s-cap')).forEach(c=>{
    const n=c.dataset.capitulo,i0=telas.indexOf(c);
    c.querySelectorAll('.trilha-cap span').forEach(s=>{
      s.classList.toggle('on',s.dataset.c===n);s.classList.toggle('feito',s.dataset.c<n);s.dataset.cursor='Ir';
      s.addEventListener('click',e=>{e.stopPropagation();const alvo=telas.findIndex(t=>(t.dataset.cap||'').startsWith('('+s.dataset.c+')'));if(alvo>=0)ir(alvo);});
    });
    c.querySelectorAll('.dentro li').forEach((li,k)=>{li.dataset.cursor='Ir';li.addEventListener('click',e=>{e.stopPropagation();ir(i0+1+k);});});
  });

  /* ---------------------------------------------------------- KV: os quatro ajustes */
  (function(){
    const t=$('.s-kv2');if(!t)return;
    const lis=$$('#ajustes li',t),hs=$$('.hs',t);
    function mostra(k){lis.forEach((l,j)=>l.classList.toggle('on',j===k));hs.forEach(h=>h.classList.toggle('on',+h.dataset.k===k));}
    lis.forEach((l,k)=>l.querySelector('button').addEventListener('click',e=>{e.stopPropagation();mostra(k);}));
    hs.forEach(h=>{h.dataset.cursor='Ver';h.addEventListener('click',e=>{e.stopPropagation();mostra(+h.dataset.k);});});
    aoEntrar['s-kv2']=()=>mostra(0);
    roteiro('s-kv2',{itens:()=>lis.map(l=>l.querySelector('button')),texto:k=>lis[k].textContent});
  })();

  /* ---------------------------------------------------------- conceitos acadêmicos */
  (function(){
    const t=$('.s-teo');if(!t)return;
    const dados=[...$('#conceitosDados').content.querySelectorAll('i')],lis=$$('#conceitos li',t),box=$('#conceitoBox');
    box.innerHTML='<div class="im"></div><div class="tx"><h3></h3><span class="au"></span><p></p><span class="na"></span></div>';
    function mostra(k){
      const d=dados[k];lis.forEach((l,j)=>l.classList.toggle('on',j===k));
      $('.im',box).style.backgroundImage='url('+d.dataset.img+')';
      $('h3',box).innerHTML=d.dataset.ic?'<svg class="ic"><use href="#i-'+d.dataset.ic+'"/></svg>':'';$('h3',box).appendChild(document.createTextNode(d.dataset.t));$('.au',box).textContent=d.dataset.a;$('p',box).textContent=d.textContent;$('.na',box).textContent='Na loja: '+d.dataset.p;
      box.classList.remove('troca');void box.offsetWidth;box.classList.add('troca');
    }
    lis.forEach((l,k)=>l.querySelector('button').addEventListener('click',e=>{e.stopPropagation();mostra(k);}));
    aoEntrar['s-teo']=()=>mostra(0);mostra(0);
    roteiro('s-teo',{itens:()=>lis.map(l=>l.querySelector('button')),texto:k=>dados[k].textContent});
  })();

  /* ---------------------------------------------------------- plantas: peças marcadas na vista de cima */
  (function(){
    const P=window.PLANTAS||{};
    $$('.s-planta').forEach(t=>{
      const itens=P[t.dataset.planta]||[],planta=$('.planta',t),ol=$('.lista-pl',t),fig=$('.vista-pl',t),img=$('img',planta);
      const deita=()=>{if(img.naturalWidth)t.classList.toggle('deitada',img.naturalWidth>img.naturalHeight*1.05);};
      img.complete?deita():img.addEventListener('load',deita);
      // o mesmo nome vira um item só na lista (dois carrinhos, por exemplo), com o mesmo número nos dois marcadores
      const uni=[];itens.forEach(it=>{if(!uni.some(u=>u.nome===it.nome))uni.push(it);});
      uni.forEach((it,k)=>{
        const li=document.createElement('li');li.innerHTML='<button data-cursor="Ver"><i>'+(k+1)+'</i><span></span></button><p></p>';
        $('span',li).textContent=it.nome;$('p',li).textContent=it.txt;ol.appendChild(li);
        li.querySelector('button').addEventListener('click',e=>{e.stopPropagation();mostra(k);});
      });
      const mks=itens.map((it,j)=>{
        const k=uni.findIndex(u=>u.nome===it.nome),m=document.createElement('button');
        m.className='mk';m.dataset.k=k;m.dataset.cursor='Ver';m.textContent=k+1;m.style.left=it.pos[0]+'%';m.style.top=it.pos[1]+'%';
        m.style.transitionDelay=(.5+j*.12)+'s';m.setAttribute('aria-label',it.nome);
        m.addEventListener('click',e=>{e.stopPropagation();mostra(k);});planta.appendChild(m);return m;
      });
      fig.innerHTML='<img alt=""><figcaption><b></b><p></p></figcaption>';
      function mostra(k){
        const it=uni[k];if(!it)return;
        $$('li',ol).forEach((l,j)=>l.classList.toggle('on',j===k));mks.forEach(m=>m.classList.toggle('on',+m.dataset.k===k));
        const im=$('img',fig);im.src=it.img;im.alt=it.nome;im.dataset.amplia=it.img;im.dataset.legenda=it.nome;im.dataset.cursor='Ampliar';
        $('b',fig).textContent=it.nome;$('p',fig).textContent=it.txt;
        fig.classList.remove('troca');void fig.offsetWidth;fig.classList.add('troca');
      }
      t._mostra=mostra;mostra(0);
    });
    aoEntrar['s-planta']=t=>t._mostra&&t._mostra(0);
    roteiro('s-planta',{itens:t=>$$('.lista-pl button',t),texto:(k,t)=>$$('.lista-pl li',t)[k].textContent,extra:800});
  })();


  /* ---------------------------------------------------------- o time: fichas, papéis e frentes */
  (function(){
    const P=window.PAPEIS||[],F=window.FRENTES||[];
    const NOMEF=['Lojas Próprias','Franquias','Varejo'];
    const ICP=['loja','pessoas','cubo','pincel','moeda','camera','caminhao','carrinho','pincel','raio','moeda','caminhao','olho','regua','arquivo'];
    const icone=n=>'<svg class="ic"><use href="#i-'+n+'"/></svg>';
    const pizza=d=>{const a=d[0]*3.6,b=(d[0]+d[1])*3.6;return 'conic-gradient(var(--vinho) 0deg '+a+'deg,var(--cobre) '+a+'deg '+b+'deg,var(--azul) '+b+'deg 360deg)';};
    const fichas=$('#fichas');
    if(fichas)P.forEach((p,k)=>{
      const f=document.createElement('div');f.className='fi';f.style.transitionDelay=(.3+k*.05)+'s';
      f.innerHTML='<i></i><span></span>';$('i',f).style.background=pizza(p[2]);$('span',f).textContent=p[0];fichas.appendChild(f);
    });
    const lista=$('#listaPapeis'),box=$('#papelBox'),todos=$('#todosPapeis');
    if(lista&&P.length){
      const divisao=d=>d.map((v,j)=>v?'<span class="f'+j+'" style="flex:'+v+'"><b>'+v+'%</b> '+NOMEF[j]+'</span>':'').join('');
      const maiuscula=t=>t.charAt(0).toUpperCase()+t.slice(1)+'.';
      P.forEach((p,k)=>{
        const li=document.createElement('li');li.innerHTML='<button data-cursor="Ver">'+icone(ICP[k])+'<span></span></button>';$('span',li).textContent=p[0];lista.appendChild(li);
        li.querySelector('button').addEventListener('click',e=>{e.stopPropagation();mostra(k);});
      });
      box.innerHTML='<span class="sen"></span><h3></h3><div class="div-p"></div><p class="mi"></p><div class="col-p"><div><span class="eyebrow">O que entrega</span><ul></ul></div><div><span class="eyebrow">Decide</span><p class="dec"></p><span class="eyebrow">Depende</span><p class="dep"></p><span class="eyebrow">Como a gente mede</span><p class="med"></p></div></div>';
      function mostra(k){
        const p=P[k];$$('li',lista).forEach((l,j)=>l.classList.toggle('on',j===k));
        $('.sen',box).textContent=p[1]+' · 176 horas por mês, só nesta conta';$('h3',box).innerHTML=icone(ICP[k]);$('h3',box).appendChild(document.createTextNode(p[0]));$('.div-p',box).innerHTML=divisao(p[2]);
        $('.mi',box).textContent=p[3];
        const ul=$('ul',box);ul.innerHTML='';p[4].forEach(t=>{const li=document.createElement('li');li.textContent=t;ul.appendChild(li);});
        $('.dec',box).textContent=maiuscula(p[5]);$('.dep',box).textContent=maiuscula(p[6]);$('.med',box).textContent=maiuscula(p[7]);
        box.classList.remove('troca');void box.offsetWidth;box.classList.add('troca');
      }
      P.forEach(p=>{
        const d=document.createElement('div');d.innerHTML='<b></b><span></span><p></p>';
        $('b',d).textContent=p[0];$('span',d).textContent=p[2].map((v,j)=>v?NOMEF[j]+' '+v+'%':'').filter(Boolean).join(' · ');$('p',d).textContent=p[3];todos.appendChild(d);
      });
      mostra(0);aoEntrar['s-papeis']=()=>mostra(0);
      roteiro('s-papeis',{itens:()=>$$('button',lista),texto:k=>P[k][3]+' '+P[k][4].join(' '),extra:-1500});
    }
    const tres=$('#tresFrentes');
    if(tres)F.forEach((f,k)=>{
      const c=document.createElement('div');c.className='fr f'+k+' anima d'+(k+1);
      c.innerHTML='<div class="cab-f"><span class="eyebrow"></span><b></b><div class="nf"><span><em></em>posições</span><span><em></em>pessoas em tempo integral</span><span><em></em>horas por mês</span></div></div><p class="por"></p><ul></ul>';
      $('.eyebrow',c).textContent=f.canal;$('b',c).textContent=f.nome;$('.cab-f',c).insertAdjacentHTML('afterbegin',icone(['loja','pessoas','carrinho'][k]));
      const em=$$('em',c);em[0].textContent=f.pos;em[1].textContent=f.fte;em[2].textContent=f.h.toLocaleString('pt-BR');
      $('.por',c).textContent=f.por;
      f.l.forEach(([n,pc,h])=>{
        const li=document.createElement('li');li.innerHTML='<span class="n"></span><span class="b"><i></i></span><span class="v"></span>';
        $('.n',li).textContent=n;$('.b i',li).style.width=pc+'%';$('.v',li).textContent=pc+'% · '+h+' h';$('ul',c).appendChild(li);
      });
      tres.appendChild(c);
    });
  })();



  /* ---------------------------------------------------------- KV: antes e depois */
  (function(){
    const c=$('#compKV');if(!c)return;
    const poe=v=>c.style.setProperty('--x',Math.max(0,Math.min(100,v))+'%');
    const deX=e=>{const r=c.getBoundingClientRect();return (e.clientX-r.left)/r.width*100;};
    let arr=false,anim=null;
    c.addEventListener('pointerdown',e=>{arr=true;cancelAnimationFrame(anim);c.setPointerCapture(e.pointerId);poe(deX(e));e.stopPropagation();});
    c.addEventListener('pointermove',e=>{if(arr)poe(deX(e));});
    c.addEventListener('pointerup',()=>{arr=false;});
    c.addEventListener('click',e=>e.stopPropagation());
    aoEntrar['s-kv5']=()=>{
      if(reduz){poe(50);return;}
      const t0=performance.now();
      (function passo(t){const k=Math.min(1,(t-t0-600)/2600);if(k<0){poe(96);anim=requestAnimationFrame(passo);return;}
        const v=k<.6?96-(96-8)*(k/.6):8+(50-8)*((k-.6)/.4);poe(v);if(k<1)anim=requestAnimationFrame(passo);})(t0);
    };
  })();

  /* ---------------------------------------------------------- galeria em cinema */
  (function(){
    const t=$('.s-cine');if(!t)return;
    const bs=$$('#cineTira button'),hs=$$('.cine .h',t),leg=$('#cineLeg');
    function mostra(k){
      bs.forEach((b,j)=>b.classList.toggle('on',j===k));
      hs.forEach((h,j)=>{h.classList.toggle('on',j===k);if(j===k)h.loading='eager';});
      leg.textContent=bs[k].dataset.leg;
    }
    bs.forEach((b,k)=>b.addEventListener('click',e=>{e.stopPropagation();mostra(k);}));
    aoEntrar['s-cine']=()=>mostra(0);
    roteiro('s-cine',{itens:()=>bs,ms:()=>5200});
  })();

  /* ---------------------------------------------------------- cronograma por canal (Gantt) */
  (function(){
    const box=$('#cronoGantt');if(!box||!window.CRONO)return;
    const C=window.CRONO,abas=$$('#cronoAbas button'),res=$('#cronoRes');
    const D=s=>new Date(s+'T12:00:00'),br=d=>dd(d.getDate())+'/'+dd(d.getMonth()+1);
    const T0=D('2026-11-23'),T1=D('2027-04-26');
    const MES=['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'];
    const COR={med:'#C0EE4E',aprov:'#E8412C',est:'#06C6AE'};
    const NOMES={'DTC Lojas Próprias':'Lojas Próprias','DTC Franquias':'Franquias','B2B (Alimentar e Especializado)':'Varejo'};
    function desenha(c){
      const cr=C[c],W=1456,H=542,LX=440,TOP=34;
      const prin=cr.et.filter(e=>e.tipo!=='par'),par=cr.et.filter(e=>e.tipo==='par');
      const linhas=prin.length+par.length+1,RH=Math.min(26,(H-TOP-6)/linhas);
      const x=d=>LX+(d-T0)/(T1-T0)*(W-LX-20);
      const svg=document.createElementNS(SVGNS,'svg');svg.setAttribute('viewBox','0 0 '+W+' '+H);svg.setAttribute('role','img');
      svg.setAttribute('aria-label','Cronograma '+cr.canal);
      const el=(tag,at,pai=svg)=>{const e=document.createElementNS(SVGNS,tag);for(const k in at)e.setAttribute(k,at[k]);pai.appendChild(e);return e;};
      const txt=(s,at,pai)=>{const e=el('text',at,pai);e.textContent=s;return e;};
      const defs=el('defs',{}),pat=el('pattern',{id:'hach'+c,width:6,height:6,patternUnits:'userSpaceOnUse',patternTransform:'rotate(45)'},defs);
      el('rect',{width:3,height:6,fill:'#F2F1E9','fill-opacity':.5},pat);
      // recesso e carnaval
      [['2026-12-24','2027-01-02','recesso'],['2027-02-08','2027-02-10','carnaval']].forEach(([a,b,n])=>{
        el('rect',{x:x(D(a)),y:TOP-6,width:x(D(b))-x(D(a)),height:H-TOP+6,fill:'#F2F1E9','fill-opacity':.06});
        txt(n,{x:(x(D(a))+x(D(b)))/2,y:H-4,'text-anchor':'middle','font-family':'Schibsted Grotesk','font-size':9,fill:'#F2F1E9','fill-opacity':.45});
      });
      for(let m=new Date(2026,11,1,12);m<=T1;m.setMonth(m.getMonth()+1)){
        const xm=x(m);el('line',{x1:xm,y1:TOP-14,x2:xm,y2:H-14,stroke:'#F2F1E9','stroke-opacity':.14});
        txt(MES[m.getMonth()]+(m.getMonth()===0||m.getMonth()===11?' '+String(m.getFullYear()).slice(2):''),{x:xm+5,y:TOP-18,'font-family':'Schibsted Grotesk','font-size':10.5,fill:'#F2F1E9','fill-opacity':.65,'letter-spacing':1});
      }
      const hoje=new Date();hoje.setHours(12,0,0,0);
      if(hoje>=T0&&hoje<=T1){const xh=x(hoje);
        el('line',{x1:xh,y1:TOP-14,x2:xh,y2:H-30,stroke:'#F2F1E9','stroke-width':2.5});
        el('rect',{x:xh-2,y:H-30,width:112,height:20,fill:'#F2F1E9'});
        txt('HOJE · '+br(hoje),{x:xh+6,y:H-16,'font-family':'Schibsted Grotesk','font-size':11,'font-weight':800,fill:'#050505','letter-spacing':1});}
      const marco=cr.et.find(e=>e.tipo==='marco'),xm=x(D(marco.i));
      el('line',{x1:xm,y1:TOP-14,x2:xm,y2:H-14,stroke:'#C0EE4E','stroke-dasharray':'4 4','stroke-width':1.5});
      const linha=(e,k,paralela)=>{
        const y=TOP+k*RH,a=D(e.i),b=D(e.f);b.setDate(b.getDate()+1);
        const lab=e.n.length>62?e.n.slice(0,60)+'…':e.n;
        txt(lab,{x:LX-14,y:y+RH*.62,'text-anchor':'end','font-family':'Schibsted Grotesk','font-size':12,fill:'#F2F1E9','fill-opacity':paralela?.6:.88});
        if(e.tipo==='marco'){
          el('path',{d:'M'+xm+' '+(y+2)+'l'+(RH/2-2)+' '+(RH/2-2)+'-'+(RH/2-2)+' '+(RH/2-2)+'-'+(RH/2-2)+'-'+(RH/2-2)+'z',fill:'#C0EE4E'});
          txt(br(a)+' · '+e.n.toLowerCase(),{x:xm-14,y:y+RH*.62,'text-anchor':'end','font-family':'Schibsted Grotesk','font-size':10.5,'font-weight':700,fill:'#C0EE4E'});
          return;
        }
        const w=Math.max(4,x(b)-x(a)),at={x:x(a),y:y+3,width:w,height:RH-7,class:'bar'};
        if(e.tipo==='folga')Object.assign(at,{fill:'url(#hach'+c+')'});
        else if(e.tipo==='par')Object.assign(at,{fill:'none',stroke:'#F2F1E9','stroke-width':1.6,'stroke-opacity':.8});
        else at.fill=COR[e.tipo];
        const r=el('rect',at);r.style.animationDelay=(.15+k*.05)+'s';
        el('title',{},r).textContent=e.n+' · '+br(a)+' a '+br(D(e.f))+' · '+e.du+' dias úteis';
        const fim=x(b)>W-190;
        txt(br(a)+(e.du>1?' a '+br(D(e.f)):'')+' · '+e.du+(e.du>1?' dias':' dia'),{x:fim?x(a)-6:x(b)+6,y:y+RH*.62,'text-anchor':fim?'end':'start','font-family':'Schibsted Grotesk','font-size':9.5,fill:'#F2F1E9','fill-opacity':.6});
      };
      prin.forEach((e,k)=>linha(e,k,false));
      const yp=TOP+prin.length*RH;
      txt('AO MESMO TEMPO',{x:LX-14,y:yp+RH*.62,'text-anchor':'end','font-family':'Schibsted Grotesk','font-size':10,fill:'#C0EE4E','letter-spacing':2});
      el('line',{x1:20,y1:yp+RH/2,x2:W-20,y2:yp+RH/2,stroke:'#F2F1E9','stroke-opacity':.12});
      par.forEach((e,k)=>linha(e,prin.length+1+k,true));
      box.innerHTML='';box.appendChild(svg);
      const md=cr.mediano||{};
      res.innerHTML='<div><b>'+br(D(marco.i))+'/27</b>'+(c===2?'peças no ponto de venda':'campanha na loja')+'</div><div><b>'+(md.pronto_para_o_marco_em||'').slice(0,5)+'</b>tudo pronto, no ritmo normal</div><div><b>'+cr.folga+' dias</b>de folga, mesmo num ritmo lento</div>';
      abas.forEach((x,j)=>x.classList.toggle('on',j===c));
    }
    abas.forEach((b,k)=>{b.textContent=NOMES[C[k].canal]||C[k].canal;b.addEventListener('click',e=>{e.stopPropagation();desenha(k);});});
    aoEntrar['s-crono']=()=>desenha(0);desenha(0);
    roteiro('s-crono',{itens:()=>abas,ms:()=>11000});
  })();

  /* ---------------------------------------------------------- simulador do Ariuno */
  (function(){
    const lis=$$('#simPassos li'),imgs=$$('#simVista img'),url=$('#simUrl'),n=$('#simuN');
    if(!lis.length)return;
    let k=0;
    function mostra(i){
      k=(i+lis.length)%lis.length;
      lis.forEach((l,j)=>{l.classList.toggle('on',j===k);l.classList.toggle('feito',j<k);});
      const im=+lis[k].dataset.img;imgs.forEach((m,j)=>m.classList.toggle('on',j===im));
      url.textContent=imgs[im].dataset.url;n.textContent='Passo '+(k+1)+' de '+lis.length;
      $$('.s-simu .fases span').forEach(f=>f.classList.toggle('on',f.className.indexOf('f-'+lis[k].dataset.fase)>=0));
    }
    lis.forEach((l,i)=>l.querySelector('button').addEventListener('click',e=>{e.stopPropagation();mostra(i);}));
    $('#simAnt').addEventListener('click',e=>{e.stopPropagation();mostra(k-1);});
    $('#simProx').addEventListener('click',e=>{e.stopPropagation();mostra(k+1);});
    aoEntrar['s-simu']=()=>mostra(0);
    roteiro('s-simu',{itens:()=>lis.map(l=>l.querySelector('button')),texto:i=>lis[i].textContent,extra:1500});
  })();

  /* ---------------------------------------------------------- central da rede: módulos */
  (function(){
    const lis=$$('#modsCentral li'),imgs=$$('#vistaCentral img'),abrir=$('#abrirCentral');
    if(!lis.length)return;
    function mostra(i){lis.forEach((l,j)=>l.classList.toggle('on',j===i));imgs.forEach((m,j)=>m.classList.toggle('on',j===i));abrir.href='assets/rede/central.html?v='+lis[i].querySelector('button').dataset.v;}
    lis.forEach((l,i)=>l.querySelector('button').addEventListener('click',e=>{e.stopPropagation();mostra(i);}));
    aoEntrar['s-central']=()=>mostra(0);
    roteiro('s-central',{itens:()=>lis.map(l=>l.querySelector('button')),texto:i=>lis[i].textContent,extra:2500});
  })();

  /* ---------------------------------------------------------- painel do QR */
  (function(){
    const abas=$$('#qrAbas button'),vistas=$$('#qrVista>div');
    abas.forEach((b,k)=>b.addEventListener('click',e=>{e.stopPropagation();abas.forEach(x=>x.classList.toggle('on',x===b));vistas.forEach((v,j)=>v.classList.toggle('on',j===k));}));
    vistas.forEach(v=>v.classList.add('pan'));
    roteiro('s-qr',{itens:()=>abas,ms:()=>8000});
  })();


  /* ---------------------------------------------------------- ligações: linhas que se desenham entre elementos
     <section data-ligas="a>b b~c a-b"> liga os elementos marcados com data-no="a" (só letras e números).
     >  curva com um ponto correndo    ~  curva tracejada    -  reta com um ponto correndo
     a:r>b:l escolhe o lado (t, r, b, l, c). data-circ no elemento: a linha sai da borda do círculo. */
  function caixaNo(el,m){let x=0,y=0,e=el;while(e&&e!==m){x+=e.offsetLeft;y+=e.offsetTop;e=e.offsetParent;}return{x,y,w:el.offsetWidth,h:el.offsetHeight};}
  function pontoNo(b,lado,alvo,circ){
    const cx=b.x+b.w/2,cy=b.y+b.h/2;
    if(lado==='c')return[cx,cy];if(lado==='t')return[cx,b.y];if(lado==='b')return[cx,b.y+b.h];if(lado==='l')return[b.x,cy];if(lado==='r')return[b.x+b.w,cy];
    const dx=alvo[0]-cx,dy=alvo[1]-cy,d=Math.hypot(dx,dy)||1;
    if(circ){const r=Math.min(b.w,b.h)/2;return[cx+dx/d*r,cy+dy/d*r];}
    const sx=dx?(b.w/2)/Math.abs(dx):Infinity,sy=dy?(b.h/2)/Math.abs(dy):Infinity,s=Math.min(sx,sy);
    return[cx+dx*s,cy+dy*s];
  }
  function ligas(t){
    const def=t.dataset.ligas;if(!def)return;
    const m=t.querySelector('.miolo');m.querySelectorAll(':scope>.ligas,:scope>.fluxo').forEach(e=>e.remove());
    const svg=document.createElementNS(SVGNS,'svg');svg.setAttribute('class','ligas');svg.setAttribute('viewBox','0 0 1600 900');m.prepend(svg);
    def.trim().split(/\s+/).forEach((par,k)=>{
      const mm=par.match(/^(\w+)(?::([trblc]))?([>~-])(\w+)(?::([trblc]))?$/);if(!mm)return;
      const A=m.querySelector('[data-no="'+mm[1]+'"]'),B=m.querySelector('[data-no="'+mm[4]+'"]');if(!A||!B)return;
      const ba=caixaNo(A,m),bb=caixaNo(B,m),ca=[ba.x+ba.w/2,ba.y+ba.h/2],cb=[bb.x+bb.w/2,bb.y+bb.h/2];
      const p1=pontoNo(ba,mm[2],cb,A.hasAttribute('data-circ')),p2=pontoNo(bb,mm[5],ca,B.hasAttribute('data-circ'));
      const tipo=mm[3],dx=p2[0]-p1[0],dy=p2[1]-p1[1],f=v=>Math.round(v*10)/10;
      let d;
      if(tipo==='-')d=`M${f(p1[0])} ${f(p1[1])}L${f(p2[0])} ${f(p2[1])}`;
      else if(Math.abs(dx)>=Math.abs(dy))d=`M${f(p1[0])} ${f(p1[1])}C${f(p1[0]+dx*.5)} ${f(p1[1])} ${f(p2[0]-dx*.5)} ${f(p2[1])} ${f(p2[0])} ${f(p2[1])}`;
      else d=`M${f(p1[0])} ${f(p1[1])}C${f(p1[0])} ${f(p1[1]+dy*.5)} ${f(p2[0])} ${f(p2[1]-dy*.5)} ${f(p2[0])} ${f(p2[1])}`;
      const p=document.createElementNS(SVGNS,'path');p.setAttribute('d',d);p.setAttribute('class','liga'+(tipo==='~'?' tr':''));
      p.dataset.a=mm[1];p.dataset.b=mm[4];svg.appendChild(p);
      const atraso=350+k*110,L=p.getTotalLength();
      if(!reduz){
        if(tipo==='~')p.animate([{opacity:0},{opacity:.5}],{duration:700,delay:atraso,fill:'backwards'});
        else p.animate([{strokeDasharray:L+' '+L,strokeDashoffset:L},{strokeDasharray:L+' '+L,strokeDashoffset:0}],{duration:900,delay:atraso,easing:'cubic-bezier(.5,0,.2,1)',fill:'backwards'});
      }
      if(tipo!=='~'){
        const ponto=document.createElement('i');ponto.className='fluxo';ponto.style.offsetPath=`path('${d}')`;
        ponto.style.animationDuration=Math.max(2.4,L/110).toFixed(2)+'s';ponto.style.animationDelay=((atraso+900)/1000+k*.37%1.2).toFixed(2)+'s';
        svg.after(ponto);
      }
    });
    m.querySelectorAll('[data-no]').forEach(n=>{
      const linhas=()=>svg.querySelectorAll(`[data-a="${n.dataset.no}"],[data-b="${n.dataset.no}"]`);
      n.onmouseenter=()=>linhas().forEach(p=>p.classList.add('acende'));
      n.onmouseleave=()=>linhas().forEach(p=>p.classList.remove('acende'));
    });
  }
  document.fonts&&document.fonts.ready.then(()=>ligas(telas[atual]));

  /* ---------------------------------------------------------- temporizador
     Os botões de cada tela abrem sozinhos, um de cada vez, com tempo para ler.
     O primeiro clique da pessoa dentro da tela para o temporizador até ela sair e voltar. */
  function roteiro(cls,cfg){(autos[cls]=autos[cls]||[]).push(cfg);}
  // PDF: tela com botões vira uma página por botão (fonte/gerar-pdf.mjs chama estas duas)
  const SO_UMA_PAGINA=['s-planta','s-papeis','s-cine'];
  const cfgPdf=()=>{const t=$('.tela.ativa');return SO_UMA_PAGINA.includes(t.classList[1])?null:[t,(autos[t.classList[1]]||[])[0]];};
  window.__pdfEstados=()=>{const r=cfgPdf();if(!r||!r[1])return 0;const n=r[1].itens(r[0]).length;return n>1?n:0;};
  window.__pdfEstado=k=>{const [t,c]=cfgPdf();c.itens(t)[k].click();};
  const leitura=txt=>Math.max(4500,Math.min(12000,3000+String(txt||'').replace(/\s+/g,' ').trim().length*45));
  function pararAutos(){autoAtivos.forEach(clearTimeout);autoAtivos=[];$$('.relogio-auto').forEach(r=>r.remove());}
  function iniciarAutos(t){
    if(modoPdf)return;
    (autos[t.classList[1]]||[]).forEach(cfg=>{
      const itens=cfg.itens(t),n=itens.length;if(!n)return;
      const ms=k=>cfg.ms?cfg.ms(k):leitura(cfg.texto?cfg.texto(k,t):itens[k].textContent)+(cfg.extra||0);
      let i=cfg.inicio?cfg.inicio():Math.max(0,itens.findIndex(x=>x.matches('.on,.aberto')||x.parentElement.classList.contains('on')||x.parentElement.classList.contains('aberto')));
      function relogio(k,dur){
        const alvo=itens[k];
        $$('.relogio-auto',t).forEach(r=>{if(r.parentElement&&itens.includes(r.parentElement))r.remove();});
        if(getComputedStyle(alvo).position==='static')alvo.style.position='relative';
        const r=document.createElement('i');r.className='relogio-auto';alvo.appendChild(r);
        r.style.transitionDuration=dur+'ms';void r.offsetWidth;r.classList.add('corre');
      }
      function passo(){
        if(i+1>=n&&cfg.laco===false){$$('.relogio-auto',t).forEach(r=>r.remove());return;}
        i=(i+1)%n;itens[i].click();
        if(i+1>=n&&cfg.laco===false)return;
        const d=ms(i);relogio(i,d);autoAtivos.push(setTimeout(passo,d));
      }
      if(i<0){autoAtivos.push(setTimeout(passo,cfg.primeiro||2500));return;}
      const d=ms(i);relogio(i,d);autoAtivos.push(setTimeout(passo,d));
    });
  }
  stage.addEventListener('pointerdown',e=>{if(e.isTrusted&&e.target.closest('.tela.ativa'))pararAutos();},true);

  /* ---------------------------------------------------------- início */
  const h=parseInt(location.hash.slice(1),10);
  const n0=isNaN(h)?0:Math.max(0,Math.min(total-1,h-1));
  telas.forEach(t=>t.classList.remove('ativa'));atual=n0;telas[n0].classList.add('ativa');
  atual=n0===0?1:0;aplicar(n0);
  telas.forEach((t,i)=>{if(i!==n0)t.classList.remove('ativa');});
})();
