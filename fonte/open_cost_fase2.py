"""Open cost da fase 2 do BID Alpargatas (Havaianas Aura, Dia das Mães 2027).

Monta a planilha com as três estruturas pedidas no e-mail da Alpargatas (DTC Lojas Próprias e DTC
Franquias dedicadas, B2B com estrutura única), tributos com a reforma tributária, custos adicionais,
tabela de projetos e o resumo do fee mensal fixo.

Custos (salário/hora, overhead, margem, alíquotas) ficam como entrada em amarelo para a 75 LAB preencher.
Saída em proposta/ (fora do repositório público).

Rodar: python3 fonte/open_cost_fase2.py proposta/75LAB_Open_Cost_Havaianas_BID_Fase2.xlsx
"""
import sys

import openpyxl
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

H_FTE_MES = 176  # 22 dias úteis x 8 h

LP = [
    ('Gestor(a) de conta DTC Lojas Próprias', 'Sênior', 1, 1.00,
     'Dedicado às lojas próprias: pauta com o trade, cronograma, vitrine, cenografia e ativação do mezanino da Oscar Freire.'),
    ('Designer 3D e engenharia de PDV', 'Pleno', 1, 1.00,
     'Mesa Big Hello, vitrine e cenografia: modelagem, render para aprovação e projeto executivo por formato de loja.'),
    ('Designer gráfico e arte-final', 'Pleno', 1, 1.00,
     'Desdobramento do KV nas peças das lojas próprias, embalagens (sacolas, luvas, envelopes) e arte-final para a gráfica.'),
    ('Produtor(a) de campo', 'Pleno', 1, 1.00,
     'Protótipo testado em loja, acompanhamento de instalação e checagem com foto pelo QR.'),
    ('Diretor(a) de criação (compartilhado)', 'Sênior', 1, 0.30,
     'Mesma pessoa em Franquias (30%) e B2B (30%). Uma só direção de criação para a unicidade da marca.'),
    ('Arquiteto(a) e 3D (compartilhado)', 'Sênior', 1, 0.40,
     'Mesma pessoa em Franquias (20%) e B2B (40%). Lojas modeladas, plantas e projetos especiais.'),
    ('Produtor(a) de fornecedores (compartilhado)', 'Sênior', 1, 0.40,
     'Mesma pessoa em Franquias (40%) e B2B (20%). Compra por família de material e três cotações por peça.'),
    ('Analista fiscal (compartilhado)', 'Pleno', 1, 0.30,
     'Mesma pessoa em Franquias (30%) e B2B (40%). Faturamento, SEFAZ e pagamentos a fornecedores.'),
]

FR = [
    ('Gestor(a) de conta DTC Franquias', 'Sênior', 1, 1.00,
     'Dedicado às franquias: pauta com o trade, adesão das franquias e grade de peças por loja.'),
    ('Designer gráfico e arte-final', 'Pleno', 1, 1.00,
     'Peças por formato de loja franqueada (mesa atual, glorifier, caixotes) e kits de embalagem presenteável.'),
    ('Atendimento à rede e SAC', 'Pleno', 1, 1.00,
     'Franqueados por WhatsApp e e-mail numa caixa só, com ticket por loja e prazo.'),
    ('Analista de logística', 'Pleno', 1, 1.00,
     'Kitting por franquia, envio para o Brasil todo, recebimento pelo QR e ocorrências.'),
    ('Diretor(a) de criação (compartilhado)', 'Sênior', 1, 0.30,
     'Mesma pessoa em Lojas Próprias (30%) e B2B (30%).'),
    ('Arquiteto(a) e 3D (compartilhado)', 'Sênior', 1, 0.20,
     'Mesma pessoa em Lojas Próprias (40%) e B2B (40%).'),
    ('Produtor(a) de fornecedores (compartilhado)', 'Sênior', 1, 0.40,
     'Mesma pessoa em Lojas Próprias (40%) e B2B (20%).'),
    ('Analista fiscal (compartilhado)', 'Pleno', 1, 0.30,
     'Mesma pessoa em Lojas Próprias (30%) e B2B (40%).'),
]

