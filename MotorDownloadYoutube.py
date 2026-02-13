import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import os
import sys
import re
import unicodedata


COR_FUNDO = 'silver'
COR_LETRA = 'black'
FONT_SIZE = 14
FONT_STYLE = ("Arial", FONT_SIZE)

NOME_SISTEMA = "Motor download mp3/mp4 para youtube"



# --- Controle de instância única ---
lock_file = "program.lock"

if os.path.exists(lock_file):
    # Já existe uma instância rodando
    print("O programa já está em execução.")
    sys.exit()

# Cria o lock
open(lock_file, "w").close()
# -----------------------------------




def listar_formatos(url, tipo):
    ydl_opts = {'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formatos = []
        for f in info['formats']:
            tamanho = f.get('filesize')
            if not tamanho:
                continue

            if tipo == "mp4" and f.get('height'):
                resolucao = f"{f['height']}p"
                codec = f.get('vcodec', 'desconhecido').upper()
                tamanho_mb = f"{round(tamanho/1024/1024,1)} MB"
                descricao = f"Vídeo {resolucao} ({codec}) - {tamanho_mb}"
                formatos.append((f['format_id'], descricao, resolucao))

            elif tipo == "mp3" and f.get('acodec') != 'none':
                codec = f.get('acodec', 'desconhecido').upper()
                abr = f.get('abr')
                qualidade = f"{abr} kbps" if abr else "?"
                tamanho_mb = f"{round(tamanho/1024/1024,1)} MB"
                descricao = f"Áudio ({codec}) - {qualidade} - {tamanho_mb}"
                formatos.append((f['format_id'], descricao, qualidade))

        duracao_seg = info.get('duration', 0)
        minutos, segundos = divmod(duracao_seg, 60)
        duracao_fmt = f"{minutos}:{segundos:02d}"
        return formatos, info['title'], duracao_fmt




def bloquear_controles(status=True):
    state = "disabled" if status else "normal"
    entry_url.config(state=state)
    combo_res.config(state=state)
    btn_carregar.config(state=state)
    btn_baixar.config(state=state)




def limpar_nome(titulo: str) -> str:
    # Normaliza para remover acentos e caracteres especiais
    titulo = unicodedata.normalize('NFKD', titulo).encode('ASCII', 'ignore').decode('ASCII')
    # Remove qualquer coisa que não seja letra, número, espaço ou hífen
    titulo = re.sub(r'[^a-zA-Z0-9\s-]', '', titulo)
    # Troca múltiplos espaços por um só
    titulo = re.sub(r'\s+', ' ', titulo).strip()
    # Limita tamanho para evitar nomes gigantes
    if len(titulo) > 100:
        titulo = titulo[:100]
    return titulo



def baixar_video(url, formato_id, tipo, titulo, extra_info):
    progress.start()
    bloquear_controles(True)
    video_file = None
    audio_file = None
    try:
        if tipo == "mp3":
            titulo_limpo = limpar_nome(titulo)
            save_path = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                initialfile=f"{titulo_limpo}_{extra_info}.mp3",
                filetypes=[("MP3 files", "*.mp3")]
            )
            if not save_path:
                return
            ydl_opts = {
                'format': formato_id,
                'outtmpl': save_path,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'ffmpeg_location': r'C:\ffmpeg\bin',
                'noplaylist': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        else:
            video_opts = {
                'format': formato_id,
                'outtmpl': 'aux_video.%(ext)s',
                'ffmpeg_location': r'C:\ffmpeg\bin',
                'noplaylist': True
            }
            audio_opts = {
                'format': 'bestaudio',
                'outtmpl': 'aux_audio.%(ext)s',
                'ffmpeg_location': r'C:\ffmpeg\bin',
                'noplaylist': True
            }
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                ydl.download([url])
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                ydl.download([url])

            video_file = next((f for f in os.listdir() if f.startswith("aux_video")), None)
            audio_file = next((f for f in os.listdir() if f.startswith("aux_audio")), None)

            titulo_limpo = limpar_nome(titulo)
            if video_file and audio_file:
                save_path = filedialog.asksaveasfilename(
                    defaultextension=".mp4",
                    initialfile=f"{titulo_limpo}_{extra_info}.mp4",
                    filetypes=[("MP4 files", "*.mp4")]
                )
                if not save_path:
                    return

                subprocess.run([
                    r"C:\ffmpeg\bin\ffmpeg.exe",
                    "-i", video_file,
                    "-i", audio_file,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    save_path
                ],
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
                )

        messagebox.showinfo("Sucesso", f"Download concluído: {os.path.basename(save_path)}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))
    finally:
        # garante que os temporários sejam removidos mesmo se cancelar
        for f in [video_file, audio_file]:
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Erro ao remover {f}: {e}")
        progress.stop()
        bloquear_controles(False)

def limpar_campos():
    entry_url.delete(0, tk.END)
    combo_res.set("")
    lbl_info.config(text="")
    formatos_cache.clear() if 'formatos_cache' in globals() else None
    formatos_cache_reversed.clear() if 'formatos_cache_reversed' in globals() else None
    titulo_cache = "" if 'titulo_cache' in globals() else None
    duracao_cache = "" if 'duracao_cache' in globals() else None


def validar_url(url):
    if url.startswith("https://youtu.be/") or url.startswith("https://www.youtube.com/watch?v=") or url.startswith("https://www.youtube.com/shorts/"):
        if "&list=" in url or "&index=" in url:
            return False
        return True
    return False

def limpar_temporarios():
    # Remove todos os arquivos temporários criados
    for f in os.listdir():
        if f.startswith("aux_video") or f.startswith("aux_audio"):
            print('Tentando remover:', f)
            try:
                os.remove(f)
                print('Removido com sucesso:', f)
            except Exception as e:
                print(f'Erro ao remover {f}: {e.__class__.__name__} - {e}')


def on_close():
    # Antes de fechar, limpa os temporários
    limpar_temporarios()
    # Remove o lock file
    if os.path.exists("program.lock"):
        os.remove("program.lock")
    root.destroy()


def iniciar_download():
    url = entry_url.get()
    if not validar_url(url):
        messagebox.showerror("Erro", "\n-URL inválida. \n-Use apenas links diretos de vídeo (não playlists) \nou \n-Clique no botão 'COMPARTILHAR' dentro do youtube.")
        return
    tipo = formato_var.get()
    idx = combo_res.current()
    if idx < 0:
        messagebox.showwarning("Aviso", "Selecione uma resolução/áudio primeiro.")
        return
    formato_id, _, extra_info = formatos_cache_reversed[idx] # usa a lista invertida
    titulo = titulo_cache
    threading.Thread(target=baixar_video, args=(url, formato_id, tipo, titulo, extra_info)).start()

def carregar_resolucoes():

    limpar_temporarios()

    url = entry_url.get()
    if not validar_url(url):
        messagebox.showerror("Erro", "\n-URL inválida.")
        return
    tipo = formato_var.get()
    global formatos_cache, formatos_cache_reversed, titulo_cache, duracao_cache
    formatos_cache, titulo_cache, duracao_cache = listar_formatos(url, tipo)
    # inverter ordem e guardar
    formatos_cache_reversed = list(reversed(formatos_cache))
    combo_res['values'] = [desc for _, desc, _ in formatos_cache_reversed]
    if formatos_cache_reversed:
        combo_res.current(0)
    lbl_info.config(text=f"Título: {titulo_cache}\nDuração: {duracao_cache}")



# Interface Tkinter
root = tk.Tk()
root.title(NOME_SISTEMA)
root.configure(bg=COR_FUNDO)

# Título principal centralizado
titulo_principal = tk.Label(root, text=NOME_SISTEMA,
                            bg=COR_FUNDO, fg=COR_LETRA,
                            font=("Arial", 20, "bold"))
titulo_principal.pack(pady=15)

# Criar menu de contexto para o Entry
menu_contexto = tk.Menu(root, tearoff=0)
menu_contexto.add_command(label="Colar", command=lambda: entry_url.event_generate("<<Paste>>"))

def mostrar_menu(event):
    menu_contexto.tk_popup(event.x_root, event.y_root)

# Frame para URL e botão limpar
frame_url = tk.Frame(root, bg=COR_FUNDO)
frame_url.pack(pady=5)

btn_limpar = tk.Button(frame_url, text="Limpar", command=limpar_campos,
                       bg="gray", fg=COR_LETRA, font=FONT_STYLE)
btn_limpar.pack(side="left", padx=5)

entry_url = tk.Entry(frame_url, width=50, font=FONT_STYLE,
                     bg=COR_FUNDO, fg=COR_LETRA, insertbackground=COR_LETRA)
entry_url.pack(side="left", padx=5)
entry_url.bind("<Button-3>", mostrar_menu)

# Frame para opções de formato
frame_formatos = tk.Frame(root, bg=COR_FUNDO)
frame_formatos.pack(pady=5)

formato_var = tk.StringVar(value="mp4")
tk.Radiobutton(frame_formatos, text="MP4 (vídeo)", variable=formato_var, value="mp4",
               bg=COR_FUNDO, fg=COR_LETRA, selectcolor=COR_FUNDO, font=FONT_STYLE).pack(side="left", padx=10)
tk.Radiobutton(frame_formatos, text="MP3 (áudio)", variable=formato_var, value="mp3",
               bg=COR_FUNDO, fg=COR_LETRA, selectcolor=COR_FUNDO, font=FONT_STYLE).pack(side="left", padx=10)

btn_carregar = tk.Button(root, text="Carregar opções", command=carregar_resolucoes,
                         bg="gray", fg=COR_LETRA, font=FONT_STYLE)
btn_carregar.pack(pady=5)

lbl_info = tk.Label(root, text="", justify="left", bg=COR_FUNDO, fg=COR_LETRA, font=FONT_STYLE)
lbl_info.pack(pady=5)

combo_res = ttk.Combobox(root, width=50, font=FONT_STYLE)
combo_res.pack(pady=5, padx=20)

btn_baixar = tk.Button(root, text="Baixar", command=iniciar_download,
                       bg="gray", fg=COR_LETRA, font=FONT_STYLE)
btn_baixar.pack(pady=10)

progress = ttk.Progressbar(root, mode="indeterminate")
progress.pack(fill="x", pady=5, padx=20) 


style = ttk.Style()
style.theme_use("default")
style.configure("TCombobox", fieldbackground=COR_FUNDO, background=COR_FUNDO, foreground=COR_LETRA)
style.configure("TProgressbar", troughcolor=COR_FUNDO, background="gray")

footer = tk.Label(root, text="Developed by~~> @_fdutra",
                  bg=COR_FUNDO, fg=COR_LETRA, font=("Arial", 10))
footer.pack(side="bottom", pady=7)

if getattr(sys, 'frozen', False):
    diretorio_atual = sys._MEIPASS
else:
    diretorio_atual = os.getcwd()

icone_path = os.path.join(diretorio_atual, "icone", "youtube.ico")
root.iconbitmap(icone_path)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
