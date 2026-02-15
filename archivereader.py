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


def extrair_cnpj_14_digitos(texto):

    # 🔹 1) Primeiro tenta pegar CNPJ formatado
    match_formatado = re.search(r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}", texto)
    if match_formatado:
        return re.sub(r"\D", "", match_formatado.group(0))

    # 🔹 2) Se não achar, tenta pegar 14 dígitos consecutivos
    match_seco = re.search(r"\b\d{14}\b", texto)
    if match_seco:
        return match_seco.group(0)

    # 🔹 3) Última tentativa (caso venha com espaços estranhos)
    numeros = re.findall(r"\d+", texto)
    for n in numeros:
        if len(n) == 14:
            return n

    raise Exception("CNPJ não encontrado no documento.")


def validar_competencia(data_inicial, data_final):
    dt_inicio = datetime.strptime(data_inicial, "%d/%m/%Y")
    dt_fim = datetime.strptime(data_final, "%d/%m/%Y")
    ultimo_dia = calendar.monthrange(dt_inicio.year, dt_inicio.month)[1]
    return dt_inicio.day == 1 and dt_fim.day == ultimo_dia


def extrair_datas_tabela(texto):
    padrao = re.compile(
        r"^\s*\d+\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})\s+(\d{2}/\d{2}/\d{4})",
        re.MULTILINE
    )

    match = padrao.search(texto)
    if not match:
        raise Exception("Linha de datas não encontrada.")

    return match.group(1), match.group(2), match.group(3)


def extrair_competencia_por_extenso(texto):

    padrao = re.search(
        r"Declaramos que no mês de\s+([A-Za-zçÇãÃéÉêÊíÍóÓôÔúÚ]+)\s+de\s+(\d{4})",
        texto,
        re.IGNORECASE
    )

    if not padrao:
        raise Exception("Competência por extenso não encontrada.")

    mes_texto = padrao.group(1).lower()
    ano = padrao.group(2)

    meses = {
        "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3,
        "abril": 4, "maio": 5, "junho": 6,
        "julho": 7, "agosto": 8, "setembro": 9,
        "outubro": 10, "novembro": 11, "dezembro": 12
    }

    mes_num = meses.get(mes_texto)
    if not mes_num:
        raise Exception(f"Mês inválido detectado: {mes_texto}")

    data_inicial = datetime(int(ano), mes_num, 1)
    ultimo_dia = calendar.monthrange(int(ano), mes_num)[1]
    data_final = datetime(int(ano), mes_num, ultimo_dia)

    return data_inicial.strftime("%d/%m/%Y"), data_final.strftime("%d/%m/%Y")


def validar_total_geral(texto):

    linhas = texto.split("\n")

    for linha in linhas:
        if "Total Geral:" in linha:

            # Se não tiver nenhum valor monetário na linha
            if "R$" not in linha:
                return False

            # Se tiver R$, verifica se todos são 0,00
            valores = re.findall(r"R\$\s*([\d\.,]+)", linha)

            if not valores:
                return False

            todos_zero = all(
                v.replace(".", "").replace(",", "") == "000"
                for v in valores
            )

            if todos_zero:
                return False

            return True

    # Se não encontrou linha Total Geral, não bloqueia
    return True



def montar_estrutura_e_salvar(caminho_pdf, dados):

    dt = datetime.strptime(dados["data_inicial"], "%d/%m/%Y")

    ano = dt.strftime("%Y")
    mes = dt.strftime("%m%y")

    caminho_final = os.path.join(
        os.getcwd(),
        dados["cnpj"],
        ano,
        mes,
        dados["departamento"],
        dados["esfera"]
    )

    os.makedirs(caminho_final, exist_ok=True)

    nome_arquivo = f"{dados['cnpj']} - {dados['nome_obrigacao']} {mes}.pdf"
    destino = os.path.join(caminho_final, nome_arquivo)

    if os.path.exists(destino):
        messagebox.showwarning("Atenção", "Já existe arquivo para essa competência.")
        return

    shutil.copy2(caminho_pdf, destino)
    messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{destino}")


