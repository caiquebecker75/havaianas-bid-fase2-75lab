"""Open cost da fase 2 do BID Alpargatas, alinhado ao "Documento base · Fase 2 · 75 LAB".

15 posições dedicadas, divididas entre Lojas Próprias, Franquias e B2B com o percentual do documento.
Preço de cada posição = custo direto × (1 + overhead) ÷ (1 − tributos − margem), como no documento.
O custo direto por hora de cada pessoa fica em amarelo para a 75 LAB preencher; overhead (21%),
margem (18%) e tributos (19,53%, lucro presumido) vêm do documento e podem ser ajustados.
Saída em proposta/ (fora do repositório público). Os valores nunca vão para o deck.

Rodar: python3 fonte/open_cost_fase2.py proposta/75LAB_Open_Cost_Havaianas_BID_Fase2.xlsx
"""
import sys

import openpyxl
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

H_FTE = 176

# cargo, senioridade, [LP, FR, B2B] em %, perfil (documento base, seção 1)
POSICOES = [
    ('Gestor(a) de conta Lojas Próprias', 'Sênior', [100, 0, 0], 'Ponto focal único das lojas próprias, do briefing à peça instalada.'),
    ('Gestor(a) de conta Franquias', 'Sênior', [0, 100, 0], 'Frente de franquias: adesão da rede, pedido consolidado e resposta ao franqueado.'),
    ('Designer 3D e engenharia de PDV', 'Pleno', [70, 30, 0], 'Executivo das peças estruturais, mesa Big Hello, vitrine e loja modelada por cluster.'),
    ('Designer gráfico e arte-final', 'Pleno', [45, 55, 0], 'Desdobramento do KV no DTC, embalagens comercializadas e arte-final com prova de cor.'),
    ('Produtor(a) de fornecedores', 'Sênior', [35, 65, 0], 'Três cotações por família, equalização, recomendação, protótipo e QA por lote.'),
    ('Produtor(a) de campo e SAC', 'Pleno', [35, 65, 0], 'Teste de protótipo em loja, implementação fotografada e primeira resposta à rede.'),
    ('Analista de logística', 'Pleno', [25, 75, 0], 'Distribuição loja a loja, rastreio por peça e kit de embalagem das franquias.'),
    ('Gestor(a) de conta B2B', 'Sênior', [0, 0, 100], 'Canal B2B alimentar e especializado, calendário casado com a negociação de volume.'),
    ('Designer gráfico sênior', 'Sênior', [0, 0, 100], 'MPDVs do alimentar e do especializado, por tipo e tamanho de PDV.'),
    ('Designer de artes rápidas', 'Pleno', [0, 0, 100], 'Arte rápida em 1 a 2 dias úteis, fora da fila da campanha.'),
    ('Produtor(a) de fornecedores B2B', 'Pleno', [0, 0, 100], 'Compra do volume do canal, amostra aprovada e conferência de lote.'),
    ('Analista de logística e implementação', 'Pleno', [0, 0, 100], 'Distribuição às redes, instalação assistida e remoção ao fim do ciclo.'),
    ('Diretor(a) de criação', 'Diretor', [33, 17, 50], 'Uma só direção de arte nas três frentes: unicidade de marca.'),
    ('Arquiteto(a) e 3D', 'Sênior', [27, 7, 66], 'Cenografia do mezanino OF, vitrine e engage do especializado, ambientação nas redes.'),
    ('Analista fiscal', 'Pleno', [20, 30, 50], 'Conferência de nota, SEFAZ e CFOP, homologação de fornecedor e reforma tributária.'),
]
FRENTES = [('Lojas Próprias', 0), ('Franquias', 1), ('B2B', 2)]

