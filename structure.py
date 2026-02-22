import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import requests
import database

database.criar_tabelas()



#-----------------------------------------------------------------------------------------------------------------------------------------
# INTERFACE
#-----------------------------------------------------------------------------------------------------------------------------------------

# JANELA PRINCIPAL
janela = tk.Tk()
largura = janela.winfo_screenwidth()
altura = janela.winfo_screenheight()
janela.geometry(f"{largura}x{altura}+0+0")

# FUNÇÃO JANELA DE CADASTRO - EMPRESAS
def abrir_cadastro_empresas():
    janela_cadastro_empresas = tk.Toplevel(janela)
    janela_cadastro_empresas.title("Cadastro de Empresas")
    janela_cadastro_empresas.geometry("800x700")

    labels_form = {
        "cnpj": "CNPJ",
        "nome": "Razão Social",
        "fantasia": "Nome Fantasia",
        "tipo": "Tipo",
        "porte": "Porte",
        "abertura": "Data de Abertura",
        "natureza_juridica": "Natureza Jurídica",
        "capital_social": "Capital Social",
        "situacao": "Situação",
        "telefone": "Telefone",
        "email": "E-mail",
        "logradouro": "Logradouro",
        "numero": "Número",
        "complemento": "Complemento",
        "bairro": "Bairro",
        "municipio": "Município",
        "uf": "UF",
        "cep": "CEP",
        "inscricao_estadual": "Inscrição Estadual",
        "inscricao_municipal": "Inscrição Municipal"
    }
    

    def salvar_dados_empresa():


        dados = (
            entries["cnpj"].get(),
            entries["nome"].get(),
            entries["fantasia"].get(),
            entries["tipo"].get(),
            entries["porte"].get(),
            entries["abertura"].get(),
            entries["natureza_juridica"].get(),
            entries["capital_social"].get(),
            entries["situacao"].get(),
            entries["telefone"].get(),
            entries["email"].get(),
            entries["logradouro"].get(),
            entries["numero"].get(),
            entries["complemento"].get(),
            entries["bairro"].get(),
            entries["municipio"].get(),
            entries["uf"].get(),
            entries["cep"].get(),
            int(simples_var.get()),
            int(simei_var.get()),
            int(desoneracao_var.get()),
            entries["inscricao_estadual"].get(),
            entries["inscricao_municipal"].get()
        )

        database.salvar_empresa(dados)

        if hasattr(janela_cadastro_empresas, "dados_api"):
            database.salvar_cnae(
                entries["cnpj"].get(),
                janela_cadastro_empresas.dados_api.get("atividade_principal", []) +
                janela_cadastro_empresas.dados_api.get("atividades_secundarias", [])
            )

            database.salvar_qsa(
                entries["cnpj"].get(),
                janela_cadastro_empresas.dados_api.get("qsa", [])
            )

        messagebox.showinfo("Sucesso", "Empresa salva com sucesso")

        for entry in entries.values():
            entry.delete(0, tk.END)

        simples_var.set(False)
        simei_var.set(False)
        desoneracao_var.set(False)

        tree_cnae.delete(*tree_cnae.get_children())
        tree_qsa.delete(*tree_qsa.get_children())
        

    notebook = ttk.Notebook(janela_cadastro_empresas)
    notebook.pack(fill="both", expand=True)

    # ================= DADOS GERAIS =================
    frame_cadastro_empresas = tk.Frame(notebook)
    notebook.add(frame_cadastro_empresas, text="Dados gerais")

    campos_gerais = [
        "cnpj","nome","fantasia","tipo","porte","abertura",
        "natureza_juridica","capital_social","situacao"
    ]

    entries = {}

    for campo in campos_gerais:
        tk.Label(frame_cadastro_empresas, text=labels_form.get(campo, campo)).pack(anchor="w", padx=10)
        e = tk.Entry(frame_cadastro_empresas)
        e.pack(fill="x", padx=10, pady=2)
        entries[campo] = e

    entry_CNPJ = entries["cnpj"]

    

    # ================= ENDEREÇO =================
    frame_end = tk.Frame(notebook)
    notebook.add(frame_end, text="Endereço")

    campos_end = ["logradouro","numero","complemento","bairro","municipio","uf","cep"]

    for campo in campos_end:
        tk.Label(frame_end,  text=labels_form.get(campo, campo)).pack(anchor="w", padx=10)
        e = tk.Entry(frame_end)
        e.pack(fill="x", padx=10, pady=2)
        entries[campo] = e

    # ================= CONTATO =================
    frame_contato = tk.Frame(notebook)
    notebook.add(frame_contato, text="Contato")

    for campo in ["telefone","email"]:
        tk.Label(frame_contato,  text=labels_form.get(campo, campo)).pack(anchor="w", padx=10)
        e = tk.Entry(frame_contato)
        e.pack(fill="x", padx=10, pady=2)
        entries[campo] = e

    # ================= FISCAL =================
    frame_fiscal = tk.Frame(notebook)
    notebook.add(frame_fiscal, text="Fiscal")

    simples_var = tk.BooleanVar()
    simei_var = tk.BooleanVar()
    desoneracao_var = tk.BooleanVar()

    tk.Checkbutton(frame_fiscal, text="Optante Simples", variable=simples_var).pack(anchor="w", padx=10)
    tk.Checkbutton(frame_fiscal, text="Optante MEI", variable=simei_var).pack(anchor="w", padx=10)
    tk.Checkbutton(frame_fiscal, text="Desoneração da Folha", variable=desoneracao_var).pack(anchor="w", padx=10)

    tk.Label(frame_fiscal, text="Inscrição Estadual").pack(anchor="w", padx=10)
    entry_ie = tk.Entry(frame_fiscal)
    entry_ie.pack(fill="x", padx=10)
    entries["inscricao_estadual"] = entry_ie
    
    tk.Label(frame_fiscal, text="Inscrição Municipal").pack(anchor="w", padx=10)
    entry_im = tk.Entry(frame_fiscal)
    entry_im.pack(fill="x", padx=10)
    entries["inscricao_municipal"] = entry_im

    # ================= CNAE =================
    frame_cnae = tk.Frame(notebook)
    notebook.add(frame_cnae, text="CNAE")

    tree_cnae = ttk.Treeview(frame_cnae, columns=("codigo","descricao"), show="headings")
    tree_cnae.heading("codigo", text="Código")
    tree_cnae.heading("descricao", text="Descrição")
    tree_cnae.pack(fill="both", expand=True)

    # ================= QSA =================
    frame_qsa = tk.Frame(notebook)
    notebook.add(frame_qsa, text="Sócios")

    tree_qsa = ttk.Treeview(frame_qsa, columns=("nome","qual"), show="headings")
    tree_qsa.heading("nome", text="Nome")
    tree_qsa.heading("qual", text="Qualificação")
    tree_qsa.pack(fill="both", expand=True)

    # ================= BUSCAR API =================
    def buscar():
        cnpj = entry_CNPJ.get().replace(".","").replace("/","").replace("-","")

        try:
            dados = requests.get(f"https://www.receitaws.com.br/v1/cnpj/{cnpj}").json()

            if dados.get("status") == "ERROR":
                messagebox.showerror("Erro", dados.get("message"))
                return

            janela_cadastro_empresas.dados_api = dados

            for campo, entry in entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, dados.get(campo,""))

            simples_var.set(dados.get("simples",{}).get("optante",False))
            simei_var.set(dados.get("simei",{}).get("optante",False))

            tree_cnae.delete(*tree_cnae.get_children())
            for a in dados.get("atividade_principal",[]):
                tree_cnae.insert("",tk.END,values=(a["code"],a["text"]))
            for a in dados.get("atividades_secundarias",[]):
                tree_cnae.insert("",tk.END,values=(a["code"],a["text"]))

            tree_qsa.delete(*tree_qsa.get_children())
            for s in dados.get("qsa",[]):
                tree_qsa.insert("",tk.END,values=(s["nome"],s["qual"]))

        except Exception as e:
            messagebox.showerror("Erro", str(e))

    tk.Button(frame_cadastro_empresas, text="Buscar CNPJ", command=buscar).pack(pady=10)
    tk.Button(frame_cadastro_empresas, text="Salvar CNPJ", command=salvar_dados_empresa).pack(pady=10)

    janela_cadastro_empresas.grab_set()


