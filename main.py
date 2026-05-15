from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from fpdf import FPDF
import time
import os
import json
import ezdxf
import math

# Módulos de Hardware e Permissões
from kivy.utils import platform
try:
    from plyer import share, gps, filechooser, camera
except ImportError:
    share = gps = filechooser = camera = None

class AplicativoObra(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.escolha_atual = "Não selecionado"
        self.setores_poligonos = {} 
        self.gps_lat = 0.0
        self.gps_lon = 0.0
        self.ultima_foto = ""
        
        # Proteção de permissões para evitar crash no Pydroid/PC
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.ACCESS_FINE_LOCATION, 
                    Permission.CAMERA, 
                    Permission.READ_EXTERNAL_STORAGE, 
                    Permission.WRITE_EXTERNAL_STORAGE
                ])
            except Exception as e:
                # Se falhar aqui, o app apenas continua
                print(f"Erro ao solicitar permissões: {e}")

        self.iniciar_gps()
        
        tela = MDScreen()
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=10)
        
        layout.add_widget(MDLabel(text="Inspeção Técnica de Aterro", halign="center", font_style="H6", adaptive_height=True))

        self.campo_utm = MDTextField(
            hint_text="Zona UTM (Ex: 23)", 
            input_filter="int", 
            size_hint_x=0.8, 
            pos_hint={"center_x": .5}
        )
        layout.add_widget(self.campo_utm)

        layout.add_widget(MDRaisedButton(
            text="SELECIONAR DXF", 
            pos_hint={"center_x": .5}, 
            size_hint_x=0.8, 
            on_release=self.abrir_seletor_dxf
        ))

        botoes_layout = MDBoxLayout(orientation='horizontal', spacing=10, adaptive_height=True)
        self.lista_botoes = []
        for nome in ["Pluvial", "Chorume", "Gás"]:
            btn = MDFillRoundFlatButton(text=nome, on_release=self.registrar_escolha)
            botoes_layout.add_widget(btn)
            self.lista_botoes.append(btn)
        layout.add_widget(botoes_layout)

        self.label_status = MDLabel(text="GPS: Aguardando...", halign="center", theme_text_color="Secondary")
        layout.add_widget(self.label_status)

        layout.add_widget(MDRaisedButton(
            text="TIRAR FOTO E REGISTRAR", 
            pos_hint={"center_x": .5}, 
            size_hint_x=0.8, 
            md_bg_color="orange", 
            on_release=self.capturar_foto
        ))
        
        layout.add_widget(MDRaisedButton(
            text="GERAR E COMPARTILHAR PDF", 
            pos_hint={"center_x": .5}, 
            size_hint_x=0.8, 
            on_release=self.finalizar_inspecao
        ))

        tela.add_widget(layout)
        return tela

    def iniciar_gps(self):
        if gps:
            try:
                gps.configure(on_location=self.atualizar_coordenadas)
                gps.start(minTime=1000, minDistance=1)
            except: 
                self.label_status.text = "GPS Indisponível"

    def atualizar_coordenadas(self, **kwargs):
        self.gps_lat = kwargs.get('lat', self.gps_lat)
        self.gps_lon = kwargs.get('lon', self.gps_lon)
        self.label_status.text = f"Lat: {self.gps_lat:.4f} Lon: {self.gps_lon:.4f}"

    def abrir_seletor_dxf(self, *args):
        if filechooser:
            filechooser.open_file(on_selection=self.processar_dxf, filters=[("CAD", "*.dxf")])

    def processar_dxf(self, selecao):
        if selecao:
            try:
                doc = ezdxf.readfile(selecao[0])
                # Extrai os pontos das polilinhas diretamente
                self.setores_poligonos = {
                    p.dxf.layer: [(pt[0], pt[1]) for pt in p.get_points()] 
                    for p in doc.modelspace().query('LWPOLYLINE')
                }
                self.label_status.text = f"DXF OK: {len(self.setores_poligonos)} setores"
            except: 
                self.label_status.text = "Erro ao ler DXF"

    def ponto_em_poligono(self, x, y, poligono):
        """ Algoritmo Ray Casting - Matemática pura sem bibliotecas externas """
        n = len(poligono)
        dentro = False
        p1x, p1y = poligono[0]
        for i in range(n + 1):
            p2x, p2y = poligono[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            dentro = not dentro
            p1x, p1y = p2x, p2y
        return dentro

    def converter_para_utm(self, lat, lon, zona):
        """ Conversão matemática de WGS84 para UTM - Sem Pyproj """
        a = 6378137.0; f = 1/298.257223563; k0 = 0.9996
        phi = math.radians(lat); lam = math.radians(lon)
        lam0 = math.radians((zona * 6 - 183))
        e2 = 2*f - f**2; ep2 = e2/(1-e2); n = f/(2-f)
        A = a*(1 + n**2/4); B = (3/2*n)*a; C = (15/16*n**2)*a; D = (35/48*n**3)*a
        M = A*phi - B*math.sin(2*phi) + C*math.sin(4*phi) - D*math.sin(6*phi)
        nu = a/math.sqrt(1 - e2*math.sin(phi)**2); p = lam - lam0
        E = 500000 + k0*nu*(p*math.cos(phi))
        N = 10000000 + k0*(M + nu*math.tan(phi)*(p**2*math.cos(phi)**2/2))
        return E, N

    def identificar_setor(self, lat, lon):
        if not self.campo_utm.text: return "Zona UTM ?"
        try:
            utm_e, utm_n = self.converter_para_utm(lat, lon, int(self.campo_utm.text))
            for layer, pontos in self.setores_poligonos.items():
                if self.ponto_em_poligono(utm_e, utm_n, pontos): 
                    return layer
        except: 
            return "Erro UTM"
        return "Fora"

    def registrar_escolha(self, instancia):
        for btn in self.lista_botoes: 
            btn.md_bg_color = self.theme_cls.primary_color
        instancia.md_bg_color = [0.1, 0.7, 0.3, 1]
        self.escolha_atual = instancia.text

    def capturar_foto(self, *args):
        if self.escolha_atual == "Não selecionado":
            self.label_status.text = "Selecione o tipo primeiro!"
            return
        
        # Define caminho da foto na pasta interna do App
        nome_foto = f"foto_{int(time.time())}.jpg"
        self.ultima_foto = os.path.join(self.user_data_dir, nome_foto)
        
        if camera:
            try:
                camera.take_picture(filename=self.ultima_foto, on_complete=self.salvar_registro_final)
            except:
                self.salvar_registro_final(self.ultima_foto)
        else:
            self.salvar_registro_final(self.ultima_foto)

    def salvar_registro_final(self, caminho_foto):
        setor = self.identificar_setor(self.gps_lat, self.gps_lon)
        dados = {
            "tipo": self.escolha_atual, 
            "setor": setor, 
            "foto": caminho_foto, 
            "lat": self.gps_lat, 
            "lon": self.gps_lon, 
            "data": time.strftime("%d/%m/%Y %H:%M")
        }
        
        base = []
        caminho_base = os.path.join(self.user_data_dir, "base_inspecao.json")
        if os.path.exists(caminho_base):
            with open(caminho_base, "r") as f: 
                base = json.load(f)
        
        base.append(dados)
        with open(caminho_base, "w") as f: 
            json.dump(base, f)
        
        self.label_status.text = f"Registrado no setor: {setor}"

    def finalizar_inspecao(self, *args):
        caminho_base = os.path.join(self.user_data_dir, "base_inspecao.json")
        if not os.path.exists(caminho_base): 
            self.label_status.text = "Sem dados salvos"
            return
        
        with open(caminho_base, "r") as f: 
            dados = json.load(f)
        
        pdf = FPDF()
        for r in dados:
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"Elemento: {r['tipo']}", ln=True)
            pdf.set_font("Arial", "", 10)
            pdf.cell(0, 8, f"Setor: {r['setor']} | Coordenadas: {r['lat']:.4f}, {r['lon']:.4f}", ln=True)
            pdf.cell(0, 8, f"Data: {r['data']}", ln=True)
            
            if os.path.exists(r['foto']):
                try:
                    pdf.image(r['foto'], x=10, y=40, w=180)
                except:
                    pdf.cell(0, 10, "Erro ao carregar imagem no PDF", ln=True)

        # Caminho seguro para salvar o PDF
        caminho_pdf = os.path.join(self.user_data_dir, "Relatorio_Inspecao.pdf")
        pdf.output(caminho_pdf)
        
        if share:
            share.share(filepath=caminho_pdf)
        else:
            self.label_status.text = f"PDF salvo em: {caminho_pdf}"

if __name__ == '__main__':
    AplicativoObra().run()