CUSTOS_ADIC = [
    ('Produção das peças', 'Pago pela Alpargatas direto ao fornecedor', 'Mínimo de três propostas válidas, equalização e recomendação justificada.'),
    ('Distribuição', 'Pago pela Alpargatas direto ao fornecedor', 'Transportadora e operador logístico cotados.'),
    ('Positivação', 'Pago pela Alpargatas direto ao fornecedor', 'Promotoria e colocação no PDV.'),
    ('Armazenagem', 'Pago pela Alpargatas direto ao fornecedor', 'Quando houver estoque de material.'),
    ('Mídia e veiculação', 'Pago pela Alpargatas direto ao fornecedor', 'Fora do escopo da agência de trade.'),
    ('Licenciamento de imagem, cachê de talento e direito de imagem', 'Pago pela Alpargatas direto ao fornecedor', 'Somente quando a campanha pedir.'),
    ('Impressão do QR nas peças', 'Entra no custo da própria peça impressa', 'A tecnologia de rastreio, o painel e a geração dos códigos estão no fee.'),
    ('Etiqueta eletrônica de GPS', 'Cotada como material de produção', 'Hardware; a plataforma que lê a etiqueta está no fee.'),
]

ARIAL = 'Arial'
AMARELO = PatternFill('solid', fgColor='FFF2CC')
CAB = PatternFill('solid', fgColor='2F4A55')
LISTRA = PatternFill('solid', fgColor='E3ECEF')
CREME = PatternFill('solid', fgColor='FFF6EA')
FINA = Side(style='thin', color='B7C4C9')
BORDA = Border(left=FINA, right=FINA, top=FINA, bottom=FINA)
F_TIT = Font(name=ARIAL, size=14, bold=True, color='2F4A55')
F_SUB = Font(name=ARIAL, size=10, color='555555')
F_CAB = Font(name=ARIAL, size=10, bold=True, color='FFFFFF')
F_TXT = Font(name=ARIAL, size=10, color='000000')
F_ENT = Font(name=ARIAL, size=10, color='0000FF')
F_LINK = Font(name=ARIAL, size=10, color='008000')
F_TOT = Font(name=ARIAL, size=10, bold=True)
F_NOTA = Font(name=ARIAL, size=9, color='555555', italic=True)
RS = 'R$ #,##0.00;(R$ #,##0.00);"-"'
PCT = '0.00%;(0.00%);"-"'


def cel(ws, ref, v, fonte=F_TXT, fmt=None, al='left', fill=None, wrap=False):
    c = ws[ref]
    c.value, c.font, c.border = v, fonte, BORDA
    c.alignment = Alignment(horizontal=al, vertical='center', wrap_text=wrap)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def cab(ws, r, titulos, larguras):
    for i, (t, w) in enumerate(zip(titulos, larguras), 1):
        c = ws.cell(r, i, t)
        c.font, c.fill, c.border = F_CAB, CAB, BORDA
        c.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[r].height = 34


def titulo(ws, t, sub):
    ws['A1'], ws['A1'].font = t, F_TIT
    ws['A2'], ws['A2'].font = sub, F_SUB
    ws.sheet_view.showGridLines = False


def premissas(ws):
    titulo(ws, 'PREMISSAS DA FORMAÇÃO DE PREÇO', 'Documento base · Fase 2, seção 3. Entradas em azul; amarelo = conferir.')
    cab(ws, 4, ['Premissa', 'Valor', 'Observação'], [44, 16, 100])
    linhas = [
        ('Horas/mês de 1 pessoa em tempo integral', H_FTE, '#,##0" h"', '22 dias úteis × 8 h.'),
        ('Overhead sobre o custo direto', 0.21, PCT, 'Escritório, softwares, administrativo e contabilidade, rateados sobre o custo das pessoas.'),
        ('Margem líquida sobre a receita', 0.18, PCT, 'Sai da receita: entra dividindo, por isso a margem declarada é a realizada.'),
        ('Tributos sobre a receita', "=Tributos!B10", PCT, 'Vem da aba Tributos (lucro presumido).'),
        ('Encargos sobre o custo direto', 0, PCT, 'Time PJ: a nota já é o custo.'),
    ]
    for i, (n, v, fmt, obs) in enumerate(linhas):
        r = 5 + i
        cel(ws, f'A{r}', n)
        cel(ws, f'B{r}', v, F_LINK if isinstance(v, str) else F_ENT, fmt, 'center', None if isinstance(v, str) else AMARELO)
        cel(ws, f'C{r}', obs, F_NOTA, wrap=True)
    ws['A11'] = 'Preço de cada posição = custo direto × (1 + overhead) ÷ (1 − tributos − margem).'
    ws['A11'].font = F_TOT
    ws['A12'] = 'Cada R$ 1,00 de custo direto vira, na nota:'
    ws['A12'].font = F_SUB
    cel(ws, 'B12', '=(1+B6)/(1-B8-B7)', fmt='0.00', al='center')