# MENU DE AÇÕES
barra_menu_acoes = tk.Menu(janela)

# MENU DE AÇÕES - CADASTROS
menu_cadastro = tk.Menu(barra_menu_acoes, tearoff=0)
menu_cadastro.add_command(label="Atividades")
menu_cadastro.add_command(label="Empresas", command=abrir_cadastro_empresas)
menu_cadastro.add_command(label="Usuários")
barra_menu_acoes.add_cascade(label="Cadastros", menu=menu_cadastro)
janela.config(menu=barra_menu_acoes)

# FRAME RODAPÉ (BAIXO)
fbot = tk.Frame(janela, bg="#2c3e50", height=altura*0.0250)
fbot.pack(side="bottom", fill="x")
fbot.pack_propagate(False)

# FRAME MENU DE NAVEGAÇÃO (ESQUERDA)
fleft = tk.Frame(janela, bg="#34495e", width=largura*0.1)
fleft.pack(side="left", fill="y")
fleft.pack_propagate(False)

# FRAME EXIBIÇÃO DE CONTEÚDO (CENTRO E DIREITA)
fcontent = tk.Frame(janela, bg="#ecf0f1", width=largura*0.2)
fcontent.pack(side="right", expand=True, fill="both")
fcontent.pack_propagate(False)


# FIM JANELA PRINCIPAL
janela.mainloop()
