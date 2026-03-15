import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy import VideoFileClip
import os

def converter_video():
    # Seleciona o arquivo .mkv
    caminho_video = filedialog.askopenfilename(
        title="Selecione o vídeo",
        filetypes=[("Arquivos MKV", "*.mkv")]
    )
    
    if not caminho_video:
        return
    
    try:
        # Define o nome de saída
        saida = os.path.splitext(caminho_video)[0] + ".mp4"
        
        # Carrega e converte
        clip = VideoFileClip(caminho_video)
        clip.write_videofile(saida, codec="libx264", audio_codec="aac")
        
        messagebox.showinfo("Sucesso", f"Vídeo convertido para:\n{saida}")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{e}")

# Cria a janela principal
janela = tk.Tk()
janela.title("Conversor MKV → MP4")

botao = tk.Button(janela, text="Selecionar e Converter", command=converter_video)
botao.pack(pady=20)

janela.mainloop()