B2B = [
    ('Gestor(a) de conta B2B', 'Sênior', 1, 1.00,
     'Estrutura única para alimentar e especializado: pauta, cronograma, negociação de ponto extra com o comercial da Alpargatas.'),
    ('Designer gráfico sênior', 'Sênior', 1, 1.00,
     'MPDVs de gôndola (stopper, testeira, moldura, tag, wobbler, clip strip, placa de carrinho) e artes rápidas.'),
    ('Produtor(a) de fornecedores', 'Pleno', 1, 1.00,
     'Volume, negociação de peças em lote, amostras e QA por lote.'),
    ('Analista de implementação', 'Pleno', 1, 1.00,
     'CDs das redes, distribuidores, promotoria e positivação dos PDVs medida pelo QR.'),
    ('Diretor(a) de criação (compartilhado)', 'Sênior', 1, 0.30,
     'Mesma pessoa em Lojas Próprias (30%) e Franquias (30%).'),
    ('Arquiteto(a) e 3D (compartilhado)', 'Sênior', 1, 0.40,
     'Mesma pessoa em Lojas Próprias (40%) e Franquias (20%). Ponta de gôndola, ilha e store in store.'),
    ('Produtor(a) de fornecedores (compartilhado)', 'Sênior', 1, 0.20,
     'Mesma pessoa em Lojas Próprias (40%) e Franquias (40%). Compra consolidada por família de material.'),
    ('Analista fiscal (compartilhado)', 'Pleno', 1, 0.40,
     'Mesma pessoa em Lojas Próprias (30%) e Franquias (30%).'),
]

# horas médias por entrega medidas no Ariuno (jul a nov/2026, dados/ariuno_fase2.md)
PROJETOS = [
    ('KV e desdobramento', 'KV de campanha ou desdobramento base nos formatos', 'DTC/B2B', 3.5, 'Média de 27 entregas com hora apontada.'),
    ('Peça de campanha e PDV', 'Criação de peça de PDV, display, ativação ou enxoval', 'DTC/B2B', 5.3, 'Média de 99 entregas com hora apontada.'),
    ('Arte rápida', 'Post, carrossel, e-mail ou peça digital a partir do KV vigente', 'DTC/B2B', 3.1, 'Média de 90 entregas com hora apontada.'),
    ('Arte-final tática', 'Adaptação e finalização de peça tática para a gráfica', 'DTC/B2B', 2.4, 'Média de 31 entregas com hora apontada.'),
    ('Rodada de ajuste', 'Ajuste pedido pelo cliente depois da 2ª rodada incluída no fee', 'DTC/B2B', 2.8, 'Média de 163 rodadas com hora apontada.'),
    ('Render 3D e mockup', 'Render de aprovação por formato de loja', 'DTC/B2B', 8.8, 'Média de 20 entregas com hora apontada.'),
    ('Projeto 3D de display', 'Modelagem de display, ilha, ponta ou mesa', 'DTC/B2B', 11.3, 'Média de 9 projetos com hora apontada.'),
    ('Projeto executivo', 'Executivo, faca e desenho técnico para fornecedor', 'DTC/B2B', 4.8, 'Média de 23 entregas com hora apontada.'),
    ('Stand e cenografia', 'Etapa de projeto de stand, cenografia ou vitrine especial', 'DTC', 8.1, 'Média por etapa (16 etapas com hora); um projeto completo tem várias etapas.'),
    ('Orçamento com fornecedores', 'Três cotações e comparativo aberto por peça', 'DTC/B2B', 2.9, 'Média de 65 orçamentos com hora apontada.'),
]

