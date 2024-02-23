import tkinter as tk
import subprocess

def criar_nova_janela(script):
    # Verifica se há uma janela anterior e fecha
    for widget in janela.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()

    try:
        # Executa o script
        subprocess.Popen(["python", script])
    except Exception as e:
        print(f"Erro ao executar o script {script}: {e}")

def ler_libras():
    label_resultado.config(text="Opção selecionada: Ler Libras")
    criar_nova_janela("lerLibra.py")

def gravar_libras():
    label_resultado.config(text="Opção selecionada: Gravar Libras")
    criar_nova_janela("gravavideo.py")

# Criar janela
janela = tk.Tk()
janela.title("SignTalk")

# Criar rótulo para exibir resultado
label_resultado = tk.Label(janela, text="Opção selecionada: ")
label_resultado.pack(pady=10)

# Criar botões na tela inicial
botao_ler_libras = tk.Button(janela, text="Ler Libras", command=ler_libras)
botao_ler_libras.pack(pady=10)

botao_gravar_libras = tk.Button(janela, text="Gravar Libras", command=gravar_libras)
botao_gravar_libras.pack(pady=10)

# Iniciar loop da interface gráfica
janela.mainloop()
