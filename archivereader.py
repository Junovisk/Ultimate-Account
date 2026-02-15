import pdfplumber
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import re
from datetime import datetime
import calendar


# ======================================================
# 🔹 REGISTRO DE PADRÕES (PLUGÁVEL)
# ======================================================

PADROES = {}


def registrar_padrao(nome, detector, extrator):
    PADROES[nome] = {
        "detector": detector,
        "extrator": extrator
    }


# ======================================================
# 🔹 UTILITÁRIOS
# ======================================================

def limpar_numeros(texto):
    return re.sub(r"\D", "", texto)


def validar_competencia(data_inicial, data_final):
    dt_inicio = datetime.strptime(data_inicial, "%d/%m/%Y")
    dt_fim = datetime.strptime(data_final, "%d/%m/%Y")

    ultimo_dia = calendar.monthrange(dt_inicio.year, dt_inicio.month)[1]

    return dt_inicio.day == 1 and dt_fim.day == ultimo_dia


def montar_estrutura_e_salvar(caminho_pdf, dados):

    dt = datetime.strptime(dados["data_inicial"], "%d/%m/%Y")

    ano = dt.strftime("%Y")
    mes = dt.strftime("%m%y")

    pasta_base = os.getcwd()

    caminho_final = os.path.join(
        pasta_base,
        dados["cnpj"],   # CNPJ
        ano,             # Ano
        mes,             # Mês
        dados["departamento"],  # Fiscal / Contábil / DP
        dados["esfera"]         # Municipal / Estadual / Federal
    )

    os.makedirs(caminho_final, exist_ok=True)

    nome_arquivo = f"{dados['cnpj']} - {dados['nome_obrigacao']} {mes} {dados['valor']}.pdf"
    destino = os.path.join(caminho_final, nome_arquivo)

    if os.path.exists(destino):
        messagebox.showwarning(
            "Atenção",
            "Já existe um arquivo com esse nome.\nPossível divergência."
        )
        return

    shutil.copy2(caminho_pdf, destino)

    messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{destino}")



# ======================================================
# 🔹 REST GOIÂNIA (PRIMEIRO PADRÃO)
# ======================================================

def detector_rest_goiania(texto):
    primeira_linha = texto.split("\n")[0]
    return "Prefeitura Municipal de Goiânia - GO Serviços Contratados" in primeira_linha


def extrair_datas_rest(texto):

    linhas = texto.split("\n")

    padrao_linha_datas = re.compile(
        r"^\s*\d+\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})"
    )

    for linha in linhas:
        match = padrao_linha_datas.search(linha)
        if match:
            data_inicial = match.group(1)
            data_final = match.group(2)
            data_geracao = match.group(3)
            return data_inicial, data_final, data_geracao

    raise Exception("Linha de datas não encontrada.")

def extrator_rest_goiania(texto):

    linhas = texto.split("\n")

    # 🔹 CNPJ – procurar linha que contenha "Municipal C"
    linha_cnpj = None
    for linha in linhas:
        if "Municipal C" in linha:
            linha_cnpj = linha
            break

    if not linha_cnpj:
        raise Exception("Linha do CNPJ não encontrada.")

    numeros = limpar_numeros(linha_cnpj)
    cnpj = numeros[-14:]


    # 🔹 Valor do imposto – procurar linha que contenha "R$"
    linha_valor = None
    for linha in linhas:
        if "R$" in linha:
            linha_valor = linha
            break

    if not linha_valor:
        raise Exception("Linha do valor não encontrada.")

    valor_match = re.search(r"R\$\s*([\d\.,]+)", linha_valor)
    valor = valor_match.group(1) if valor_match else None

    data_inicial, data_final, data_geracao = extrair_datas_rest(texto)

    competencia_ok = validar_competencia(data_inicial, data_final)

    if not competencia_ok:
        messagebox.showwarning(
            "Competência divergente",
            "Datas não correspondem ao mês completo."
        )

    return {
        "cnpj": cnpj,
        "valor": valor,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "data_geracao": data_geracao,
        "departamento": "Fiscal",
        "esfera": "Municipal",
        "nome_obrigacao": "REST"
    }




registrar_padrao("REST_GOIANIA", detector_rest_goiania, extrator_rest_goiania)


# ======================================================
# 🔹 MOTOR PRINCIPAL
# ======================================================

def processar_pdf(caminho_pdf):

    with pdfplumber.open(caminho_pdf) as pdf:
        texto = pdf.pages[0].extract_text()

    for nome, config in PADROES.items():
        if config["detector"](texto):
            dados = config["extrator"](texto)
            montar_estrutura_e_salvar(caminho_pdf, dados)
            return

    messagebox.showerror("Erro", "Nenhum padrão identificado.")


# ======================================================
# 🔹 INTERFACE
# ======================================================

def carregar_arquivo():
    caminho = filedialog.askopenfilename(
        title="Selecione um PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )

    if caminho:
        processar_pdf(caminho)


janela = tk.Tk()
janela.title("Controle Fiscal Inteligente")
janela.geometry("500x200")

botao = tk.Button(
    janela,
    text="Carregar Arquivo",
    command=carregar_arquivo,
    height=2,
    width=25
)

botao.pack(pady=40)

janela.mainloop()