def tributos(ws):
    titulo(ws, 'TRIBUTOS · LUCRO PRESUMIDO', 'Documento base · Fase 2, seção 3. Carga vigente e apurada, sem projeção da reforma.')
    cab(ws, 4, ['Tributo', 'Alíquota sobre a receita', 'Base'], [44, 22, 80])
    linhas = [
        ('PIS + COFINS, regime cumulativo', 0.0365, 'Receita bruta.'),
        ('IRPJ, 15% mais adicional de 10%', 0.08, 'Lucro presumido de 32% da receita; adicional cheio, leitura conservadora.'),
        ('CSLL, 9%', 0.0288, 'Lucro presumido de 32% da receita.'),
        ('ISS de São Bernardo do Campo', 0.05, 'Preço do serviço.'),
    ]
    for i, (n, v, b) in enumerate(linhas):
        r = 5 + i
        cel(ws, f'A{r}', n)
        cel(ws, f'B{r}', v, F_ENT, PCT, 'center', AMARELO)
        cel(ws, f'C{r}', b, F_NOTA)
    cel(ws, 'A10', 'Carga total sobre a receita', F_TOT, fill=CREME)
    cel(ws, 'B10', '=SUM(B5:B8)', F_TOT, PCT, 'center', CREME)
    cel(ws, 'C10', 'Usada no divisor da formação de preço.', F_NOTA, fill=CREME)
    notas = [
        'Retenções na fonte: antecipação do tributo da 75 LAB; o desembolso da Alpargatas continua sendo o valor da nota.',
        'Crédito: no regime cumulativo, PIS e COFINS não geram crédito ao contratante.',
        'Reforma tributária (EC 132/2023 e LC 214/2025): a CBS substitui PIS e COFINS e é não cumulativa; passa a gerar crédito.',
        'Compromisso: a carga é revista a cada mudança de faixa, regime ou lei, com memória de cálculo aberta. Se a carga cair, o preço cai junto.',
    ]
    for i, n in enumerate(notas):
        ws[f'A{12 + i}'], ws[f'A{12 + i}'].font = n, F_SUB


def estrutura(ws):
    titulo(ws, 'ESTRUTURA DE ATENDIMENTO · 15 POSIÇÕES DEDICADAS',
           'Preencher o custo direto por hora (amarelo). Dedicação total de cada posição = 100%, dividida entre as frentes.')
    cab(ws, 4, ['Cargo / função', 'Senioridade', 'Qtd', 'Lojas Próprias %', 'Franquias %', 'B2B %', 'Dedicação total',
                'Horas/mês', 'Custo direto/hora (R$)', 'Preço H/H (R$)', 'Preço mensal (R$)', 'Perfil'],
        [36, 11, 6, 12, 12, 10, 11, 10, 15, 14, 16, 70])
    ini = 5
    for i, (cargo, sen, d, perfil) in enumerate(POSICOES):
        r = ini + i
        fill = LISTRA if i % 2 else None
        cel(ws, f'A{r}', cargo, fill=fill)
        cel(ws, f'B{r}', sen, al='center', fill=fill)
        cel(ws, f'C{r}', 1, F_ENT, '0', 'center', fill)
        for j, col in enumerate('DEF'):
            cel(ws, f'{col}{r}', d[j] / 100, F_ENT, '0%', 'center', fill)
        cel(ws, f'G{r}', f'=D{r}+E{r}+F{r}', fmt='0%', al='center', fill=fill)
        cel(ws, f'H{r}', f'=C{r}*G{r}*Premissas!$B$5', fmt='#,##0', al='center', fill=fill)
        cel(ws, f'I{r}', None, F_ENT, RS, 'right', fill)
        cel(ws, f'J{r}', f'=IF(I{r}="","",I{r}*(1+Premissas!$B$6)/(1-Premissas!$B$8-Premissas!$B$7))', fmt=RS, al='right', fill=fill)
        cel(ws, f'K{r}', f'=IF(J{r}="","",J{r}*H{r})', fmt=RS, al='right', fill=fill)
        cel(ws, f'L{r}', perfil, F_NOTA, fill=fill, wrap=True)
    fim = ini + len(POSICOES) - 1
    tot = fim + 1
    for col in 'ABCDEFGHIJKL':
        cel(ws, f'{col}{tot}', None, F_TOT, fill=CREME)
    ws[f'A{tot}'] = 'TOTAL'
    ws[f'C{tot}'] = f'=SUM(C{ini}:C{fim})'
    for col in 'DEF':
        ws[f'{col}{tot}'] = f'=SUM({col}{ini}:{col}{fim})'
        ws[f'{col}{tot}'].number_format = '0.00'
    ws[f'G{tot}'] = f'=SUM(G{ini}:G{fim})'
    ws[f'G{tot}'].number_format = '0.00'
    ws[f'H{tot}'] = f'=SUM(H{ini}:H{fim})'
    ws[f'H{tot}'].number_format = '#,##0'
    ws[f'K{tot}'] = f'=SUM(K{ini}:K{fim})'
    ws[f'K{tot}'].number_format = RS
    ws[f'L{tot}'] = 'Total esperado: 15 posições, 15,00 pessoas em tempo integral, 2.640 horas por mês.'
    ws[f'L{tot}'].font = F_NOTA
    ws.conditional_formatting.add(f'I{ini}:I{fim}', FormulaRule(formula=[f'ISBLANK(I{ini})'], fill=AMARELO))
    ws.freeze_panes = 'B5'
    return ini, fim, tot