CUSTOS_ADIC = [
    ('Produção física das peças', 'Repasse do orçamento aprovado', 'por peça ou lote', 'Gráfica, marcenaria, serralheria e acrílico. Três cotações por peça, comparativo aberto, sem BV nem comissão.'),
    ('Protótipos e amostras', 'Repasse do orçamento aprovado', 'por peça', 'Protótipo das peças estruturais antes do lote.'),
    ('Frete e logística', 'Repasse do orçamento aprovado', 'por envio', 'Envio às lojas próprias, às franquias e aos CDs das redes.'),
    ('Kitting e armazenagem', 'Repasse do orçamento aprovado', 'por kit ou posição', 'Separação por loja, etiqueta e romaneio.'),
    ('Instalação e montagem', 'Repasse do orçamento aprovado', 'por loja', 'Montadores fora do horário de loja; franquias instalam com guia e suporte remoto.'),
    ('Viagens fora da Grande São Paulo', 'Repasse com prestação de contas', 'por viagem', 'Passagem, hospedagem e diária, sempre aprovadas antes.'),
    ('Fotografia, shooting e vídeo', 'Orçamento à parte', 'por produção', 'Quando a campanha pedir imagem nova além do KV entregue pela Alpargatas.'),
    ('Licenças de imagem, fonte e música', 'Repasse', 'por licença', 'Somente quando o material não vier licenciado pela Alpargatas.'),
    ('Etiquetas QR e rastreadores GPS ou BLE', 'Repasse do custo do material', 'por peça ou dispositivo', 'Etiqueta QR nas peças de campanha; GPS ou BLE só em ativo caro que volta.'),
    ('Tiragens extras e reposição', 'Orçamento à parte', 'por lote', 'Fora da grade aprovada por loja.'),
    ('Projetos acima do escopo do fee', 'Tabela de projetos (aba Projetos)', 'por entrega', 'Horas medidas no Ariuno vezes o valor de H/H da tabela.'),
    ('Seguro de carga', 'Repasse', 'por envio', 'Quando o valor transportado pedir.'),
]

ARIAL = 'Arial'
AMARELO = PatternFill('solid', fgColor='FFF2CC')
CAB = PatternFill('solid', fgColor='2F4A55')
AZUL_CLARO = PatternFill('solid', fgColor='E3ECEF')
CREME = PatternFill('solid', fgColor='FFF6EA')
FINA = Side(style='thin', color='B7C4C9')
BORDA = Border(left=FINA, right=FINA, top=FINA, bottom=FINA)
F_TIT = Font(name=ARIAL, size=14, bold=True, color='2F4A55')
F_SUB = Font(name=ARIAL, size=10, color='555555')
F_CAB = Font(name=ARIAL, size=10, bold=True, color='FFFFFF')
F_TXT = Font(name=ARIAL, size=10, color='000000')
F_ENT = Font(name=ARIAL, size=10, color='0000FF')       # entrada
F_LINK = Font(name=ARIAL, size=10, color='008000')      # link para outra aba
F_TOT = Font(name=ARIAL, size=10, bold=True, color='000000')
F_NOTA = Font(name=ARIAL, size=9, color='555555', italic=True)
RS = 'R$ #,##0.00;(R$ #,##0.00);"-"'
PCT = '0.00%;(0.00%);"-"'


