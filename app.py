import streamlit as st
import sqlite3
import matplotlib.pyplot as plt

# =============================
# CONFIG
# =============================
st.set_page_config(page_title="Controle Financeiro", layout="wide")
st.title("💰 Controle Financeiro")

# =============================
# DB
# =============================
conn = sqlite3.connect("financeiro.db", check_same_thread=False)
cursor = conn.cursor()

# =============================
# FUNÇÃO MIGRAÇÃO
# =============================
def coluna_existe(tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    return coluna in [c[1] for c in cursor.fetchall()]

# =============================
# TABELAS
# =============================
cursor.execute("""
CREATE TABLE IF NOT EXISTS meses (
    mes TEXT PRIMARY KEY,
    ano INTEGER,
    inicializado INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS receitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mes TEXT,
    mes_ref TEXT,
    pessoa TEXT,
    tipo TEXT,
    descricao TEXT,
    valor REAL,
    fixa INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS despesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mes TEXT,
    mes_ref TEXT,
    categoria TEXT,
    descricao TEXT,
    valor REAL,
    fixa INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS dividas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    valor_total REAL,
    parcelas INTEGER,
    mes_inicio TEXT,
    ano_inicio INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS metas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    valor_total REAL,
    prazo_meses INTEGER,
    valor_guardado REAL DEFAULT 0,
    data_inicio TEXT
)
""")

conn.commit()

# =============================
# MESES / ANO
# =============================
MESES = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
         "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

st.sidebar.title("📅 Período")
ano_atual = st.sidebar.selectbox("Ano", list(range(2025, 2035)))
mes_atual = st.sidebar.selectbox("Mês", MESES)

mes_ref = f"{mes_atual}-{ano_atual}"
idx_mes_atual = MESES.index(mes_atual)

# =============================
# INICIAR MÊS
# =============================
cursor.execute("SELECT 1 FROM meses WHERE mes=?", (mes_ref,))
mes_iniciado = cursor.fetchone()

if not mes_iniciado:
    st.warning(f"Mês {mes_ref} não iniciado")
    with st.form("start_month"):
        repetir_r = st.checkbox("Repetir receitas fixas")
        repetir_d = st.checkbox("Repetir despesas fixas")
        start = st.form_submit_button("Iniciar mês")

        if start:
            cursor.execute("INSERT OR IGNORE INTO meses (mes,ano,inicializado) VALUES (?,?,1)",
                           (mes_ref, ano_atual))

            # EVITAR DUPLICAÇÃO
            if repetir_r:
                cursor.execute("SELECT pessoa,tipo,descricao,valor FROM receitas WHERE fixa=1 GROUP BY pessoa,tipo,descricao,valor")
                for r in cursor.fetchall():
                    cursor.execute("""
                    INSERT INTO receitas (mes,mes_ref,pessoa,tipo,descricao,valor,fixa)
                    VALUES (?,?,?,?,?,?,1)
                    """, (mes_atual, mes_ref, *r))

            if repetir_d:
                cursor.execute("SELECT categoria,descricao,valor FROM despesas WHERE fixa=1 GROUP BY categoria,descricao,valor")
                for d in cursor.fetchall():
                    cursor.execute("""
                    INSERT INTO despesas (mes,mes_ref,categoria,descricao,valor,fixa)
                    VALUES (?,?,?,?,?,1)
                    """, (mes_atual, mes_ref, *d))

            conn.commit()
            st.rerun()
    st.stop()

# =============================
# ABAS
# =============================
tab_r, tab_d, tab_v, tab_m, tab_res = st.tabs(["💵 Receitas", "💸 Despesas", "📉 Dívidas", "🎯 Metas", "📊 Resumo"])

# =============================
# RECEITAS
# =============================
with tab_r:
    st.subheader("Receitas")

    with st.form("add_r"):
        pessoa = st.selectbox("Pessoa", ["Pessoa 1","Pessoa 2"])
        tipo = st.selectbox("Tipo", ["Salário","Extra"])
        desc = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0)
        fixa = st.checkbox("Fixa")
        save = st.form_submit_button("Salvar")

        if save:
            cursor.execute("""
            INSERT INTO receitas (mes,mes_ref,pessoa,tipo,descricao,valor,fixa)
            VALUES (?,?,?,?,?,?,?)
            """, (mes_atual, mes_ref, pessoa, tipo, desc, valor, int(fixa)))
            conn.commit()
            st.rerun()

    cursor.execute("SELECT id,pessoa,tipo,descricao,valor,fixa FROM receitas WHERE mes_ref=?", (mes_ref,))
    for r in cursor.fetchall():
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.write(r[1]); c2.write(r[2]); c3.write(r[3])
        c4.write(f"R$ {r[4]:,.2f}")
        c5.write("Fixa" if r[5] else "")
        if c6.button("❌", key=f"r{r[0]}"):
            cursor.execute("DELETE FROM receitas WHERE id=?", (r[0],))
            conn.commit()
            st.rerun()

# =============================
# DESPESAS
# =============================
with tab_d:
    st.subheader("Despesas")

    with st.form("add_d"):
        cat = st.selectbox("Categoria", ["Aluguel","Mercado","Luz","Água","Internet","Outros"])
        desc = st.text_input("Descrição")
        valor = st.number_input("Valor", min_value=0.0)
        fixa = st.checkbox("Fixa")
        save = st.form_submit_button("Salvar")

        if save:
            cursor.execute("""
            INSERT INTO despesas (mes,mes_ref,categoria,descricao,valor,fixa)
            VALUES (?,?,?,?,?,?)
            """, (mes_atual, mes_ref, cat, desc, valor, int(fixa)))
            conn.commit()
            st.rerun()

    cursor.execute("SELECT id,categoria,descricao,valor,fixa FROM despesas WHERE mes_ref=?", (mes_ref,))
    for d in cursor.fetchall():
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.write(d[1]); c2.write(d[2])
        c3.write(f"R$ {d[3]:,.2f}")
        c4.write("Fixa" if d[4] else "")
        if c5.button("❌", key=f"d{d[0]}"):
            cursor.execute("DELETE FROM despesas WHERE id=?", (d[0],))
            conn.commit()
            st.rerun()