def frente(ws, nome, j, ini, fim):
    col = 'DEF'[j]
    titulo(ws, f'FRENTE {nome.upper()}', 'Calculado a partir da aba Estrutura: horas e preço proporcionais à dedicação nesta frente.')
    cab(ws, 4, ['Cargo / função', 'Senioridade', 'Dedicação nesta frente', 'Horas/mês', 'Preço H/H (R$)', 'Preço mensal nesta frente (R$)'],
        [36, 11, 14, 11, 15, 22])
    r = 5
    for i, (cargo, sen, d, _) in enumerate(POSICOES):
        if not d[j]:
            continue
        src = ini + i
        fill = LISTRA if r % 2 else None
        cel(ws, f'A{r}', f'=Estrutura!A{src}', F_LINK, fill=fill)
        cel(ws, f'B{r}', f'=Estrutura!B{src}', F_LINK, al='center', fill=fill)
        cel(ws, f'C{r}', f'=Estrutura!{col}{src}', F_LINK, '0%', 'center', fill)
        cel(ws, f'D{r}', f'=C{r}*Premissas!$B$5', fmt='#,##0', al='center', fill=fill)
        cel(ws, f'E{r}', f'=Estrutura!J{src}', F_LINK, RS, 'right', fill)
        cel(ws, f'F{r}', f'=IF(E{r}="","",E{r}*D{r})', fmt=RS, al='right', fill=fill)
        r += 1
    for c in 'ABCDEF':
        cel(ws, f'{c}{r}', None, F_TOT, fill=CREME)
    ws[f'A{r}'] = f'TOTAL {nome.upper()}'
    ws[f'B{r}'] = f'=COUNT(C5:C{r - 1})'
    ws[f'C{r}'] = f'=SUM(C5:C{r - 1})'
    ws[f'C{r}'].number_format = '0.00'
    ws[f'D{r}'] = f'=SUM(D5:D{r - 1})'
    ws[f'D{r}'].number_format = '#,##0'
    ws[f'F{r}'] = f'=SUM(F5:F{r - 1})'
    ws[f'F{r}'].number_format = RS
    return r