def cab(ws, r, titulos, larguras=None):
    for i, t in enumerate(titulos, 1):
        c = ws.cell(r, i, t)
        c.font, c.fill, c.border = F_CAB, CAB, BORDA
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[r].height = 32
    if larguras:
        for i, w in enumerate(larguras, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def cel(ws, ref, v, fonte=F_TXT, fmt=None, al='left', fill=None, wrap=False):
    c = ws[ref]
    c.value = v
    c.font = fonte
    c.border = BORDA
    c.alignment = Alignment(horizontal=al, vertical='center', wrap_text=wrap)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def titulo(ws, t, sub):
    ws['A1'] = t
    ws['A1'].font = F_TIT
    ws['A2'] = sub
    ws['A2'].font = F_SUB
    ws.sheet_view.showGridLines = False


def estrutura(ws, nome, linhas, base_ref=None):
    titulo(ws, f'OPEN COST DE RECURSOS · {nome}',
           'Fee mensal fixo, sem honorários, agenciamento, BV ou comissão. Preencher as células em amarelo (texto azul = entrada).')
    cel(ws, 'A3', 'Horas/mês de 1 FTE', F_SUB)
    if base_ref:
        cel(ws, 'B3', base_ref, F_LINK, '#,##0" h"', 'center')
    else:
        cel(ws, 'B3', H_FTE_MES, F_ENT, '#,##0" h"', 'center')
    ws['C3'] = '22 dias úteis × 8 h. Horas Mês = FTE × esta base. Custo salarial/hora = (salário + encargos + benefícios) ÷ esta base.'
    ws['C3'].font = F_NOTA
    cab(ws, 5, ['Cargo / Função', 'Senioridade', 'Qtd (headcount)', 'Dedicação (FTE)', 'Horas mês',
                'Custo salarial/hora (R$)', 'Overhead %', 'Margem %', 'Custo H/H final (R$)',
                'Custo mensal por recurso (R$)', 'Custo total mensal (R$)', 'Observações / perfil'],
        [40, 12, 11, 11, 10, 15, 11, 11, 15, 17, 17, 70])
    ini = 6
    for i, (cargo, sen, qtd, fte, obs) in enumerate(linhas):
        r = ini + i
        fill = AZUL_CLARO if i % 2 else None
        cel(ws, f'A{r}', cargo, fill=fill, wrap=True)
        cel(ws, f'B{r}', sen, al='center', fill=fill)
        cel(ws, f'C{r}', qtd, F_ENT, '0', 'center', fill)
        cel(ws, f'D{r}', fte, F_ENT, '0%', 'center', fill)
        cel(ws, f'E{r}', f'=D{r}*$B$3', fmt='#,##0', al='center', fill=fill)
        cel(ws, f'F{r}', None, F_ENT, RS, 'right', fill)
        cel(ws, f'G{r}', None, F_ENT, PCT, 'center', fill)
        cel(ws, f'H{r}', None, F_ENT, PCT, 'center', fill)
        cel(ws, f'I{r}', f'=F{r}*(1+G{r})*(1+H{r})', fmt=RS, al='right', fill=fill)
        cel(ws, f'J{r}', f'=I{r}*E{r}', fmt=RS, al='right', fill=fill)
        cel(ws, f'K{r}', f'=C{r}*J{r}', fmt=RS, al='right', fill=fill)
        cel(ws, f'L{r}', obs, F_NOTA, fill=fill, wrap=True)
        ws.row_dimensions[r].height = 30
    fim = ini + len(linhas) - 1
    tot = fim + 1
    for col in 'ABCDEFGHIJKL':
        cel(ws, f'{col}{tot}', None, F_TOT, fill=CREME)
    ws[f'A{tot}'] = f'TOTAL FEE MENSAL · {nome}'
    ws[f'C{tot}'] = f'=SUM(C{ini}:C{fim})'
    ws[f'D{tot}'] = f'=SUM(D{ini}:D{fim})'
    ws[f'D{tot}'].number_format = '0.00" FTE"'
    ws[f'E{tot}'] = f'=SUM(E{ini}:E{fim})'
    ws[f'E{tot}'].number_format = '#,##0'
    ws[f'G{tot}'] = f'=IFERROR(AVERAGE(G{ini}:G{fim}),"")'
    ws[f'G{tot}'].number_format = PCT
    ws[f'H{tot}'] = f'=IFERROR(AVERAGE(H{ini}:H{fim}),"")'
    ws[f'H{tot}'].number_format = PCT
    ws[f'K{tot}'] = f'=SUM(K{ini}:K{fim})'
    ws[f'K{tot}'].number_format = RS
    ws[f'L{tot}'] = 'Os 4 compartilhados aparecem nas três estruturas com a fração de cada uma; somados, cada um fecha 1 pessoa.'
    ws[f'L{tot}'].font = F_NOTA
    ws[f'L{tot}'].alignment = Alignment(wrap_text=True, vertical='center')
    ws.row_dimensions[tot].height = 30
    ws.conditional_formatting.add(f'F{ini}:H{fim}', FormulaRule(formula=[f'ISBLANK(F{ini})'], fill=AMARELO))
    ws.freeze_panes = 'B6'
    return ini, fim, tot


def tributos(ws):
    titulo(ws, 'TRIBUTOS E REFORMA TRIBUTÁRIA',
           'Alíquotas sobre o faturamento do fee. Preencher com a contabilidade (amarelo). Base legal: EC 132/2023 e LC 214/2025.')
    cab(ws, 4, ['Tributo', 'Dez/2026 (regime atual)', '2027 (CBS plena)', 'Observação'], [44, 22, 22, 90])
    linhas = [
        ('ISS (por dentro)', 0.05, 0.05, 'Município de São Paulo. Confirmar a alíquota do código de serviço da 75 LAB. Continua igual até 2028.'),
        ('PIS (por dentro)', 0.0065, 0, 'Regime cumulativo do lucro presumido. Extinto em 2027.'),
        ('COFINS (por dentro)', 0.03, 0, 'Regime cumulativo do lucro presumido. Extinta em 2027.'),
        ('IRPJ sobre a receita (por dentro)', 0.048, 0.048, 'Lucro presumido: 32% de presunção × 15%. O adicional de 10% depende do lucro presumido do trimestre.'),
        ('CSLL sobre a receita (por dentro)', 0.0288, 0.0288, 'Lucro presumido: 32% de presunção × 9%.'),
        ('CBS (por fora, destacada na nota)', 0, 0.087, 'Em 2026 a CBS de 0,9% é de teste e compensável, sem custo. Em 2027 entra plena; 8,7% é a referência estimada pela Fazenda menos 0,1 p.p. do IBS de teste. A alíquota definitiva sai por resolução do Senado.'),
        ('IBS (por fora, destacado na nota)', 0, 0.001, 'Em 2027 e 2028, 0,1% de teste. Sobe de 2029 a 2032, quando ISS e ICMS caem por etapas; pleno em 2033.'),
    ]
    for i, (n, a, b, obs) in enumerate(linhas):
        r = 5 + i
        cel(ws, f'A{r}', n)
        cel(ws, f'B{r}', a, F_ENT, PCT, 'center', AMARELO)
        cel(ws, f'C{r}', b, F_ENT, PCT, 'center', AMARELO)
        cel(ws, f'D{r}', obs, F_NOTA, wrap=True)
        ws.row_dimensions[r].height = 30
    # 5 ISS, 6 PIS, 7 COFINS, 8 IRPJ, 9 CSLL, 10 CBS, 11 IBS
    cel(ws, 'A13', 'Soma dos tributos por dentro', F_TOT, fill=CREME)
    cel(ws, 'B13', '=B5+B6+B7+B8+B9', F_TOT, PCT, 'center', CREME)
    cel(ws, 'C13', '=C5+C6+C7+C8+C9', F_TOT, PCT, 'center', CREME)
    cel(ws, 'D13', 'Entram no preço: preço sem IVA = custo ÷ (1 − esta soma).', F_NOTA, fill=CREME)
    cel(ws, 'A14', 'IVA por fora (CBS + IBS)', F_TOT, fill=CREME)
    cel(ws, 'B14', '=B10+B11', F_TOT, PCT, 'center', CREME)
    cel(ws, 'C14', '=C10+C11', F_TOT, PCT, 'center', CREME)
    cel(ws, 'D14', 'Destacado na nota sobre o preço sem IVA. A Alpargatas, no regime regular, toma esse valor como crédito.', F_NOTA, fill=CREME, wrap=True)
    cel(ws, 'A15', 'Regime da 75 LAB considerado', F_TXT)
    cel(ws, 'B15', 'Lucro presumido', F_ENT, al='center', fill=AMARELO)
    cel(ws, 'C15', 'Lucro presumido', F_ENT, al='center', fill=AMARELO)
    cel(ws, 'D15', 'Se o regime for outro (lucro real ou Simples), trocar as alíquotas acima com a contabilidade.', F_NOTA)

    cab(ws, 17, ['Transição (LC 214/2025)', 'CBS', 'IBS', 'ISS e ICMS'])
    trans = [
        ('2026', '0,9% de teste, compensável', '0,1% de teste, compensável', 'Integrais'),
        ('2027 e 2028', 'Plena (PIS e Cofins extintos)', '0,1% de teste', 'Integrais'),
        ('2029', 'Plena', 'Sobe na proporção da queda', 'Redução de 10%'),
        ('2030', 'Plena', 'Sobe na proporção da queda', 'Redução de 20%'),
        ('2031', 'Plena', 'Sobe na proporção da queda', 'Redução de 30%'),
        ('2032', 'Plena', 'Sobe na proporção da queda', 'Redução de 40%'),
        ('2033', 'Plena', 'Pleno', 'Extintos'),
    ]
    for i, linha in enumerate(trans):
        r = 18 + i
        for j, v in enumerate(linha):
            cel(ws, f'{"ABCD"[j]}{r}', v, al='center' if j else 'left')
    ws['A26'] = ('Regra do contrato proposta: cada mudança de alíquota da transição é repassada no mês em que vale, '
                 'pela fórmula desta aba, sem renegociar o fee.')
    ws['A26'].font = F_NOTA


def resumo(ws, tots):
    titulo(ws, 'RESUMO · FEE MENSAL FIXO POR ESTRUTURA',
           'Havaianas Aura · Dia das Mães 2027 · BID Fase 2 · 75 LAB. Valores calculados a partir das abas de estrutura e de tributos.')
    ws['A3'] = 'Legenda: amarelo e texto azul = preencher; verde = vem de outra aba; preto = fórmula.'
    ws['A3'].font = F_NOTA
    cab(ws, 5, ['Estrutura', 'Headcount (linhas)', 'FTE', 'Horas/mês', 'Custo mensal sem tributos (R$)',
                'Preço sem IVA dez/2026 (R$)', 'Preço sem IVA 2027 (R$)', 'CBS + IBS 2027 (R$)',
                'Total da nota 2027 (R$)', 'Observação'], [34, 13, 10, 11, 20, 20, 20, 18, 20, 60])
    nomes = [('DTC Lojas Próprias', 'Estrutura LP', 'Estrutura dedicada.'),
             ('DTC Franquias', 'Estrutura Franquias', 'Estrutura dedicada.'),
             ('B2B Varejo', 'Estrutura B2B', 'Estrutura única para alimentar e especializado.')]
    for i, ((nome, aba, obs), tot) in enumerate(zip(nomes, tots)):
        r = 6 + i
        q = f"'{aba}'"
        cel(ws, f'A{r}', nome)
        cel(ws, f'B{r}', f'={q}!C{tot}', F_LINK, '0', 'center')
        cel(ws, f'C{r}', f'={q}!D{tot}', F_LINK, '0.00', 'center')
        cel(ws, f'D{r}', f'={q}!E{tot}', F_LINK, '#,##0', 'center')
        cel(ws, f'E{r}', f'={q}!K{tot}', F_LINK, RS, 'right')
        cel(ws, f'F{r}', f"=IFERROR(E{r}/(1-Tributos!$B$13),0)", fmt=RS, al='right')
        cel(ws, f'G{r}', f"=IFERROR(E{r}/(1-Tributos!$C$13),0)", fmt=RS, al='right')
        cel(ws, f'H{r}', f'=G{r}*Tributos!$C$14', fmt=RS, al='right')
        cel(ws, f'I{r}', f'=G{r}+H{r}', fmt=RS, al='right')
        cel(ws, f'J{r}', obs, F_NOTA)
    r = 9
    for col in 'ABCDEFGHIJ':
        cel(ws, f'{col}{r}', None, F_TOT, fill=CREME)
    ws['A9'] = 'TOTAL FEE MENSAL'
    ws['B9'] = '=SUM(B6:B8)'
    ws['C9'] = '=SUM(C6:C8)'
    ws['C9'].number_format = '0.00'
    ws['D9'] = '=SUM(D6:D8)'
    ws['D9'].number_format = '#,##0'
    for col in 'EFGHI':
        ws[f'{col}9'] = f'=SUM({col}6:{col}8)'
        ws[f'{col}9'].number_format = RS
    ws['J9'] = 'Headcount conta os compartilhados nas três abas; em pessoas físicas são 16.'
    ws['J9'].font = F_NOTA
    notas = [
        'Modelo de remuneração: fee mensal fixo por estrutura. Sem honorários, agenciamento, BV ou comissão sobre produção ou terceiros.',
        'Incluído no fee: criação, desdobramento, 3D, executivos, orçamentos, gestão da operação (Ariuno, central da rede, SharePoint, painel do QR) e até 2 rodadas de ajuste por peça.',
        'Fora do fee: aba Custos adicionais (sempre com orçamento aprovado antes) e aba Projetos (entregas acima do escopo).',
        'Tributos: aba Tributos. Em 2027 a CBS é destacada na nota e gera crédito para a Alpargatas no regime regular; o custo efetivo para a Alpargatas é o preço sem IVA.',
        'Dimensionamento: horas e prazos medidos no Ariuno (1.155 entregas, jul a nov/2026). O case da fase 2 consome de 246 a 571 h de agência para os 3 canais.',
    ]
    for i, n in enumerate(notas):
        ws[f'A{11 + i}'] = n
        ws[f'A{11 + i}'].font = F_SUB


def projetos(ws):
    titulo(ws, 'TABELA DE PROJETOS · ENTREGAS ACIMA DO ESCOPO DO FEE',
           'Horas estimadas = média medida no Ariuno (jul a nov/2026). Valor = horas × valor de H/H (preencher em B3).')
    cel(ws, 'A3', 'Valor de H/H para projetos (R$)', F_SUB)
    cel(ws, 'B3', None, F_ENT, RS, 'right', AMARELO)
    cab(ws, 5, ['Categoria de entrega', 'Descrição do escopo', 'Canal', 'Horas estimadas', 'Valor por entrega (R$)',
                'Honorário ou BV', 'Premissa'], [30, 54, 11, 13, 20, 14, 60])
    for i, (cat, desc, canal, h, prem) in enumerate(PROJETOS):
        r = 6 + i
        fill = AZUL_CLARO if i % 2 else None
        cel(ws, f'A{r}', cat, fill=fill)
        cel(ws, f'B{r}', desc, fill=fill, wrap=True)
        cel(ws, f'C{r}', canal, al='center', fill=fill)
        cel(ws, f'D{r}', h, F_ENT, '#,##0.0', 'center', fill)
        cel(ws, f'E{r}', f'=IF($B$3="","",D{r}*$B$3)', fmt=RS, al='right', fill=fill)
        cel(ws, f'F{r}', 0, fmt='0%', al='center', fill=fill)
        cel(ws, f'G{r}', prem, F_NOTA, fill=fill, wrap=True)
        ws.row_dimensions[r].height = 28
    ws.freeze_panes = 'A6'


def adicionais(ws):
    titulo(ws, 'CUSTOS ADICIONAIS · FORA DO FEE',
           'Nada aqui entra sem orçamento aprovado pela Alpargatas. Repasse a custo, sem honorário, BV ou comissão.')
    cab(ws, 4, ['Item', 'Como é cobrado', 'Unidade', 'Valor de referência (R$)', 'Observação'], [38, 32, 22, 20, 80])
    for i, (item, como, un, obs) in enumerate(CUSTOS_ADIC):
        r = 5 + i
        fill = AZUL_CLARO if i % 2 else None
        cel(ws, f'A{r}', item, fill=fill)
        cel(ws, f'B{r}', como, fill=fill)
        cel(ws, f'C{r}', un, al='center', fill=fill)
        cel(ws, f'D{r}', None, F_ENT, RS, 'right', AMARELO)
        cel(ws, f'E{r}', obs, F_NOTA, fill=fill, wrap=True)
        ws.row_dimensions[r].height = 28


def main(saida):
    wb = openpyxl.Workbook()
    ws_res = wb.active
    ws_res.title = 'Resumo'
    lp = estrutura(wb.create_sheet('Estrutura LP'), 'DTC LOJAS PRÓPRIAS', LP)
    fr = estrutura(wb.create_sheet('Estrutura Franquias'), 'DTC FRANQUIAS', FR, "='Estrutura LP'!B3")
    b2 = estrutura(wb.create_sheet('Estrutura B2B'), 'B2B VAREJO', B2B, "='Estrutura LP'!B3")
    tributos(wb.create_sheet('Tributos'))
    adicionais(wb.create_sheet('Custos adicionais'))
    projetos(wb.create_sheet('Projetos'))
    resumo(ws_res, [lp[2], fr[2], b2[2]])
    # conferência: cada compartilhado soma 1 FTE nas três abas
    for nome in ('Diretor(a) de criação', 'Arquiteto(a) e 3D', 'Produtor(a) de fornecedores (compartilhado)', 'Analista fiscal'):
        s = sum(f for lst in (LP, FR, B2B) for (c, _, _, f, _) in lst if c.startswith(nome) and 'compartilhado' in c)
        assert abs(s - 1) < 0.11, (nome, s)
    wb.calculation.fullCalcOnLoad = True
    wb.save(saida)
    print('ok', saida)


if __name__ == '__main__':
    main(sys.argv[1])
