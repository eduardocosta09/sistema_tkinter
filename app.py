import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import pandas as pd
import os

# ================================
# BANCO DE DADOS
# ================================

con = sqlite3.connect("sistema.db")
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    senha TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    email TEXT,
    telefone TEXT
)
""")
con.commit()


# ================================
# CRIAR ADMIN AUTOMATICAMENTE
# ================================

def criar_admin():
    cur.execute("SELECT usuario FROM usuarios WHERE usuario='admin'")
    if cur.fetchone() is None:
        cur.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ("admin", "123"))
        con.commit()

criar_admin()


# ================================
# FUNÇÕES CRUD
# ================================

def adicionar_cliente(nome, email, telefone, tree):
    cur.execute("INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)", (nome, email, telefone))
    con.commit()
    carregar_clientes(tree)

def atualizar_cliente(id_cliente, nome, email, telefone, tree):
    cur.execute("UPDATE clientes SET nome=?, email=?, telefone=? WHERE id=?", (nome, email, telefone, id_cliente))
    con.commit()
    carregar_clientes(tree)

def deletar_cliente(id_cliente, tree):
    cur.execute("DELETE FROM clientes WHERE id=?", (id_cliente,))
    con.commit()
    carregar_clientes(tree)

def carregar_clientes(tree):
    for row in tree.get_children():
        tree.delete(row)

    cur.execute("SELECT * FROM clientes")
    for cliente in cur.fetchall():
        tree.insert("", tk.END, values=cliente)


# ================================
# IMPORTAÇÃO DE ARQUIVOS
# ================================

def importar_csv(tree):
    try:
        file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file:
            df = pd.read_csv(file)
            df.to_sql("clientes", con, if_exists="append", index=False)
            carregar_clientes(tree)
            messagebox.showinfo("Sucesso", "CSV importado com sucesso!")
    except:
        messagebox.showerror("Erro", "Arquivo CSV inválido.")

def importar_excel(tree):
    try:
        file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file:
            df = pd.read_excel(file)
            df.to_sql("clientes", con, if_exists="append", index=False)
            carregar_clientes(tree)
            messagebox.showinfo("Sucesso", "Excel importado com sucesso!")
    except:
        messagebox.showerror("Erro", "Arquivo Excel inválido.")

def importar_sql(tree):
    try:
        file = filedialog.askopenfilename(filetypes=[("SQL Files", "*.sql")])
        if file:
            with open(file, "r") as f:
                sql_script = f.read()
                cur.executescript(sql_script)
                con.commit()
            carregar_clientes(tree)
            messagebox.showinfo("Sucesso", "Arquivo SQL importado com sucesso!")
    except:
        messagebox.showerror("Erro", "Erro ao importar SQL.")


# ================================
# EXPORTAÇÃO DE ARQUIVOS
# ================================

def exportar_csv():
    file = filedialog.asksaveasfilename(defaultextension=".csv")
    if file:
        cur.execute("SELECT * FROM clientes")
        rows = cur.fetchall()

        with open(file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "nome", "email", "telefone"])
            writer.writerows(rows)

        messagebox.showinfo("Sucesso", "CSV exportado com sucesso!")

def exportar_sql():
    file = filedialog.asksaveasfilename(defaultextension=".sql")
    if file:
        cur.execute("SELECT * FROM clientes")
        rows = cur.fetchall()

        with open(file, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(f"INSERT INTO clientes (id, nome, email, telefone) VALUES ({r[0]}, '{r[1]}', '{r[2]}', '{r[3]}');\n")

        messagebox.showinfo("Sucesso", "SQL exportado com sucesso!")


# ================================
# INTERFACE TKINTER
# ================================

app = tk.Tk()
app.title("Sistema Tkinter")

# ✔ Janela 1280x720
largura = 1280
altura = 720

# ✔ Centralização
pos_x = (app.winfo_screenwidth() // 2) - (largura // 2)
pos_y = (app.winfo_screenheight() // 2) - (altura // 2)

app.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

# ✔ Permitido redimensionar
app.resizable(True, True)


# ================================
# TELA DE LOGIN
# ================================

def tela_login():
    for widget in app.winfo_children():
        widget.destroy()

    tk.Label(app, text="Login", font=("Arial", 22)).pack(pady=20)

    tk.Label(app, text="Usuário:").pack()
    usuario_entry = tk.Entry(app)
    usuario_entry.pack()

    tk.Label(app, text="Senha:").pack()
    senha_entry = tk.Entry(app, show="*")
    senha_entry.pack()

    def autenticar():
        u = usuario_entry.get()
        s = senha_entry.get()

        cur.execute("SELECT * FROM usuarios WHERE usuario=? AND senha=?", (u, s))
        if cur.fetchone():
            tela_principal()
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    tk.Button(app, text="Entrar", command=autenticar, width=20).pack(pady=20)


# ================================
# TELA PRINCIPAL
# ================================

def tela_principal():
    for widget in app.winfo_children():
        widget.destroy()

    tk.Label(app, text="Sistema de Cadastro", font=("Arial", 22)).pack(pady=20)

    tk.Button(app, text="Cadastrar Clientes", width=30, command=tela_cadastro).pack(pady=10)
    tk.Button(app, text="Ver Clientes", width=30, command=tela_listagem).pack(pady=10)
    tk.Button(app, text="Importar / Exportar Dados", width=30, command=tela_importacao).pack(pady=10)
    tk.Button(app, text="Sair", width=30, command=tela_login).pack(pady=10)


# ================================
# TELA DE CADASTRO
# ================================

def tela_cadastro():
    for widget in app.winfo_children():
        widget.destroy()

    tk.Label(app, text="Cadastrar Cliente", font=("Arial", 20)).pack(pady=20)

    tk.Label(app, text="Nome:").pack()
    nome_entry = tk.Entry(app)
    nome_entry.pack()

    tk.Label(app, text="Email:").pack()
    email_entry = tk.Entry(app)
    email_entry.pack()

    tk.Label(app, text="Telefone:").pack()
    telefone_entry = tk.Entry(app)
    telefone_entry.pack()

    def salvar():
        adicionar_cliente(nome_entry.get(), email_entry.get(), telefone_entry.get(), tree=None)
        messagebox.showinfo("Sucesso", "Cliente cadastrado!")

    tk.Button(app, text="Salvar", command=salvar).pack(pady=10)
    tk.Button(app, text="Voltar", command=tela_principal).pack(pady=10)


# ================================
# TELA LISTAGEM (CRUD)
# ================================

def tela_listagem():
    for widget in app.winfo_children():
        widget.destroy()

    tk.Label(app, text="Clientes Cadastrados", font=("Arial", 20)).pack(pady=20)

    columns = ("id", "nome", "email", "telefone")
    tree = ttk.Treeview(app, columns=columns, show="headings", height=20)
    for col in columns:
        tree.heading(col, text=col.upper())
    tree.pack()

    carregar_clientes(tree)

    def editar():
        selecionado = tree.focus()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente.")
            return

        dados = tree.item(selecionado)["values"]

        edit_win = tk.Toplevel(app)
        edit_win.title("Editar Cliente")
        edit_win.geometry("400x300")

        tk.Label(edit_win, text="Nome").pack()
        nome_e = tk.Entry(edit_win)
        nome_e.insert(0, dados[1])
        nome_e.pack()

        tk.Label(edit_win, text="Email").pack()
        email_e = tk.Entry(edit_win)
        email_e.insert(0, dados[2])
        email_e.pack()

        tk.Label(edit_win, text="Telefone").pack()
        tel_e = tk.Entry(edit_win)
        tel_e.insert(0, dados[3])
        tel_e.pack()

        def salvar():
            atualizar_cliente(dados[0], nome_e.get(), email_e.get(), tel_e.get(), tree)
            edit_win.destroy()

        tk.Button(edit_win, text="Salvar", command=salvar).pack(pady=10)

    def excluir():
        selecionado = tree.focus()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um cliente.")
            return

        dados = tree.item(selecionado)["values"]
        deletar_cliente(dados[0], tree)

    tk.Button(app, text="Editar", command=editar, width=20).pack(pady=5)
    tk.Button(app, text="Excluir", command=excluir, width=20).pack(pady=5)
    tk.Button(app, text="Voltar", command=tela_principal, width=20).pack(pady=20)


# ================================
# TELA DE IMPORTAÇÃO / EXPORTAÇÃO
# ================================

def tela_importacao():
    for widget in app.winfo_children():
        widget.destroy()

    tk.Label(app, text="Importar / Exportar Dados", font=("Arial", 20)).pack(pady=20)

    # dummy tree only for refresh
    columns = ("id", "nome", "email", "telefone")
    tree = ttk.Treeview(app, columns=columns, show="headings")

    tk.Button(app, text="Importar CSV", width=30, command=lambda: importar_csv(tree)).pack(pady=5)
    tk.Button(app, text="Importar Excel", width=30, command=lambda: importar_excel(tree)).pack(pady=5)
    tk.Button(app, text="Importar SQL", width=30, command=lambda: importar_sql(tree)).pack(pady=5)

    tk.Label(app, text="--- Exportação ---", font=("Arial", 14)).pack(pady=10)

    tk.Button(app, text="Exportar CSV", width=30, command=exportar_csv).pack(pady=5)
    tk.Button(app, text="Exportar SQL", width=30, command=exportar_sql).pack(pady=5)

    tk.Button(app, text="Voltar", width=30, command=tela_principal).pack(pady=20)


# ================================
# INICIAR SISTEMA
# ================================

tela_login()
app.mainloop()
