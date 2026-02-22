import sqlite3

# ================= CONEXÃO =================

conn = sqlite3.connect("ultimate_account.db")
cursor = conn.cursor()


# ================= CRIAR TABELAS =================

def criar_tabelas():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empresas (
        cnpj TEXT PRIMARY KEY,
        nome TEXT,
        fantasia TEXT,
        tipo TEXT,
        porte TEXT,
        abertura TEXT,
        natureza_juridica TEXT,
        capital_social TEXT,
        situacao TEXT,
        telefone TEXT,
        email TEXT,
        logradouro TEXT,
        numero TEXT,
        complemento TEXT,
        bairro TEXT,
        municipio TEXT,
        uf TEXT,
        cep TEXT,
        simples INTEGER,
        simei INTEGER,
        desoneracao INTEGER,
        inscricao_estadual TEXT,
        inscricao_municipal TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cnae (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cnpj TEXT,
        codigo TEXT,
        descricao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qsa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cnpj TEXT,
        nome TEXT,
        qualificacao TEXT
    )
    """)

    conn.commit()


# ================= SALVAR EMPRESA =================

def salvar_empresa(dados):
    cursor.execute("""
        INSERT OR REPLACE INTO empresas VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, dados)
    conn.commit()


# ================= SALVAR CNAE =================

def salvar_cnae(cnpj, lista_cnae):
    cursor.execute("DELETE FROM cnae WHERE cnpj = ?", (cnpj,))

    for c in lista_cnae:
        cursor.execute(
            "INSERT INTO cnae (cnpj, codigo, descricao) VALUES (?,?,?)",
            (cnpj, c["code"], c["text"])
        )

    conn.commit()


# ================= SALVAR QSA =================

def salvar_qsa(cnpj, lista_qsa):
    cursor.execute("DELETE FROM qsa WHERE cnpj = ?", (cnpj,))

    for s in lista_qsa:
        cursor.execute(
            "INSERT INTO qsa (cnpj, nome, qualificacao) VALUES (?,?,?)",
            (cnpj, s["nome"], s["qual"])
        )

    conn.commit()


# ================= BUSCAR EMPRESAS =================

def listar_empresas():
    cursor.execute("SELECT cnpj, nome, fantasia, municipio, uf FROM empresas")
    return cursor.fetchall()


# ================= EXCLUIR EMPRESA =================

def excluir_empresa(cnpj):
    cursor.execute("DELETE FROM empresas WHERE cnpj = ?", (cnpj,))
    cursor.execute("DELETE FROM cnae WHERE cnpj = ?", (cnpj,))
    cursor.execute("DELETE FROM qsa WHERE cnpj = ?", (cnpj,))
    conn.commit()