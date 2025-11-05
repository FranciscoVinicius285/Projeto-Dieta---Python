import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Banco de dados
def criar_banco():
    conn = sqlite3.connect("dieta.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        nome TEXT,
        idade INTEGER,
        peso REAL,
        altura REAL,
        objetivo TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dietas (
        id INTEGER PRIMARY KEY,
        usuario_id INTEGER,
        calorias REAL,
        carboidratos REAL,
        proteinas REAL,
        gorduras REAL,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    """)

    conn.commit()
    conn.close()

# Cálculo TMB
def calcular_tmb(peso, altura, idade, sexo="M"):
    if sexo.upper() == "M":
        return 10 * peso + 6.25 * altura - 5 * idade + 5
    else:
        return 10 * peso + 6.25 * altura - 5 * idade - 161

# Cálculo dieta
def calcular_dieta(tmb, objetivo):
    manutencao = tmb * 1.55

    if objetivo.lower() == "emagrecer":
        calorias = manutencao * 0.8
        macros = (0.4, 0.4, 0.2)
    elif objetivo.lower() == "ganhar peso":
        calorias = manutencao * 1.2
        macros = (0.25, 0.55, 0.2)
    else:
        calorias = manutencao
        macros = (0.3, 0.4, 0.3)

    proteina = (calorias * macros[0]) / 4
    carbo = (calorias * macros[1]) / 4
    gordura = (calorias * macros[2]) / 9

    return calorias, carbo, proteina, gordura


# Cadastro
def cadastrar_usuario(nome, idade, peso, altura, objetivo, sexo="M"):
    conn = sqlite3.connect("dieta.db")
    cursor = conn.cursor()

    cursor.execute("INSERT INTO usuarios (nome, idade, peso, altura, objetivo) VALUES (?, ?, ?, ?, ?)",
                   (nome, idade, peso, altura, objetivo))
    usuario_id = cursor.lastrowid

    tmb = calcular_tmb(peso, altura, idade, sexo)
    calorias, carb, prot, gord = calcular_dieta(tmb, objetivo)

    cursor.execute("INSERT INTO dietas (usuario_id, calorias, carboidratos, proteinas, gorduras) VALUES (?, ?, ?, ?, ?)",
                   (usuario_id, calorias, carb, prot, gord))

    conn.commit()
    conn.close()


# Interface
def interface_dieta():
    criar_banco()

    root = tk.Tk()
    root.title("Smart Dieta")
    root.geometry("520x400")
    root.resizable(False, False)

    # Campos
    tk.Label(root, text="Nome:").grid(row=0, column=0)
    entry_nome = tk.Entry(root)
    entry_nome.grid(row=0, column=1)

    tk.Label(root, text="Idade:").grid(row=1, column=0)
    entry_idade = tk.Entry(root)
    entry_idade.grid(row=1, column=1)

    tk.Label(root, text="Peso (kg):").grid(row=2, column=0)
    entry_peso = tk.Entry(root)
    entry_peso.grid(row=2, column=1)

    tk.Label(root, text="Altura (cm):").grid(row=3, column=0)
    entry_altura = tk.Entry(root)
    entry_altura.grid(row=3, column=1)

    tk.Label(root, text="Sexo:").grid(row=4, column=0)
    sexo_var = ttk.Combobox(root, values=["M", "F"], width=17)
    sexo_var.set("M")
    sexo_var.grid(row=4, column=1)

    tk.Label(root, text="Objetivo:").grid(row=5, column=0)
    objetivo_var = ttk.Combobox(root, values=["emagrecer", "ganhar peso", "saúde"], width=17)
    objetivo_var.set("emagrecer")
    objetivo_var.grid(row=5, column=1)

    # Obter dados para lista
    def obter_dietas():
        conn = sqlite3.connect("dieta.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.nome, u.objetivo, d.calorias, d.carboidratos, d.proteinas, d.gorduras
            FROM usuarios u
            JOIN dietas d ON u.id = d.usuario_id
        """)
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    # Atualizar a lista e mostrar os valores do macros
    def atualizar_lista():
        lista.delete(0, tk.END)
        for idu, nome, obj, cal, carb, prot, gord in obter_dietas():
            texto = f"{idu} - {nome} ({obj}) | {cal:.0f} kcal | Carbo:{carb:.0f}g - Proteina:{prot:.0f}g - Gordura:{gord:.0f}g"
            lista.insert(tk.END, texto)

    # Cadastrar usuário
    def cadastrar():
        try:
            nome = entry_nome.get()
            idade = int(entry_idade.get())
            peso = float(entry_peso.get())
            altura = float(entry_altura.get())
            sexo = sexo_var.get()
            objetivo = objetivo_var.get()

            cadastrar_usuario(nome, idade, peso, altura, objetivo, sexo)
            messagebox.showinfo("Sucesso", f"Usuário {nome} cadastrado com sucesso!")

            entry_nome.delete(0, tk.END)
            entry_idade.delete(0, tk.END)
            entry_peso.delete(0, tk.END)
            entry_altura.delete(0, tk.END)

            atualizar_lista()
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    # Editar usuário
    def editar_usuario():
        selecao = lista.curselection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um usuário na lista.")
            return

        item = lista.get(selecao[0])
        id_usuario = item.split(" - ")[0]

        editar_janela = tk.Toplevel(root)
        editar_janela.title("Editar Usuário")
        editar_janela.geometry("300x300")

        tk.Label(editar_janela, text="Novo nome:").pack()
        novo_nome = tk.Entry(editar_janela)
        novo_nome.pack()

        tk.Label(editar_janela, text="Nova idade:").pack()
        nova_idade = tk.Entry(editar_janela)
        nova_idade.pack()

        tk.Label(editar_janela, text="Novo peso (kg):").pack()
        novo_peso = tk.Entry(editar_janela)
        novo_peso.pack()

        tk.Label(editar_janela, text="Novo objetivo:").pack()
        novo_obj = ttk.Combobox(editar_janela, values=["emagrecer", "ganhar peso", "saúde"])
        novo_obj.pack()

        #atualizando os dados no BD
        def salvar():
            conn = sqlite3.connect("dieta.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE usuarios SET nome=?, idade=?, peso=?, objetivo=? WHERE id=?",
                           (novo_nome.get(), nova_idade.get(), novo_peso.get(), novo_obj.get(), id_usuario))
            conn.commit()
            conn.close()
            editar_janela.destroy()
            atualizar_lista()
            messagebox.showinfo("Sucesso", "Usuário atualizado!")

        tk.Button(editar_janela, text="Salvar", command=salvar).pack(pady=10)

    # Excluir usuário
    def excluir_usuario():
        selecao = lista.curselection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um usuário na lista.")
            return

        item = lista.get(selecao[0])
        id_usuario = item.split(" - ")[0]

        if not messagebox.askyesno("Confirmar", "Deseja realmente excluir este usuário?"):
            return

        conn = sqlite3.connect("dieta.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dietas WHERE usuario_id=?", (id_usuario,))
        cursor.execute("DELETE FROM usuarios WHERE id=?", (id_usuario,))
        conn.commit()
        conn.close()

        atualizar_lista()
        messagebox.showinfo("Removido", "Usuário excluído com sucesso!")

    # Botões
    frame_botoes = tk.Frame(root)
    frame_botoes.grid(row=6, column=0, columnspan=2, pady=10)
    tk.Button(frame_botoes, text="Cadastrar", width=12, command=cadastrar).grid(row=0, column=0, padx=3)
    tk.Button(frame_botoes, text="Editar", width=12, command=editar_usuario).grid(row=0, column=1, padx=3)
    tk.Button(frame_botoes, text="Excluir", width=12, command=excluir_usuario).grid(row=0, column=2, padx=3)

    # Lista dos usuarios
    tk.Label(root, text="Usuários e Dietas:").grid(row=7, column=0, columnspan=2)
    lista = tk.Listbox(root, width=75, height=10)
    lista.grid(row=8, column=0, columnspan=2, padx=10, pady=5)

    atualizar_lista()
    root.mainloop()


if __name__ == "__main__":
    interface_dieta()