def resumo(ws, tots, tot_est):
    titulo(ws, 'RESUMO · FEE MENSAL FIXO', 'Havaianas · BID Fase 2 · 75 LAB. Zero honorários, zero agenciamento, zero comissão.')
    cab(ws, 4, ['Frente', 'Posições', 'Pessoas em tempo integral', 'Horas/mês', 'Fee mensal (R$)'], [30, 11, 16, 12, 20])
    for i, ((nome, _), t) in enumerate(zip(FRENTES, tots)):
        r = 5 + i
        aba = f"'Frente {nome}'"
        cel(ws, f'A{r}', nome)
        cel(ws, f'B{r}', f'={aba}!B{t}', F_LINK, '0', 'center')
        cel(ws, f'C{r}', f'={aba}!C{t}', F_LINK, '0.00', 'center')
        cel(ws, f'D{r}', f'={aba}!D{t}', F_LINK, '#,##0', 'center')
        cel(ws, f'E{r}', f'={aba}!F{t}', F_LINK, RS, 'right')
    for c in 'ABCDE':
        cel(ws, f'{c}8', None, F_TOT, fill=CREME)
    ws['A8'] = 'TOTAL (15 posições, sem contar ninguém duas vezes)'
    ws['B8'] = f'=Estrutura!C{tot_est}'
    ws['C8'] = '=SUM(C5:C7)'
    ws['C8'].number_format = '0.00'
    ws['D8'] = '=SUM(D5:D7)'
    ws['D8'].number_format = '#,##0'
    ws['E8'] = '=SUM(E5:E7)'
    ws['E8'].number_format = RS
    cel(ws, 'A10', 'Fee em 12 meses (R$)')
    cel(ws, 'E10', '=E8*12', fmt=RS, al='right')
    cel(ws, 'A11', 'Hora-equipe efetiva (R$)')
    cel(ws, 'E11', '=IFERROR(E8/D8,0)', fmt=RS, al='right')
    cel(ws, 'A12', 'Conferência: fee mensal do documento base (R$)')
    cel(ws, 'E12', 226620.78, F_ENT, RS, 'right', AMARELO)
    cel(ws, 'A13', 'Diferença entre a planilha e o documento (R$)')
    cel(ws, 'E13', '=E8-E12', fmt=RS, al='right')
    for i, n in enumerate([
        'O valor é igual todos os meses, independentemente do volume de campanhas do mês.',
        'Fora do fee: aba Custos adicionais, sempre com três cotações e pagos pela Alpargatas direto ao fornecedor.',
        'Estes valores vão só no open cost do COUPA. A apresentação não mostra custos.',
    ]):
        ws[f'A{15 + i}'], ws[f'A{15 + i}'].font = n, F_SUB


def adicionais(ws):
    titulo(ws, 'CUSTOS ADICIONAIS · FORA DO FEE', 'Documento base · Fase 2, seção 4. Sem honorário, agenciamento ou comissão da 75 LAB.')
    cab(ws, 4, ['Item', 'Como é pago', 'Observação'], [52, 40, 90])
    for i, (a, b, c) in enumerate(CUSTOS_ADIC):
        r = 5 + i
        fill = LISTRA if i % 2 else None
        cel(ws, f'A{r}', a, fill=fill)
        cel(ws, f'B{r}', b, fill=fill)
        cel(ws, f'C{r}', c, F_NOTA, fill=fill, wrap=True)
    ws['A15'] = ('Dentro do fee: estratégia de canal, direção de arte, desdobramento, engenharia, arte-final, 3D, concorrência e '
                 'equalização, acompanhamento de produção, logística e implementação, atendimento à rede, conformidade fiscal '
                 'e toda a tecnologia de rastreio (sistema, plataforma de ativos, painel, códigos e integração com a base de lojas).')
    ws['A15'].font = F_SUB
    ws['A15'].alignment = Alignment(wrap_text=True, vertical='top')
    ws.merge_cells('A15:C17')


def main(saida):
    wb = openpyxl.Workbook()
    ws_res = wb.active
    ws_res.title = 'Resumo'
    ini, fim, tot_est = estrutura(wb.create_sheet('Estrutura'))
    tots = [frente(wb.create_sheet(f'Frente {n}'), n, j, ini, fim) for n, j in FRENTES]
    premissas(wb.create_sheet('Premissas'))
    tributos(wb.create_sheet('Tributos'))
    adicionais(wb.create_sheet('Custos adicionais'))
    resumo(ws_res, tots, tot_est)
    # conferência com o documento: 15 posições, 15 FTE, frentes 3,90 / 4,44 / 6,66
    assert len(POSICOES) == 15 and all(sum(d) == 100 for _, _, d, _ in POSICOES)
    assert [round(sum(d[j] for _, _, d, _ in POSICOES) / 100, 2) for j in range(3)] == [3.9, 4.44, 6.66]
    wb.calculation.fullCalcOnLoad = True
    wb.save(saida)
    print('ok', saida)


if __name__ == '__main__':
    main(sys.argv[1])