# ======================================================
# 🔹 REST GOIÂNIA
# ======================================================

def detector_rest_goiania(texto):
    return "serviços contratados" in texto.lower() and "declaração de não movimentação" not in texto.lower()


def extrator_rest_goiania(texto):

    if not validar_total_geral(texto):
        messagebox.showwarning(
            "Sem Movimento Detectado",
            "Total Geral zerado.\nEnvie a REST Negativa."
        )
        return None

    linhas = texto.split("\n")

    linha_cnpj = next((l for l in linhas if "Municipal C" in l), None)
    if not linha_cnpj:
        raise Exception("Linha do CNPJ não encontrada.")

    cnpj = limpar_numeros(linha_cnpj)[-14:]

    data_inicial, data_final, data_geracao = extrair_datas_tabela(texto)

    return {
        "cnpj": cnpj,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "departamento": "Fiscal",
        "esfera": "Municipal",
        "nome_obrigacao": "REST"
    }


# ======================================================
# 🔹 DMS GOIÂNIA
# ======================================================

def detector_dms_goiania(texto):
    return "serviços prestados" in texto.lower() and "declaração de não movimentação" not in texto.lower()


def extrator_dms_goiania(texto):

    if not validar_total_geral(texto):
        messagebox.showwarning(
            "Sem Movimento Detectado",
            "Total Geral zerado.\nEnvie a DMS Negativa."
        )
        return None

    cnpj = extrair_cnpj_14_digitos(texto)
    data_inicial, data_final, data_geracao = extrair_datas_tabela(texto)

    return {
        "cnpj": cnpj,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "departamento": "Fiscal",
        "esfera": "Municipal",
        "nome_obrigacao": "DMS"
    }


# ======================================================
# 🔹 REST NEGATIVA
# ======================================================

def detector_rest_negativa_goiania(texto):
    return "declaração de não movimentação" in texto.lower() and "serviços contratados" in texto.lower()


def extrator_rest_negativa_goiania(texto):

    cnpj = extrair_cnpj_14_digitos(texto)
    data_inicial, data_final = extrair_competencia_por_extenso(texto)

    return {
        "cnpj": cnpj,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "departamento": "Fiscal",
        "esfera": "Municipal",
        "nome_obrigacao": "REST Negativa"
    }


# ======================================================
# 🔹 DMS NEGATIVA
# ======================================================

def detector_dms_negativa_goiania(texto):
    return "declaração de não movimentação" in texto.lower() and "serviços prestados" in texto.lower()


def extrator_dms_negativa_goiania(texto):

    cnpj = extrair_cnpj_14_digitos(texto)
    data_inicial, data_final = extrair_competencia_por_extenso(texto)

    return {
        "cnpj": cnpj,
        "data_inicial": data_inicial,
        "data_final": data_final,
        "departamento": "Fiscal",
        "esfera": "Municipal",
        "nome_obrigacao": "DMS Negativa"
    }


# ======================================================
# 🔹 REGISTRO
# ======================================================

registrar_padrao("REST", detector_rest_goiania, extrator_rest_goiania)
registrar_padrao("DMS", detector_dms_goiania, extrator_dms_goiania)
registrar_padrao("REST_NEGATIVA", detector_rest_negativa_goiania, extrator_rest_negativa_goiania)
registrar_padrao("DMS_NEGATIVA", detector_dms_negativa_goiania, extrator_dms_negativa_goiania)


# ======================================================
# 🔹 MOTOR
# ======================================================

def processar_pdf(caminho_pdf):

    with pdfplumber.open(caminho_pdf) as pdf:
        texto = pdf.pages[0].extract_text()

    for nome, config in PADROES.items():
        if config["detector"](texto):
            dados = config["extrator"](texto)
            if dados:
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
