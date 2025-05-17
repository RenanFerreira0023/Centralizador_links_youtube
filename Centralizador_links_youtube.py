import kivy
kivy.require('2.1.0')  # ou a versão que você está usando

from kivy.config import Config
Config.set('kivy', 'window', 'sdl2')

print(kivy.__version__)

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.uix.spinner import Spinner
from kivy.graphics import Color, RoundedRectangle
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.checkbox import CheckBox

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


import json
import os
import requests
from bs4 import BeautifulSoup
import re
import webbrowser


def quebra_linha(text, limite=20):
    return '\n'.join([text[i:i+limite] for i in range(0, len(text), limite)])

class Card(BoxLayout):
    def __init__(self, title, categoria, duracao, image_path=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [dp(10), dp(10), dp(10), dp(5)]
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(400)
        self.title = title

        with self.canvas.before:
            Color(0.5, 0.5, 0.1, 0.2)
            self.bg = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
        self.bind(pos=self.update_rect, size=self.update_rect)

        caminhoImagem = os.path.join(os.getcwd(), 'imagens', image_path + ".jpg")

        print(image_path)
        print(caminhoImagem)
        if image_path and os.path.exists(caminhoImagem):
            self.add_widget(Image(source=caminhoImagem, size_hint=(None, None),  pos_hint={'center_x': 0.5} ,size=(dp(280), dp(250))))

        self.add_widget(Label(
            text=quebra_linha(title, 28),
            font_size='17sp',
             size_hint=(1, None),
            height=dp(30),
            halign='center'
        ))

        bottom_layout = BoxLayout(orientation='horizontal', spacing=dp(10), padding=[dp(5), dp(5)])

        info_layout = BoxLayout(orientation='vertical', size_hint=(1, None), height=dp(50))
        info_layout.add_widget(Label(text=f"{categoria}", font_size='20sp', halign='center'))
        info_layout.add_widget(Label(text=f"{duracao}", font_size='14sp', halign='center'))

        button_layout = BoxLayout(orientation='vertical', size_hint=(None, None), width=dp(80), spacing=dp(5))
        delete_button = Button(text='Deletar', size_hint=(1, None), height=dp(30))
        delete_button.bind(on_release=lambda x: self.show_delete_dialog(title))
        abrir_button = Button(text='Abrir', size_hint=(1, None), height=dp(30))
        abrir_button.bind(on_release=lambda x: self.abrir_video(image_path))

        button_layout.add_widget(delete_button)
        button_layout.add_widget(abrir_button)

        bottom_layout.add_widget(info_layout)
        bottom_layout.add_widget(button_layout)

        self.add_widget(bottom_layout)

    def show_delete_dialog(self, title):
        self.dialog = MDDialog(
            title="Deletar este vídeo",
            text=f"Tem certeza que deseja deletar? [ {title} ]",
            buttons=[
                MDFlatButton(text="Não", on_release=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="Deletar", on_release=lambda x: self.delete_card())
            ],
        )
        self.dialog.open()

    def abrir_video(self, idYoutube):
        url = f"https://www.youtube.com/watch?v={idYoutube}"
        webbrowser.open(url)

    def delete_card(self):
        self.parent.remove_widget(self)
        arquivo_json = 'videos.json'
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as file:
                data = json.load(file)
                videos = data.get('videos', [])
            for video in videos:
                if video.get('nome_video') == self.title:
                    caminho_imagem = os.path.join(os.getcwd(), 'imagens', video.get('nome_imagem', ''))
                    if os.path.exists(caminho_imagem):
                        os.remove(caminho_imagem)
                        print(f"Imagem '{caminho_imagem}' removida com sucesso.")
                    videos.remove(video)
                    self.dialog.dismiss()
                    break
            with open(arquivo_json, 'w', encoding='utf-8') as file:
                json.dump({'videos': videos}, file, ensure_ascii=False, indent=4)
            print(f"Vídeo '{self.title}' removido com sucesso do arquivo JSON.")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Erro ao remover vídeo: {e}")

    def update_rect(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class CardGrid(GridLayout):
    def on_window_resize(self, instance, size):
        self.update_columns(size[0])

    def update_columns(self, width):
        self.cols = max(3, int(width / dp(300)))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spacing = dp(10)
        self.padding = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        self.update_columns(Window.size[0])
        Window.bind(size=self.on_window_resize)

        for card in carregar_videos(''):
            self.add_widget(card)


def carregar_videos(filtroPalavra,filtro='Titulo'):
    cards = []  
    try:
        with open('videos.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            videos = data.get('videos', [])

            for video in videos:
                titulo = video.get('nome_video', 'Sem título')
                categoria = video.get('categoriaVideo', 'Geral')
                if(filtro == 'Titulo'and ( filtroPalavra == '' or filtroPalavra.lower() in titulo.lower() )):
                    duracao = video.get('tempo_video', 'Desconhecida')
                    imagem = video.get('nome_imagem', None)

                    if imagem and imagem.startswith("imagens/"):
                        imagem = imagem.replace("imagens/", "")

                    card = Card(title=titulo, categoria=categoria, duracao=duracao, image_path=imagem)
                    cards.append(card)

                if(filtro == 'Categoria' and ( filtroPalavra == '' or filtroPalavra.lower() in categoria.lower() )):
                    duracao = video.get('tempo_video', 'Desconhecida')
                    imagem = video.get('nome_imagem', None)

                    if imagem and imagem.startswith("imagens/"):
                        imagem = imagem.replace("imagens/", "")

                    card = Card(title=titulo, categoria=categoria, duracao=duracao, image_path=imagem)
                    cards.append(card)

        return cards
    except FileNotFoundError:
        print("Arquivo 'videos.json' não encontrado.")
        return []
    except json.JSONDecodeError:
        print("Erro ao decodificar o arquivo JSON.")
        return []


def verificar_imagem(thumbnail_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        response = requests.get(thumbnail_url, headers=headers, timeout=10,verify=False)
        if response.status_code == 200:
            print("Imagem encontrada e carregada com sucesso!")
            return thumbnail_url
        else:
            print(f"Erro ao acessar imagem: Status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

def baixar_imagem(thumbnail_url, video_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }

    try:
        response = requests.get(thumbnail_url, headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            if not os.path.exists("imagens"):
                os.makedirs("imagens")
            
            caminho_imagem = f"imagens/{video_id}.jpg"
            
            with open(caminho_imagem, "wb") as file:
                file.write(response.content)
            
            print(f"Imagem salva em: {caminho_imagem}")
            return caminho_imagem
        else:
            print(f"Erro ao acessar imagem: Status {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None

def obter_titulo_e_duracao(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url, verify=False)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find("title").text.replace(" - YouTube", "").strip()

        scripts = soup.find_all("script")
        for script in scripts:
            if 'ytInitialPlayerResponse' in script.text:
                json_text = re.search(r'var ytInitialPlayerResponse = ({.*?});', script.string)
                if json_text:
                    data = json.loads(json_text.group(1))
                    try:
                        duration = data['videoDetails']['lengthSeconds']
                        minutos, segundos = divmod(int(duration), 60)
                        duracao_formatada = f"{minutos}min {segundos}s"
                    except KeyError:
                        duracao_formatada = "Duração não encontrada"

                    resolutions = ["maxresdefault", "hqdefault", "mqdefault", "default"]
                    thumbnail_url = None


                    for res in resolutions:
                        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/{res}.jpg"
                        if verificar_imagem(thumbnail_url):
                            caminho_imagem = baixar_imagem(thumbnail_url, video_id)
                            if caminho_imagem:
                                nome_imagem = os.path.basename(caminho_imagem)  # Pegar apenas o nome do arquivo
                                return title, duracao_formatada, nome_imagem

        return title, "Duração não encontrada", None
    return "Erro ao obter título", "Erro ao obter duração", None


def filtrar_videos(card_grid, texto):
    card_grid.clear_widgets()
    if not hasattr(card_grid, 'videos'):
        return

    if texto == '':
        cards = carregar_videos('')
        for card in cards:
            card_grid.add_widget(card)
        return
    for video in card_grid.videos:
        if texto.lower() in video['title'].lower():
            card_grid.add_widget(Card(video['title'], video['categoria'], video['duracao'], video['image_path']))



class ResponsiveApp(MDApp):


    def build(self):
        root = BoxLayout(orientation='vertical')

        self.title = "Centralizador de link do Renato"      
        diretorio_atual = os.getcwd()
        icone_path = os.path.join(diretorio_atual,"icone", "icone.ico")
        Window.set_icon(icone_path) 

        Window.size = (1000, 800) 

        self.theme_cls.theme_style = "Dark"  
        self.theme_cls.primary_palette = "Teal" 
        
        def save_video(self, url, tempo, categoria, nome, nomeImagem):
            if categoria == 'Selecione uma categoria':
                categoria = 'Geral'

            data = {'videos': []}
            if os.path.exists('videos.json'):
                with open('videos.json', 'r', encoding='utf-8') as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        pass


            video_existente = False
            for video in data['videos']:
                if nomeImagem in video['url_video'] :
                    video['tempo_video'] = tempo
                    video['categoriaVideo'] = categoria
                    video['nome_video'] = nome
                    video['nome_imagem'] = nomeImagem
                    video_existente = True
                    break

            if not video_existente:
                data['videos'].append({
                    'url_video': url,
                    'tempo_video': tempo,
                    'categoriaVideo': categoria,
                    'nome_video': nome,
                    'nome_imagem': nomeImagem
                })

            with open('videos.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False)

            cards = carregar_videos('')
            card_grid.clear_widgets()
            for card in cards:
                card_grid.add_widget(card)

        def show_add_popup(self):
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
            input_url = TextInput(hint_text='URL do vídeo', multiline=True  ,size_hint_y=None, height=dp(50),    halign='center' )
            content.add_widget(input_url)

            save_carregarVideo = Button(text='Carregar vídeo', size_hint_y=None, height=dp(40))
            content.add_widget(save_carregarVideo)

            def carregar_video(url):
                youtube_regex = re.compile(r'(https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)|https?://(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+))')

                match = youtube_regex.match(url)
                if match:

                    video_id = match.group(2) if match.group(2) else match.group(3)
                    titulo, duracao, caminho_imagem = obter_titulo_e_duracao(video_id)
                    
                    caminhoImagem = os.path.join(os.getcwd(), 'imagens', caminho_imagem)
                    caminho_imagem = caminhoImagem

                    if caminho_imagem:
                        thumbnail_image = Image(source=caminho_imagem, size_hint=(None, None), size=(dp(500), dp(450)), pos_hint={'center_x': 0.5, 'center_y': 0.5})
                        content.add_widget(thumbnail_image)
                    
                    texto = titulo.encode('utf-8').decode('utf-8')
                    content.add_widget(Label(text=f"Título: {texto}", size_hint_y=None, height=dp(10)))
                    content.add_widget(Label(text=f"Duração: {duracao}", size_hint_y=None, height=dp(10)))
                    categorias = ["Culinaria", "Historia", "Musica", "Geral"]
                    categoria_spinner = Spinner(text='Selecione uma categoria', values=categorias, size_hint_y=None, height=dp(40), background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1), background_normal='', background_down='', font_size='18sp')
                    content.add_widget(categoria_spinner)

                    save_button = Button(text='Salvar', size_hint_y=None, height=dp(40))
                    content.add_widget(save_button)


                    save_button.bind(on_release=lambda x: (save_video(self, input_url.text, duracao,categoria_spinner.text, titulo,video_id), popup.dismiss()))

                    save_carregarVideo.disabled = True  
                    input_url.disabled = True  

                else:
                    print("URL inválida: não é um vídeo do YouTube")

            save_carregarVideo.bind(on_release=lambda x: carregar_video(input_url.text))  
            popup = Popup(title='Adicionar Vídeo', content=content, size_hint=(0.9, 0.9))
            popup.open()


        add_button = Button(
            text='Adicionar um novo vídeo à lista',
            size_hint_y=None,
            height=dp(50)
        )
        add_button.bind(on_release=lambda x: show_add_popup(self))
        root.add_widget(add_button)



        search_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=(dp(10), 0, dp(10), 0)  
        )


        search_input = TextInput(
            hint_text='Pesquisar vídeos...',
            size_hint=(0.6, 1), 
            multiline=False,
             halign='center' 
        )


        checkbox_title = CheckBox(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            active=True  
        )
        label_title = Label(
            text='Título',
            size_hint=(None, None),
            size=(dp(60), dp(30))
        )

        checkbox_category = CheckBox(
            size_hint=(None, None),
            size=(dp(30), dp(30))
        )
        label_category = Label(
            text='Categoria',
            size_hint=(None, None),
            size=(dp(90), dp(30))
        )

        def on_checkbox_active(instance, value):
            if instance == checkbox_title and value:
                checkbox_category.active = False
            elif instance == checkbox_category and value:
                checkbox_title.active = False

        checkbox_title.bind(active=on_checkbox_active)
        checkbox_category.bind(active=on_checkbox_active)

        def on_text_change(instance, value):
            filtro = 'Titulo' if checkbox_title.active else 'Categoria'
            print(f"Texto alterado para: {value}, Filtro: {filtro}")
            cards = carregar_videos(value,filtro)
            card_grid.clear_widgets()
            for card in cards:
                card_grid.add_widget(card)

        search_input.bind(text=on_text_change)

        search_layout.add_widget(search_input)
        search_layout.add_widget(label_title)
        search_layout.add_widget(checkbox_title)
        search_layout.add_widget(label_category)
        search_layout.add_widget(checkbox_category)

        root.add_widget(search_layout)

        grid = ScrollView()
        card_grid = CardGrid()
        grid.add_widget(card_grid)
        root.add_widget(grid)

        return root

if __name__ == '__main__':
    ResponsiveApp().run()