# =============================
# DÍVIDAS
# =============================
with tab_v:
    st.subheader("Dívidas")

    with st.form("add_v"):
        nome = st.text_input("Nome")
        total = st.number_input("Valor total", min_value=0.0)
        parcelas = st.number_input("Parcelas", min_value=1, step=1)
        save = st.form_submit_button("Salvar")

        if save:
            cursor.execute("""
            INSERT INTO dividas (nome,valor_total,parcelas,mes_inicio,ano_inicio)
            VALUES (?,?,?,?,?)
            """, (nome, total, parcelas, mes_atual, ano_atual))
            conn.commit()
            st.rerun()

    cursor.execute("SELECT * FROM dividas")
    for d in cursor.fetchall():
        _, nome, total, parc, mes_i, ano_i = d

        if ano_i is None: ano_i = ano_atual
        if mes_i not in MESES: mes_i = mes_atual

        idx_i = MESES.index(mes_i)
        idx_a = MESES.index(mes_atual)
        meses_passados = (ano_atual - ano_i) * 12 + (idx_a - idx_i)

        restantes = max(0, parc - meses_passados)
        valor_parcela = total / parc if parc else 0
        restante_total = restantes * valor_parcela

        progresso = min(1, meses_passados / parc if parc else 0)
        st.progress(progresso)

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.write(nome)
        c2.write(f"Parcela: {min(meses_passados+1, parc)}/{parc}")
        c3.write(f"Valor parcela: R$ {valor_parcela:,.2f}")
        c4.write(f"Restante: R$ {restante_total:,.2f}")

        if c5.button("❌", key=f"v{d[0]}"):
            cursor.execute("DELETE FROM dividas WHERE id=?", (d[0],))
            conn.commit()
            st.rerun()

        if restantes <= 0:
            cursor.execute("DELETE FROM dividas WHERE id=?", (d[0],))
            conn.commit()
            st.rerun()

# =============================
# METAS
# =============================
with tab_m:
    st.subheader("🎯 Metas")

    nome_meta = st.text_input("Nome da Meta")
    valor_meta = st.number_input("Valor total da meta", min_value=0.0)
    prazo = st.number_input("Prazo (meses)", min_value=1)

    if st.button("Adicionar Meta"):
        cursor.execute("""
        INSERT INTO metas (nome,valor_total,prazo_meses,data_inicio)
        VALUES (?,?,?,date('now'))
        """, (nome_meta, valor_meta, prazo))
        conn.commit()
        st.rerun()

    st.subheader("📌 Suas Metas")
    cursor.execute("SELECT id,nome,valor_total,prazo_meses,valor_guardado FROM metas")
    for m in cursor.fetchall():
        id_m, nome, total, prazo, guardado = m
        progresso = guardado / total if total else 0

        st.markdown(f"### {nome}")
        st.progress(min(progresso,1.0))
        st.write(f"Total: R$ {total:.2f}")
        st.write(f"Guardado: R$ {guardado:.2f}")

        valor_add = st.number_input(f"Adicionar valor guardado ({nome})", min_value=0.0, key=f"g{id_m}")

        if st.button(f"Salvar valor ({nome})", key=f"b{id_m}"):
            cursor.execute("UPDATE metas SET valor_guardado = valor_guardado + ? WHERE id=?",
                           (valor_add, id_m))
            conn.commit()
            st.rerun()

# =============================
# RESUMO
# =============================
with tab_res:
    st.subheader("📊 Resumo Mensal")

    cursor.execute("SELECT COALESCE(SUM(valor),0) FROM receitas WHERE mes_ref=?", (mes_ref,))
    total_r = float(cursor.fetchone()[0] or 0.0)
    cursor.execute("SELECT COALESCE(SUM(valor),0) FROM despesas WHERE mes_ref=?", (mes_ref,))
    total_d = float(cursor.fetchone()[0] or 0.0)
    cursor.execute("SELECT SUM(valor_total/parcelas) FROM dividas")
    total_v = float(cursor.fetchone()[0] or 0.0)
    saldo = total_r - total_d - total_v

    c1, c2 = st.columns([1,2])
    with c1:
        st.metric("Receitas", f"R$ {total_r:,.2f}")
        st.metric("Despesas", f"R$ {total_d:,.2f}")
        st.metric("Dívidas (mês)", f"R$ {total_v:,.2f}")
        st.metric("Saldo", f"R$ {saldo:,.2f}")

        if saldo < 0:
            st.error("⚠️ Atenção! Saldo negativo este mês!")

    with c2:
        labels = ["Receitas","Despesas","Dívidas"]
        valores = [total_r, total_d, total_v]

        if all(v == 0 for v in valores):
            st.info("Não há dados para mostrar no gráfico de pizza este mês.")
        else:
            plt.figure(figsize=(4,4))
            plt.pie(valores, labels=labels, autopct="%1.1f%%", startangle=90)
            plt.title(f"Evolução Mensal - {mes_ref}")
            st.pyplot(plt.gcf())
            plt.close()
