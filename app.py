import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import subprocess
import os
import threading
import time
import shutil
import sys
import json
import re
from datetime import datetime
from PIL import Image
import psutil
import platform

# Configurar tema e aparência
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MTechBotManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("🤖 MTECH BOT MANAGER - Sistema Profissional")
        self.geometry("1600x1000")
        self.minsize(1400, 800)
        
        # Configurar pasta
        self.bot_dir = os.path.dirname(os.path.abspath(__file__))
        self.bot_file = os.path.join(self.bot_dir, "chatbot.js")
        self.qr_image_file = os.path.join(self.bot_dir, "qrcode.png")
        self.recargas_config_file = os.path.join(self.bot_dir, "recargas_config.json")
        
        # Variáveis
        self.bot_process = None
        self.bot_running = False
        self.bot_connected = False
        self.qr_ctk_image = None
        self.monitoring = True
        self.real_time_update = True
        self.dashboard_info = {}
        self.stats = {
            "total_messages": 0,
            "total_connections": 0,
            "start_time": None,
            "cpu_history": [],
            "ram_history": [],
            "max_cpu": 0,
            "min_cpu": 100,
            "avg_cpu": 0,
            "max_ram": 0,
            "min_ram": 999999,
            "avg_ram": 0
        }
        
        # Carregar configurações
        self.load_full_bot_config()
        self.load_recargas_config()
        
        # Criar interface
        self.create_widgets()
        self.check_bot_file()
        
        # Iniciar monitoramento
        self.start_qr_monitoring()
        self.start_real_time_dashboard()
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_recargas_config(self):
        """Carregar configurações de recargas do arquivo JSON"""
        self.recargas_config = {
            "vivo": {
                "10": {"paga": 10.00, "recebe": 10.00},
                "20": {"paga": 20.00, "recebe": 20.00},
                "30": {"paga": 30.00, "recebe": 30.00},
                "50": {"paga": 50.00, "recebe": 50.00},
                "100": {"paga": 100.00, "recebe": 100.00}
            },
            "tim": {
                "10": {"paga": 10.00, "recebe": 10.00},
                "20": {"paga": 20.00, "recebe": 20.00},
                "30": {"paga": 30.00, "recebe": 30.00},
                "50": {"paga": 50.00, "recebe": 50.00},
                "100": {"paga": 100.00, "recebe": 100.00}
            },
            "claro": {
                "10": {"paga": 10.00, "recebe": 10.00},
                "20": {"paga": 20.00, "recebe": 20.00},
                "30": {"paga": 30.00, "recebe": 30.00},
                "50": {"paga": 50.00, "recebe": 50.00},
                "100": {"paga": 100.00, "recebe": 100.00}
            }
        }
        
        if os.path.exists(self.recargas_config_file):
            try:
                with open(self.recargas_config_file, "r", encoding="utf-8") as f:
                    self.recargas_config = json.load(f)
                self.add_log("✅ Configurações de recargas carregadas!")
            except Exception as e:
                self.add_log(f"⚠️ Erro ao carregar recargas: {e}")
    
    def save_recargas_config_to_file(self):
        """Salvar configurações de recargas no arquivo JSON"""
        try:
            with open(self.recargas_config_file, "w", encoding="utf-8") as f:
                json.dump(self.recargas_config, f, indent=2, ensure_ascii=False)
            self.add_log("✅ Configurações de recargas salvas no arquivo!")
            return True
        except Exception as e:
            self.add_log(f"❌ Erro ao salvar recargas: {e}")
            return False
    
    def update_menu_recargas_display(self):
        """Atualizar o texto do menu de recargas no chatbot.js com os valores atuais"""
        if not os.path.exists(self.bot_file):
            return
        
        try:
            with open(self.bot_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Buscar o menu de recargas atual
            menu_pattern = r'(const menuRecargas = `)([^`]+)(`)'
            match = re.search(menu_pattern, content, re.DOTALL)
            
            if match:
                current_menu = match.group(2)
                
                # Criar as linhas do menu com os valores atuais (usando TIM como referência, pois são iguais para todas)
                valor_10_paga = self.recargas_config["tim"]["10"]["paga"]
                valor_10_recebe = self.recargas_config["tim"]["10"]["recebe"]
                valor_20_paga = self.recargas_config["tim"]["20"]["paga"]
                valor_20_recebe = self.recargas_config["tim"]["20"]["recebe"]
                valor_30_paga = self.recargas_config["tim"]["30"]["paga"]
                valor_30_recebe = self.recargas_config["tim"]["30"]["recebe"]
                valor_50_paga = self.recargas_config["tim"]["50"]["paga"]
                valor_50_recebe = self.recargas_config["tim"]["50"]["recebe"]
                valor_100_paga = self.recargas_config["tim"]["100"]["paga"]
                valor_100_recebe = self.recargas_config["tim"]["100"]["recebe"]
                
                # Atualizar as linhas do menu
                new_menu = current_menu
                new_menu = re.sub(r'4️⃣1️⃣ → R\$ [\d,]+\s+cai R\$ [\d,]+ de créditos', 
                                 f'4️⃣1️⃣ → R$ {valor_10_paga:.2f}'.replace('.', ',') + f' cai R$ {valor_10_recebe:.2f}'.replace('.', ',') + ' de créditos', new_menu)
                new_menu = re.sub(r'4️⃣2️⃣ → R\$ [\d,]+\s+cai R\$ [\d,]+ de créditos', 
                                 f'4️⃣2️⃣ → R$ {valor_20_paga:.2f}'.replace('.', ',') + f' cai R$ {valor_20_recebe:.2f}'.replace('.', ',') + ' de créditos', new_menu)
                new_menu = re.sub(r'4️⃣3️⃣ → R\$ [\d,]+\s+cai R\$ [\d,]+ de créditos', 
                                 f'4️⃣3️⃣ → R$ {valor_30_paga:.2f}'.replace('.', ',') + f' cai R$ {valor_30_recebe:.2f}'.replace('.', ',') + ' de créditos', new_menu)
                new_menu = re.sub(r'4️⃣4️⃣ → R\$ [\d,]+\s+cai R\$ [\d,]+ de créditos', 
                                 f'4️⃣4️⃣ → R$ {valor_50_paga:.2f}'.replace('.', ',') + f' cai R$ {valor_50_recebe:.2f}'.replace('.', ',') + ' de créditos', new_menu)
                new_menu = re.sub(r'4️⃣5️⃣ → R\$ [\d,]+\s+cai R\$ [\d,]+ de créditos', 
                                 f'4️⃣5️⃣ → R$ {valor_100_paga:.2f}'.replace('.', ',') + f' cai R$ {valor_100_recebe:.2f}'.replace('.', ',') + ' de créditos', new_menu)
                
                # Substituir o menu completo
                new_content = content[:match.start(2)] + new_menu + content[match.end(2):]
                
                with open(self.bot_file, "w", encoding="utf-8") as f:
                    f.write(new_content)
                
                self.add_log("✅ Menu de recargas atualizado visualmente!")
                return True
            
            return False
        except Exception as e:
            self.add_log(f"❌ Erro ao atualizar menu de recargas: {e}")
            return False
    
    def load_full_bot_config(self):
        """Carregar TODAS as configurações do chatbot.js"""
        self.bot_config = {
            "proprietario": "5583988387164",
            "precos_iptv": {"1_mes": 25.00, "3_meses": 75.00, "6_meses": 150.00, "12_meses": 300.00},
            "precos_internet": {"1_mes": 20.00, "3_meses": 60.00, "6_meses": 120.00, "12_meses": 240.00},
            "links_iptv": {
                "1": "", "2": "", "3": "", "4": "", "5": "",
                "6": "", "7": "", "8": "", "9": "", "10": "",
                "11": "", "12": "", "13": "", "14": "", "15": ""
            },
            "menus": {},
            "mensagens": {
                "boas_vindas": [],
                "agradecimento": [],
                "despedida": [],
                "nao_entendi": []
            },
            "configuracoes": {
                "tempo_pausa": 30,
                "limite_testes": 1,
                "antiflood": 2
            },
            "planos_iptv": {
                "1_mes": "R$ 29,90",
                "3_meses": "R$ 69,90",
                "6_meses": "R$ 119,90",
                "12_meses": "R$ 199,90"
            },
            "planos_internet": {
                "1_mes": "R$ 49,90",
                "3_meses": "R$ 129,90",
                "6_meses": "R$ 199,90",
                "12_meses": "R$ 349,90"
            }
        }
        
        if os.path.exists(self.bot_file):
            try:
                with open(self.bot_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Proprietário
                match = re.search(r'const numeroProprietario = "([0-9]+)@', content)
                if match:
                    self.bot_config["proprietario"] = match.group(1)
                
                # Links IPTV
                links_section = re.search(r'const linksAPI = \{(.*?)\};', content, re.DOTALL)
                if links_section:
                    links_content = links_section.group(1)
                    
                    link_map = {
                        "teste1hr1": "1",
                        "teste1hr2": "2",
                        "teste1hrFutebol": "3",
                        "teste2hrs": "4",
                        "teste4hrs": "5",
                        "teste6hrIbo": "6",
                        "teste12hrSemAdultos": "7",
                        "teste12hrSamsung": "8",
                        "teste12hrLg": "9",
                        "teste12hrAndroid": "10",
                        "teste12hrIphone": "11",
                        "teste12hrTvBox": "12",
                        "testePcNotebook": "13",
                        "testeRoku": "14",
                        "testeFireStick": "15"
                    }
                    
                    for js_name, numero in link_map.items():
                        pattern = rf'{js_name}:\s*"([^"]+)"'
                        match = re.search(pattern, links_content)
                        if match:
                            self.bot_config["links_iptv"][numero] = match.group(1)
                
                # Menus principais
                menus_map = {
                    "principal": "menuPrincipal",
                    "iptv": "menuIPTV",
                    "internet": "menuInternet",
                    "recargas": "menuRecargas",
                    "consultas": "menuConsultas",
                    "ajuda": "menuAjuda",
                    "configuracoes": "menuConfiguracoes",
                    "termos": "menuTermos"
                }
                
                for menu_key, var_name in menus_map.items():
                    pattern = rf'const {var_name} = `([^`]+)`'
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        self.bot_config["menus"][menu_key] = match.group(1)
                        print(f"✅ Menu {menu_key} carregado com sucesso!")
                
                # Mensagens
                msg_patterns = {
                    "boas_vindas": "respostasBoasVindas",
                    "agradecimento": "respostasAgradecimento",
                    "despedida": "respostasDespedida",
                    "nao_entendi": "respostasNaoEntendi"
                }
                
                for key, var_name in msg_patterns.items():
                    pattern = rf'const {var_name} = \[([^\]]+)\]'
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        self.bot_config["mensagens"][key] = re.findall(r'"([^"]+)"', match.group(1))
                    
            except Exception as e:
                print(f"Erro ao carregar config: {e}")
        
        # Se o menu principal não foi carregado, criar um padrão
        if "principal" not in self.bot_config["menus"] or not self.bot_config["menus"]["principal"]:
            self.bot_config["menus"]["principal"] = """*📱 MENU PRINCIPAL - MTECH* 📱

*Digite o número da opção desejada:*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣ → 📺 TESTES IPTV
2️⃣ → 🌐 TESTE INTERNET ILIMITADA
3️⃣ → 📱 RECARGAS DE CHIP
4️⃣ → 🔧 SUPORTE IPTV
5️⃣ → 🔧 SUPORTE INTERNET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1️⃣0️⃣ → 📋 CONSULTAS
2️⃣0️⃣ → 👤 MINHA CONTA
3️⃣0️⃣ → 🎁 INDICAR AMIGOS
4️⃣0️⃣ → ❓ AJUDA
5️⃣0️⃣ → ⚖️ TERMOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6️⃣ → ⏸️ PAUSAR ATENDIMENTO (30min)
1️⃣0️⃣0️⃣ → 👨‍💼 FALAR COM PROPRIETÁRIO

📌 *Digite o número da opção desejada*"""
    
    def start_real_time_dashboard(self):
        """Iniciar atualização em tempo real do dashboard"""
        def update_loop():
            while self.real_time_update:
                try:
                    self.update_dashboard_real_time()
                    time.sleep(1)
                except:
                    time.sleep(1)
        
        threading.Thread(target=update_loop, daemon=True).start()
        self.add_log("📊 Dashboard em tempo real ativado (atualização a cada 1s)")
    
    def update_dashboard_real_time(self):
        """Atualizar dashboard em tempo real"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_used_mb = ram.used / (1024 * 1024)
            ram_total_mb = ram.total / (1024 * 1024)
            
            self.stats["cpu_history"].append(cpu_percent)
            self.stats["ram_history"].append(ram_used_mb)
            
            if len(self.stats["cpu_history"]) > 60:
                self.stats["cpu_history"].pop(0)
            if len(self.stats["ram_history"]) > 60:
                self.stats["ram_history"].pop(0)
            
            if self.stats["cpu_history"]:
                self.stats["max_cpu"] = max(self.stats["cpu_history"])
                self.stats["min_cpu"] = min(self.stats["cpu_history"])
                self.stats["avg_cpu"] = sum(self.stats["cpu_history"]) / len(self.stats["cpu_history"])
            
            if self.stats["ram_history"]:
                self.stats["max_ram"] = max(self.stats["ram_history"])
                self.stats["min_ram"] = min(self.stats["ram_history"])
                self.stats["avg_ram"] = sum(self.stats["ram_history"]) / len(self.stats["ram_history"])
            
            self.after(0, lambda: self.update_dashboard_labels(
                cpu_percent, ram_percent, ram_used_mb, ram_total_mb
            ))
            
            self.after(0, lambda: self.update_cpu_bar(cpu_percent))
            self.after(0, lambda: self.update_ram_bar(ram_percent))
            
            if self.bot_running and self.stats["start_time"]:
                elapsed = time.time() - self.stats["start_time"]
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                uptime_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.after(0, lambda: self.update_uptime_label(uptime_str))
            
            self.after(0, lambda: self.update_bot_stats())
            
        except Exception as e:
            pass
    
    def update_uptime_label(self, uptime_str):
        if hasattr(self, 'uptime_dash_label') and self.uptime_dash_label:
            self.uptime_dash_label.configure(text=uptime_str)
        if hasattr(self, 'uptime_label'):
            self.uptime_label.configure(text=f"Tempo: {uptime_str}")
        if "⏱️ Uptime:" in self.dashboard_info:
            self.dashboard_info["⏱️ Uptime:"].configure(text=uptime_str)
    
    def update_bot_stats(self):
        if hasattr(self, 'stats_messages'):
            self.stats_messages.configure(text=f"💬 Msgs: {self.stats['total_messages']}")
        if hasattr(self, 'stats_connections'):
            self.stats_connections.configure(text=f"🔌 Conexões: {self.stats['total_connections']}")
        if self.stats["start_time"]:
            start_str = datetime.fromtimestamp(self.stats["start_time"]).strftime("%H:%M:%S")
            if hasattr(self, 'stats_start'):
                self.stats_start.configure(text=f"⏱️ Início: {start_str}")
        
        if "📊 Total Msgs:" in self.dashboard_info:
            self.dashboard_info["📊 Total Msgs:"].configure(text=str(self.stats["total_messages"]))
        if "🔌 Conexões:" in self.dashboard_info:
            self.dashboard_info["🔌 Conexões:"].configure(text=str(self.stats["total_connections"]))
        
        if self.stats["start_time"]:
            elapsed_minutes = (time.time() - self.stats["start_time"]) / 60
            if elapsed_minutes > 0:
                msgs_per_min = self.stats["total_messages"] / elapsed_minutes
                if "📨 Msg/min:" in self.dashboard_info:
                    self.dashboard_info["📨 Msg/min:"].configure(text=f"{msgs_per_min:.1f}")
    
    def update_dashboard_labels(self, cpu_percent, ram_percent, ram_used_mb, ram_total_mb):
        try:
            if hasattr(self, 'cpu_value_label'):
                self.cpu_value_label.configure(text=f"{cpu_percent:.1f}%")
                
                if cpu_percent < 50:
                    self.cpu_value_label.configure(text_color="#2ecc71")
                    if hasattr(self, 'cpu_status_label'):
                        self.cpu_status_label.configure(text="🟢 Excelente", text_color="#2ecc71")
                elif cpu_percent < 80:
                    self.cpu_value_label.configure(text_color="#f39c12")
                    if hasattr(self, 'cpu_status_label'):
                        self.cpu_status_label.configure(text="🟡 Moderado", text_color="#f39c12")
                else:
                    self.cpu_value_label.configure(text_color="#e74c3c")
                    if hasattr(self, 'cpu_status_label'):
                        self.cpu_status_label.configure(text="🔴 Alto", text_color="#e74c3c")
            
            if hasattr(self, 'ram_value_label'):
                self.ram_value_label.configure(text=f"{ram_used_mb:.0f} MB / {ram_total_mb:.0f} MB")
            if hasattr(self, 'ram_percent_label'):
                self.ram_percent_label.configure(text=f"{ram_percent:.1f}%")
                
                if ram_percent < 50:
                    self.ram_percent_label.configure(text_color="#2ecc71")
                    if hasattr(self, 'ram_status_label'):
                        self.ram_status_label.configure(text="🟢 Normal", text_color="#2ecc71")
                elif ram_percent < 80:
                    self.ram_percent_label.configure(text_color="#f39c12")
                    if hasattr(self, 'ram_status_label'):
                        self.ram_status_label.configure(text="🟡 Atenção", text_color="#f39c12")
                else:
                    self.ram_percent_label.configure(text_color="#e74c3c")
                    if hasattr(self, 'ram_status_label'):
                        self.ram_status_label.configure(text="🔴 Crítico", text_color="#e74c3c")
            
            if hasattr(self, 'cpu_avg_label'):
                self.cpu_avg_label.configure(text=f"Média: {self.stats['avg_cpu']:.1f}%")
                self.cpu_max_label.configure(text=f"Máx: {self.stats['max_cpu']:.1f}%")
                self.cpu_min_label.configure(text=f"Mín: {self.stats['min_cpu']:.1f}%")
            
            if hasattr(self, 'ram_avg_label'):
                self.ram_avg_label.configure(text=f"Média: {self.stats['avg_ram']:.0f} MB")
                self.ram_max_label.configure(text=f"Máx: {self.stats['max_ram']:.0f} MB")
                self.ram_min_label.configure(text=f"Mín: {self.stats['min_ram']:.0f} MB")
                
        except Exception as e:
            pass
    
    def update_cpu_bar(self, percent):
        if hasattr(self, 'cpu_progress'):
            self.cpu_progress.set(percent / 100)
            if percent < 50:
                self.cpu_progress.configure(progress_color="#2ecc71")
            elif percent < 80:
                self.cpu_progress.configure(progress_color="#f39c12")
            else:
                self.cpu_progress.configure(progress_color="#e74c3c")
    
    def update_ram_bar(self, percent):
        if hasattr(self, 'ram_progress'):
            self.ram_progress.set(percent / 100)
            if percent < 50:
                self.ram_progress.configure(progress_color="#2ecc71")
            elif percent < 80:
                self.ram_progress.configure(progress_color="#f39c12")
            else:
                self.ram_progress.configure(progress_color="#e74c3c")
    
    def check_bot_file(self):
        if os.path.exists(self.bot_file):
            size = os.path.getsize(self.bot_file)
            self.add_log(f"✅ chatbot.js encontrado! ({size} bytes)")
            return True
        else:
            self.add_log("❌ chatbot.js não encontrado!")
            return False
    
    def kill_processes(self):
        self.add_log("🔪 Matando processos...")
        os.system('taskkill /f /im node.exe 2>nul')
        os.system('taskkill /f /im chrome.exe 2>nul')
        time.sleep(2)
        self.add_log("✅ Processos finalizados!")
    
    def clear_session(self):
        if self.bot_running:
            self.stop_bot()
            time.sleep(2)
        
        self.kill_processes()
        time.sleep(1)
        
        for folder in [".wwebjs_auth", ".wwebjs_cache", "session"]:
            folder_path = os.path.join(self.bot_dir, folder)
            if os.path.exists(folder_path):
                try:
                    shutil.rmtree(folder_path)
                    self.add_log(f"🗑️ Pasta {folder} removida")
                except Exception as e:
                    pass
        
        if os.path.exists(self.qr_image_file):
            try:
                os.remove(self.qr_image_file)
                self.add_log("🗑️ qrcode.png removido")
            except:
                pass
        
        self.qr_ctk_image = None
        if hasattr(self, 'qr_image_label'):
            self.qr_image_label.configure(image="", text="")
            self.qr_status_label.configure(text="🔴 Sessão limpa!\nInicie o robô para gerar novo QR Code", text_color="#ff6b6b")
        
        self.add_log("✅ Sessão limpa!")
        messagebox.showinfo("Sucesso", "Sessão limpa com sucesso!")
    
    def create_widgets(self):
        # Sidebar esquerda
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(pady=30)
        
        ctk.CTkLabel(logo_frame, text="🤖", font=ctk.CTkFont(size=60)).pack()
        ctk.CTkLabel(logo_frame, text="MTECH BOT", font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(logo_frame, text="Manager Pro", font=ctk.CTkFont(size=12), text_color="gray").pack()
        
        # Status card na sidebar
        status_card = ctk.CTkFrame(self.sidebar, corner_radius=15)
        status_card.pack(fill="x", padx=15, pady=20)
        
        ctk.CTkLabel(status_card, text="STATUS", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        self.status_indicator = ctk.CTkLabel(status_card, text="🔴", font=ctk.CTkFont(size=40))
        self.status_indicator.pack(pady=5)
        
        self.status_text = ctk.CTkLabel(status_card, text="OFFLINE", font=ctk.CTkFont(size=16, weight="bold"), text_color="red")
        self.status_text.pack(pady=5)
        
        self.connection_status = ctk.CTkLabel(status_card, text="📡 Aguardando...", font=ctk.CTkFont(size=11), text_color="gray")
        self.connection_status.pack(pady=5)
        
        self.uptime_label = ctk.CTkLabel(status_card, text="Tempo: --:--:--", font=ctk.CTkFont(size=11), text_color="gray")
        self.uptime_label.pack(pady=5)
        
        # Botões da sidebar
        buttons_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=15, pady=10)
        
        self.start_btn = ctk.CTkButton(buttons_frame, text="▶️ INICIAR ROBÔ", command=self.start_bot, height=45, font=ctk.CTkFont(size=13, weight="bold"), fg_color="#2ecc71", corner_radius=10)
        self.start_btn.pack(fill="x", pady=5)
        
        self.stop_btn = ctk.CTkButton(buttons_frame, text="⏹️ PARAR ROBÔ", command=self.stop_bot, height=45, font=ctk.CTkFont(size=13, weight="bold"), fg_color="#e74c3c", state="disabled", corner_radius=10)
        self.stop_btn.pack(fill="x", pady=5)
        
        self.restart_btn = ctk.CTkButton(buttons_frame, text="🔄 REINICIAR", command=self.restart_bot, height=45, font=ctk.CTkFont(size=13, weight="bold"), fg_color="#f39c12", corner_radius=10)
        self.restart_btn.pack(fill="x", pady=5)
        
        ctk.CTkButton(buttons_frame, text="🔪 MATAR PROCESSOS", command=self.kill_processes, height=40, font=ctk.CTkFont(size=12), fg_color="#e67e22", corner_radius=10).pack(fill="x", pady=5)
        ctk.CTkButton(buttons_frame, text="🧹 LIMPAR SESSÃO", command=self.clear_session, height=40, font=ctk.CTkFont(size=12), fg_color="#9b59b6", corner_radius=10).pack(fill="x", pady=5)
        ctk.CTkButton(buttons_frame, text="🔄 RECARREGAR QR", command=self.force_reload_qr, height=40, font=ctk.CTkFont(size=12), fg_color="#3498db", corner_radius=10).pack(fill="x", pady=5)
        
        # Stats na sidebar
        stats_card = ctk.CTkFrame(self.sidebar, corner_radius=15)
        stats_card.pack(fill="x", padx=15, pady=20)
        
        ctk.CTkLabel(stats_card, text="📊 ESTATÍSTICAS", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=5)
        
        self.stats_messages = ctk.CTkLabel(stats_card, text="💬 Msgs: 0", font=ctk.CTkFont(size=12))
        self.stats_messages.pack(anchor="w", padx=15, pady=2)
        
        self.stats_connections = ctk.CTkLabel(stats_card, text="🔌 Conexões: 0", font=ctk.CTkFont(size=12))
        self.stats_connections.pack(anchor="w", padx=15, pady=2)
        
        self.stats_start = ctk.CTkLabel(stats_card, text="⏱️ Início: --:--:--", font=ctk.CTkFont(size=12))
        self.stats_start.pack(anchor="w", padx=15, pady=2)
        
        # Main area - Tabview
        self.main_area = ctk.CTkFrame(self, corner_radius=15)
        self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.tabview = ctk.CTkTabview(self.main_area, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Adicionar abas
        self.tabview.add("📱 QR CODE")
        self.tabview.add("📝 MENUS")
        self.tabview.add("📋 SUBMENUS")
        self.tabview.add("💬 MENSAGENS")
        self.tabview.add("💰 PREÇOS")
        self.tabview.add("🔗 LINKS")
        self.tabview.add("💳 RECARGAS")
        self.tabview.add("⚙️ CONFIG")
        self.tabview.add("📊 DASHBOARD")
        self.tabview.add("📋 CONSOLE")
        
        self.create_qrcode_tab()
        self.create_menus_tab()
        self.create_submenus_tab()
        self.create_messages_tab()
        self.create_prices_tab()
        self.create_links_tab()
        self.create_recargas_tab()
        self.create_config_tab()
        self.create_dashboard_tab()
        self.create_console_tab()
        
        self.create_status_bar()
    
    def create_qrcode_tab(self):
        tab = self.tabview.tab("📱 QR CODE")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        container = ctk.CTkFrame(tab)
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        ctk.CTkLabel(container, text="📱 ESCANEIE O QR CODE", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=20)
        
        qr_frame = ctk.CTkFrame(container, corner_radius=20, fg_color="#1e1e1e")
        qr_frame.pack(expand=True, fill="both", padx=40, pady=20)
        
        self.qr_image_label = ctk.CTkLabel(qr_frame, text="")
        self.qr_image_label.pack(expand=True, pady=30)
        
        self.qr_status_label = ctk.CTkLabel(
            qr_frame, 
            text="🔴 Aguardando QR Code...\n\nClique em INICIAR ROBÔ na barra lateral",
            font=ctk.CTkFont(size=16),
            text_color="#ff6b6b"
        )
        self.qr_status_label.pack(pady=20)
        
        ctk.CTkLabel(
            qr_frame, 
            text="💡 Abra o WhatsApp > Configurações > Dispositivos Conectados > Conectar um dispositivo",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=10)
    
    def create_menus_tab(self):
        tab = self.tabview.tab("📝 MENUS")
        
        menus_notebook = ctk.CTkTabview(tab)
        menus_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        menus_list = [
            ("📱 Principal", "principal", "menuPrincipal"),
            ("📺 IPTV", "iptv", "menuIPTV"),
            ("🌐 Internet", "internet", "menuInternet"),
            ("📱 Recargas", "recargas", "menuRecargas"),
            ("📋 Consultas", "consultas", "menuConsultas"),
            ("❓ Ajuda", "ajuda", "menuAjuda"),
            ("⚙️ Configurações", "configuracoes", "menuConfiguracoes"),
            ("📜 Termos", "termos", "menuTermos")
        ]
        
        self.menu_texts = {}
        
        for menu_name, menu_key, js_var in menus_list:
            menus_notebook.add(menu_name)
            frame = menus_notebook.tab(menu_name)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            
            toolbar = ctk.CTkFrame(frame, height=45)
            toolbar.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
            
            ctk.CTkLabel(toolbar, text=f"✏️ Editor do Menu {menu_name}", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=15)
            ctk.CTkLabel(toolbar, text=f"(Variável: {js_var})", font=ctk.CTkFont(size=10), text_color="gray").pack(side="left", padx=10)
            
            text_area = scrolledtext.ScrolledText(frame, font=("Consolas", 12), bg="#1e1e1e", fg="#d4d4d4", wrap=tk.WORD)
            text_area.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
            
            content = self.bot_config["menus"].get(menu_key, "")
            if content:
                text_area.insert("1.0", content)
                print(f"✅ Menu {menu_name} carregado ({len(content)} caracteres)")
            else:
                text_area.insert("1.0", f"*MENU {menu_name.upper()}*\n\nDigite o número da opção desejada...")
                print(f"⚠️ Menu {menu_name} não encontrado, usando padrão")
            
            self.menu_texts[menu_key] = text_area
        
        save_frame = ctk.CTkFrame(tab)
        save_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(save_frame, text="💾 SALVAR TODOS OS MENUS", command=self.save_all_menus, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", corner_radius=10).pack(pady=10)
    
    def create_submenus_tab(self):
        tab = self.tabview.tab("📋 SUBMENUS")
        
        container = ctk.CTkScrollableFrame(tab)
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Submenu IPTV
        iptv_card = ctk.CTkFrame(container, corner_radius=15)
        iptv_card.pack(fill="x", pady=10)
        ctk.CTkLabel(iptv_card, text="📺 SUBMENU IPTV (Opções 1-20)", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.submenu_iptv_text = scrolledtext.ScrolledText(iptv_card, height=15, font=("Consolas", 11))
        self.submenu_iptv_text.pack(fill="x", padx=15, pady=10)
        
        if "iptv" in self.bot_config["menus"]:
            self.submenu_iptv_text.insert("1.0", self.bot_config["menus"]["iptv"])
        
        # Submenu Internet
        internet_card = ctk.CTkFrame(container, corner_radius=15)
        internet_card.pack(fill="x", pady=10)
        ctk.CTkLabel(internet_card, text="🌐 SUBMENU INTERNET (Opções 21-35)", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.submenu_internet_text = scrolledtext.ScrolledText(internet_card, height=12, font=("Consolas", 11))
        self.submenu_internet_text.pack(fill="x", padx=15, pady=10)
        
        if "internet" in self.bot_config["menus"]:
            self.submenu_internet_text.insert("1.0", self.bot_config["menus"]["internet"])
        
        # Submenu Recargas
        recargas_card = ctk.CTkFrame(container, corner_radius=15)
        recargas_card.pack(fill="x", pady=10)
        ctk.CTkLabel(recargas_card, text="📱 SUBMENU RECARGAS (Opções 36-50)", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        self.submenu_recargas_text = scrolledtext.ScrolledText(recargas_card, height=12, font=("Consolas", 11))
        self.submenu_recargas_text.pack(fill="x", padx=15, pady=10)
        
        if "recargas" in self.bot_config["menus"]:
            self.submenu_recargas_text.insert("1.0", self.bot_config["menus"]["recargas"])
        
        save_btn = ctk.CTkButton(container, text="💾 SALVAR TODOS OS SUBMENUS", command=self.save_all_submenus, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", corner_radius=10)
        save_btn.pack(pady=20)
    
    def create_messages_tab(self):
        tab = self.tabview.tab("💬 MENSAGENS")
        
        msg_container = ctk.CTkScrollableFrame(tab)
        msg_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Boas Vindas
        welcome_card = ctk.CTkFrame(msg_container, corner_radius=15)
        welcome_card.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(welcome_card, text="🎉 BOAS VINDAS (uma por linha)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=10)
        self.boas_vindas_text = scrolledtext.ScrolledText(welcome_card, height=6, font=("Consolas", 12))
        self.boas_vindas_text.pack(fill="x", padx=20, pady=10)
        self.boas_vindas_text.insert("1.0", "\n".join(self.bot_config["mensagens"]["boas_vindas"]))
        
        # Agradecimentos
        thanks_card = ctk.CTkFrame(msg_container, corner_radius=15)
        thanks_card.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(thanks_card, text="🙏 AGRADECIMENTOS (uma por linha)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=10)
        self.agradecimento_text = scrolledtext.ScrolledText(thanks_card, height=4, font=("Consolas", 12))
        self.agradecimento_text.pack(fill="x", padx=20, pady=10)
        self.agradecimento_text.insert("1.0", "\n".join(self.bot_config["mensagens"]["agradecimento"]))
        
        # Despedidas
        goodbye_card = ctk.CTkFrame(msg_container, corner_radius=15)
        goodbye_card.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(goodbye_card, text="👋 DESPEDIDAS (uma por linha)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=10)
        self.despedida_text = scrolledtext.ScrolledText(goodbye_card, height=4, font=("Consolas", 12))
        self.despedida_text.pack(fill="x", padx=20, pady=10)
        self.despedida_text.insert("1.0", "\n".join(self.bot_config["mensagens"]["despedida"]))
        
        # Não Entendi
        not_understood_card = ctk.CTkFrame(msg_container, corner_radius=15)
        not_understood_card.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(not_understood_card, text="🤔 NÃO ENTENDI (uma por linha)", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=10)
        self.nao_entendi_text = scrolledtext.ScrolledText(not_understood_card, height=4, font=("Consolas", 12))
        self.nao_entendi_text.pack(fill="x", padx=20, pady=10)
        self.nao_entendi_text.insert("1.0", "\n".join(self.bot_config["mensagens"]["nao_entendi"]))
        
        save_msgs_btn = ctk.CTkButton(msg_container, text="💾 SALVAR MENSAGENS", command=self.save_messages, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", corner_radius=10)
        save_msgs_btn.pack(pady=20)
    
    def create_prices_tab(self):
        tab = self.tabview.tab("💰 PREÇOS")
        
        prices_container = ctk.CTkFrame(tab)
        prices_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # IPTV Card
        iptv_card = ctk.CTkFrame(prices_container, corner_radius=15)
        iptv_card.pack(fill="x", pady=10)
        ctk.CTkLabel(iptv_card, text="📺 IPTV STAR PLAY", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        self.iptv_prices = {}
        iptv_grid = ctk.CTkFrame(iptv_card)
        iptv_grid.pack(pady=10)
        
        planos_iptv = [("1 Mês", "1_mes"), ("3 Meses", "3_meses"), ("6 Meses", "6_meses"), ("12 Meses", "12_meses")]
        for plano, key in planos_iptv:
            row = ctk.CTkFrame(iptv_grid)
            row.pack(fill="x", pady=8, padx=20)
            ctk.CTkLabel(row, text=plano, width=120, font=ctk.CTkFont(size=16)).pack(side="left", padx=20)
            ctk.CTkLabel(row, text="R$", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            entry = ctk.CTkEntry(row, width=120, font=ctk.CTkFont(size=16))
            entry.insert(0, self.bot_config["planos_iptv"].get(key, "29,90").replace("R$ ", "").replace(",", "."))
            entry.pack(side="left", padx=10)
            self.iptv_prices[key] = entry
        
        # Internet Card
        internet_card = ctk.CTkFrame(prices_container, corner_radius=15)
        internet_card.pack(fill="x", pady=10)
        ctk.CTkLabel(internet_card, text="🌐 INTERNET ILIMITADA", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=15)
        
        self.internet_prices = {}
        internet_grid = ctk.CTkFrame(internet_card)
        internet_grid.pack(pady=10)
        
        planos_internet = [("1 Mês", "1_mes"), ("3 Meses", "3_meses"), ("6 Meses", "6_meses"), ("12 Meses", "12_meses")]
        for plano, key in planos_internet:
            row = ctk.CTkFrame(internet_grid)
            row.pack(fill="x", pady=8, padx=20)
            ctk.CTkLabel(row, text=plano, width=120, font=ctk.CTkFont(size=16)).pack(side="left", padx=20)
            ctk.CTkLabel(row, text="R$", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            entry = ctk.CTkEntry(row, width=120, font=ctk.CTkFont(size=16))
            entry.insert(0, self.bot_config["planos_internet"].get(key, "49,90").replace("R$ ", "").replace(",", "."))
            entry.pack(side="left", padx=10)
            self.internet_prices[key] = entry
        
        save_prices_btn = ctk.CTkButton(prices_container, text="💾 SALVAR PREÇOS", command=self.save_prices, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", corner_radius=10)
        save_prices_btn.pack(pady=20)
    
    def create_links_tab(self):
        tab = self.tabview.tab("🔗 LINKS")
        
        links_container = ctk.CTkScrollableFrame(tab)
        links_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        iptv_card = ctk.CTkFrame(links_container, corner_radius=15)
        iptv_card.pack(fill="x", padx=10, pady=10)
        
        title_frame = ctk.CTkFrame(iptv_card)
        title_frame.pack(fill="x", pady=10, padx=15)
        ctk.CTkLabel(title_frame, text="🔗 LINKS DOS TESTES IPTV", font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        
        reload_btn = ctk.CTkButton(title_frame, text="🔄 RECARREGAR", command=self.reload_links, width=100, height=30, fg_color="#3498db")
        reload_btn.pack(side="right", padx=10)
        
        testes_desc = {
            "1": "🔴 TESTE 1 HORA (Completo)",
            "2": "🔴 TESTE 1 HORA (User/Senha)",
            "3": "⚽ TESTE 1 HORA (Futebol/Lutas)",
            "4": "🟠 TESTE 2 HORAS",
            "5": "🟢 TESTE 4 HORAS",
            "6": "🔵 TESTE 6 HORAS (IBO MAC)",
            "7": "🟣 12H SEM ADULTOS",
            "8": "📺 12H SAMSUNG",
            "9": "📺 12H LG",
            "10": "📱 12H ANDROID",
            "11": "📱 12H IPHONE",
            "12": "📦 12H TV BOX",
            "13": "💻 12H PC/NOTEBOOK",
            "14": "🎮 12H ROKU TV",
            "15": "🔥 12H FIRE STICK"
        }
        
        self.link_entries = {}
        
        for i in range(1, 16):
            num = str(i)
            frame = ctk.CTkFrame(iptv_card, corner_radius=8, fg_color="#2d2d2d")
            frame.pack(fill="x", pady=5, padx=15)
            
            desc_label = ctk.CTkLabel(frame, text=testes_desc.get(num, f"Teste {i}:"), width=200, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
            desc_label.pack(side="left", padx=10, pady=8)
            
            entry = ctk.CTkEntry(frame, width=650, font=ctk.CTkFont(size=11))
            link_value = self.bot_config["links_iptv"].get(num, "")
            entry.insert(0, link_value)
            entry.pack(side="left", padx=10, fill="x", expand=True, pady=8)
            
            if link_value:
                status_label = ctk.CTkLabel(frame, text="✅", width=30, text_color="#2ecc71")
            else:
                status_label = ctk.CTkLabel(frame, text="❌", width=30, text_color="#e74c3c")
            status_label.pack(side="right", padx=10)
            
            self.link_entries[num] = {"entry": entry, "status": status_label, "desc": testes_desc.get(num, f"Teste {i}")}
        
        buttons_frame = ctk.CTkFrame(iptv_card)
        buttons_frame.pack(fill="x", pady=15, padx=15)
        
        save_links_btn = ctk.CTkButton(buttons_frame, text="💾 SALVAR TODOS OS LINKS", command=self.save_links, height=45, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", corner_radius=10)
        save_links_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        test_links_btn = ctk.CTkButton(buttons_frame, text="🔍 VERIFICAR LINKS", command=self.check_links, height=45, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#f39c12", corner_radius=10)
        test_links_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        info_label = ctk.CTkLabel(iptv_card, text="ℹ️ Cada link corresponde a um tipo de teste diferente. Links em branco serão ignorados.", font=ctk.CTkFont(size=11), text_color="gray")
        info_label.pack(pady=10)
    
    def create_recargas_tab(self):
        """Aba para configurar valores de recargas com PAGA e RECEBE"""
        tab = self.tabview.tab("💳 RECARGAS")
        
        container = ctk.CTkScrollableFrame(tab)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_frame = ctk.CTkFrame(container)
        title_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(title_frame, text="💳 CONFIGURAÇÃO DE RECARGAS", font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(title_frame, text="Configure quanto o cliente PAGA e quanto RECEBE em créditos", font=ctk.CTkFont(size=12), text_color="gray").pack()
        
        # Card VIVO
        vivo_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e2e")
        vivo_card.pack(fill="x", pady=10)
        ctk.CTkLabel(vivo_card, text="📱 VIVO", font=ctk.CTkFont(size=18, weight="bold"), text_color="#2ecc71").pack(pady=10)
        
        self.vivo_entries = {}
        valores = ["10", "20", "30", "50", "100"]
        
        for valor in valores:
            frame = ctk.CTkFrame(vivo_card)
            frame.pack(fill="x", pady=5, padx=20)
            
            ctk.CTkLabel(frame, text=f"R$ {valor},00", width=80, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
            
            ctk.CTkLabel(frame, text="Paga:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            paga_entry = ctk.CTkEntry(frame, width=100, font=ctk.CTkFont(size=13))
            paga_entry.insert(0, str(self.recargas_config["vivo"][valor]["paga"]))
            paga_entry.pack(side="left", padx=5)
            
            ctk.CTkLabel(frame, text="Recebe:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            recebe_entry = ctk.CTkEntry(frame, width=100, font=ctk.CTkFont(size=13))
            recebe_entry.insert(0, str(self.recargas_config["vivo"][valor]["recebe"]))
            recebe_entry.pack(side="left", padx=5)
            
            self.vivo_entries[valor] = {"paga": paga_entry, "recebe": recebe_entry}
        
        # Card TIM
        tim_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e2e")
        tim_card.pack(fill="x", pady=10)
        ctk.CTkLabel(tim_card, text="📱 TIM", font=ctk.CTkFont(size=18, weight="bold"), text_color="#3498db").pack(pady=10)
        
        self.tim_entries = {}
        for valor in valores:
            frame = ctk.CTkFrame(tim_card)
            frame.pack(fill="x", pady=5, padx=20)
            
            ctk.CTkLabel(frame, text=f"R$ {valor},00", width=80, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
            
            ctk.CTkLabel(frame, text="Paga:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            paga_entry = ctk.CTkEntry(frame, width=100, font=ctk.CTkFont(size=13))
            paga_entry.insert(0, str(self.recargas_config["tim"][valor]["paga"]))
            paga_entry.pack(side="left", padx=5)
            
            ctk.CTkLabel(frame, text="Recebe:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            recebe_entry = ctk.CTkEntry(frame, width=100, font=ctk.CTkFont(size=13))
            recebe_entry.insert(0, str(self.recargas_config["tim"][valor]["recebe"]))
            recebe_entry.pack(side="left", padx=5)
            
            self.tim_entries[valor] = {"paga": paga_entry, "recebe": recebe_entry}
        
        # Card CLARO
        claro_card = ctk.CTkFrame(container, corner_radius=15, fg_color="#1e1e2e")
        claro_card.pack(fill="x", pady=10)
        ctk.CTkLabel(claro_card, text="📱 CLARO", font=ctk.CTkFont(size=18, weight="bold"), text_color="#e74c3c").pack(pady=10)
        
        self.claro_entries = {}
        for valor in valores:
            frame = ctk.CTkFrame(claro_card)
            frame.pack(fill="x", pady=5, padx=20)
            
            ctk.CTkLabel(frame, text=f"R$ {valor},00", width=80, font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)
            
            ctk.CTkLabel(frame, text="Paga:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            paga_entry = ctk.CTkEntry(frame, width=100, font=ctk.CTkFont(size=13))
            paga_entry.insert(0, str(self.recargas_config["claro"][valor]["paga"]))
            paga_entry.pack(side="left", padx=5)
            
            ctk.CTkLabel(frame, text="Recebe:", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
            recebe_entry = ctk.CTkEntry(frame, width=100, font=ctk.CTkFont(size=13))
            recebe_entry.insert(0, str(self.recargas_config["claro"][valor]["recebe"]))
            recebe_entry.pack(side="left", padx=5)
            
            self.claro_entries[valor] = {"paga": paga_entry, "recebe": recebe_entry}
        
        # Link de pagamento
        link_card = ctk.CTkFrame(container, corner_radius=15)
        link_card.pack(fill="x", pady=10)
        ctk.CTkLabel(link_card, text="🔗 LINK DE PAGAMENTO", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        self.link_pagamento_entry = ctk.CTkEntry(link_card, width=600, font=ctk.CTkFont(size=13), placeholder_text="https://payment.mtech.com.br/recarga")
        self.link_pagamento_entry.pack(pady=10, padx=20)
        self.link_pagamento_entry.insert(0, "https://payment.mtech.com.br/recarga")
        
        # Botões
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=20)
        
        save_recargas_btn = ctk.CTkButton(button_frame, text="💾 SALVAR CONFIGURAÇÕES", command=self.save_recargas_config, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#2ecc71", corner_radius=10)
        save_recargas_btn.pack(side="left", padx=10, expand=True, fill="x")
        
        reset_recargas_btn = ctk.CTkButton(button_frame, text="🔄 REDEFINIR PADRÃO", command=self.reset_recargas_default, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color="#e67e22", corner_radius=10)
        reset_recargas_btn.pack(side="left", padx=10, expand=True, fill="x")
    
    def reset_recargas_default(self):
        """Redefinir valores padrão das recargas"""
        if messagebox.askyesno("Confirmar", "Redefinir todos os valores de recarga para o padrão (paga = recebe)?"):
            for valor in self.vivo_entries:
                self.vivo_entries[valor]["paga"].delete(0, tk.END)
                self.vivo_entries[valor]["paga"].insert(0, valor)
                self.vivo_entries[valor]["recebe"].delete(0, tk.END)
                self.vivo_entries[valor]["recebe"].insert(0, valor)
            
            for valor in self.tim_entries:
                self.tim_entries[valor]["paga"].delete(0, tk.END)
                self.tim_entries[valor]["paga"].insert(0, valor)
                self.tim_entries[valor]["recebe"].delete(0, tk.END)
                self.tim_entries[valor]["recebe"].insert(0, valor)
            
            for valor in self.claro_entries:
                self.claro_entries[valor]["paga"].delete(0, tk.END)
                self.claro_entries[valor]["paga"].insert(0, valor)
                self.claro_entries[valor]["recebe"].delete(0, tk.END)
                self.claro_entries[valor]["recebe"].insert(0, valor)
            
            self.add_log("🔄 Valores de recarga redefinidos para o padrão")
            messagebox.showinfo("Sucesso", "Valores redefinidos para o padrão!")
    
    def create_config_tab(self):
        tab = self.tabview.tab("⚙️ CONFIG")
        
        config_container = ctk.CTkScrollableFrame(tab)
        config_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Proprietário
        owner_card = ctk.CTkFrame(config_container, corner_radius=15)
        owner_card.pack(fill="x", pady=10)
        ctk.CTkLabel(owner_card, text="👤 PROPRIETÁRIO", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        owner_frame = ctk.CTkFrame(owner_card)
        owner_frame.pack(pady=10)
        ctk.CTkLabel(owner_frame, text="Número do WhatsApp:", font=ctk.CTkFont(size=14)).pack(side="left", padx=15)
        self.owner_entry = ctk.CTkEntry(owner_frame, width=250, font=ctk.CTkFont(size=14))
        self.owner_entry.insert(0, self.bot_config["proprietario"])
        self.owner_entry.pack(side="left", padx=10)
        ctk.CTkButton(owner_frame, text="💾 SALVAR", command=self.save_owner_number, height=35, fg_color="#3498db", corner_radius=8).pack(side="left", padx=10)
        
        # Configurações do Bot
        bot_config_card = ctk.CTkFrame(config_container, corner_radius=15)
        bot_config_card.pack(fill="x", pady=10)
        ctk.CTkLabel(bot_config_card, text="⚙️ CONFIGURAÇÕES DO BOT", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        config_frame = ctk.CTkFrame(bot_config_card)
        config_frame.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(config_frame, text="Tempo de Pausa (minutos):", font=ctk.CTkFont(size=13)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.pausa_entry = ctk.CTkEntry(config_frame, width=100)
        self.pausa_entry.insert(0, str(self.bot_config["configuracoes"]["tempo_pausa"]))
        self.pausa_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(config_frame, text="Limite de Testes:", font=ctk.CTkFont(size=13)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.limite_testes_entry = ctk.CTkEntry(config_frame, width=100)
        self.limite_testes_entry.insert(0, str(self.bot_config["configuracoes"]["limite_testes"]))
        self.limite_testes_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(config_frame, text="Antiflood (segundos):", font=ctk.CTkFont(size=13)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.antiflood_entry = ctk.CTkEntry(config_frame, width=100)
        self.antiflood_entry.insert(0, str(self.bot_config["configuracoes"]["antiflood"]))
        self.antiflood_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkButton(config_frame, text="💾 SALVAR CONFIGURAÇÕES", command=self.save_bot_config, height=40, fg_color="#3498db", corner_radius=10).grid(row=3, column=0, columnspan=2, pady=15)
        
        # Backup
        backup_card = ctk.CTkFrame(config_container, corner_radius=15)
        backup_card.pack(fill="x", pady=10)
        ctk.CTkLabel(backup_card, text="📦 BACKUP", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        backup_frame = ctk.CTkFrame(backup_card)
        backup_frame.pack(fill="x", pady=10, padx=20)
        backup_frame.grid_columnconfigure(0, weight=1)
        backup_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(backup_frame, text="📦 CRIAR BACKUP", command=self.create_backup, height=45, fg_color="#3498db", corner_radius=10).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(backup_frame, text="🔄 RESTAURAR BACKUP", command=self.restore_backup, height=45, fg_color="#e67e22", corner_radius=10).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Limpeza
        clear_card = ctk.CTkFrame(config_container, corner_radius=15)
        clear_card.pack(fill="x", pady=10)
        ctk.CTkLabel(clear_card, text="🗑️ LIMPEZA", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)
        
        ctk.CTkButton(clear_card, text="🧹 LIMPAR DADOS DE TESTES", command=self.clear_test_data, height=45, fg_color="#e74c3c", corner_radius=10).pack(pady=10, padx=20, fill="x")
    
    def create_dashboard_tab(self):
        """Aba de Dashboard com gráficos e estatísticas em TEMPO REAL"""
        tab = self.tabview.tab("📊 DASHBOARD")
        
        dashboard_container = ctk.CTkScrollableFrame(tab)
        dashboard_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_frame = ctk.CTkFrame(dashboard_container)
        title_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(title_frame, text="📈 DASHBOARD EM TEMPO REAL", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        self.real_time_indicator = ctk.CTkLabel(title_frame, text="🟢 LIVE", font=ctk.CTkFont(size=12, weight="bold"), text_color="#2ecc71")
        self.real_time_indicator.pack(side="left", padx=15)
        
        # Card de Métricas do Sistema
        metrics_frame = ctk.CTkFrame(dashboard_container, corner_radius=15)
        metrics_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(metrics_frame, text="🖥️ MÉTRICAS DO SISTEMA", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Grid de métricas
        grid_frame = ctk.CTkFrame(metrics_frame)
        grid_frame.pack(fill="x", padx=15, pady=10)
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        
        # Card CPU
        cpu_card = ctk.CTkFrame(grid_frame, corner_radius=12, fg_color="#1e1e2e")
        cpu_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(cpu_card, text="🖥️ PROCESSADOR (CPU)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=8)
        
        self.cpu_value_label = ctk.CTkLabel(cpu_card, text="0%", font=ctk.CTkFont(size=36, weight="bold"))
        self.cpu_value_label.pack(pady=5)
        
        self.cpu_progress = ctk.CTkProgressBar(cpu_card, width=250, height=15, corner_radius=7)
        self.cpu_progress.pack(pady=5)
        self.cpu_progress.set(0)
        
        stats_frame = ctk.CTkFrame(cpu_card, fg_color="transparent")
        stats_frame.pack(pady=8)
        self.cpu_status_label = ctk.CTkLabel(stats_frame, text="🟢 Excelente", font=ctk.CTkFont(size=11))
        self.cpu_status_label.pack(side="left", padx=5)
        
        stats_row = ctk.CTkFrame(cpu_card, fg_color="transparent")
        stats_row.pack(pady=5)
        self.cpu_avg_label = ctk.CTkLabel(stats_row, text="Média: --%", font=ctk.CTkFont(size=10), text_color="gray")
        self.cpu_avg_label.pack(side="left", padx=5)
        self.cpu_max_label = ctk.CTkLabel(stats_row, text="Máx: --%", font=ctk.CTkFont(size=10), text_color="gray")
        self.cpu_max_label.pack(side="left", padx=5)
        self.cpu_min_label = ctk.CTkLabel(stats_row, text="Mín: --%", font=ctk.CTkFont(size=10), text_color="gray")
        self.cpu_min_label.pack(side="left", padx=5)
        
        # Card RAM
        ram_card = ctk.CTkFrame(grid_frame, corner_radius=12, fg_color="#1e1e2e")
        ram_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(ram_card, text="💾 MEMÓRIA RAM", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=8)
        
        self.ram_value_label = ctk.CTkLabel(ram_card, text="0 MB / 0 MB", font=ctk.CTkFont(size=16, weight="bold"))
        self.ram_value_label.pack(pady=5)
        
        self.ram_percent_label = ctk.CTkLabel(ram_card, text="0%", font=ctk.CTkFont(size=24, weight="bold"))
        self.ram_percent_label.pack(pady=5)
        
        self.ram_progress = ctk.CTkProgressBar(ram_card, width=250, height=15, corner_radius=7)
        self.ram_progress.pack(pady=5)
        self.ram_progress.set(0)
        
        ram_stats_frame = ctk.CTkFrame(ram_card, fg_color="transparent")
        ram_stats_frame.pack(pady=8)
        self.ram_status_label = ctk.CTkLabel(ram_stats_frame, text="🟢 Normal", font=ctk.CTkFont(size=11))
        self.ram_status_label.pack(side="left", padx=5)
        
        ram_stats_row = ctk.CTkFrame(ram_card, fg_color="transparent")
        ram_stats_row.pack(pady=5)
        self.ram_avg_label = ctk.CTkLabel(ram_stats_row, text="Média: -- MB", font=ctk.CTkFont(size=10), text_color="gray")
        self.ram_avg_label.pack(side="left", padx=5)
        self.ram_max_label = ctk.CTkLabel(ram_stats_row, text="Máx: -- MB", font=ctk.CTkFont(size=10), text_color="gray")
        self.ram_max_label.pack(side="left", padx=5)
        self.ram_min_label = ctk.CTkLabel(ram_stats_row, text="Mín: -- MB", font=ctk.CTkFont(size=10), text_color="gray")
        self.ram_min_label.pack(side="left", padx=5)
        
        # Card de Informações do Bot
        bot_info_card = ctk.CTkFrame(dashboard_container, corner_radius=15)
        bot_info_card.pack(fill="x", pady=10)
        ctk.CTkLabel(bot_info_card, text="🤖 STATUS DO BOT", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        info_grid = ctk.CTkFrame(bot_info_card)
        info_grid.pack(fill="x", padx=15, pady=10)
        info_grid.grid_columnconfigure(0, weight=1)
        info_grid.grid_columnconfigure(1, weight=1)
        info_grid.grid_columnconfigure(2, weight=1)
        
        # Linha 1
        info_items_row1 = [
            ("📄 Arquivo:", "chatbot.js"),
            ("👤 Proprietário:", self.bot_config["proprietario"]),
            ("💾 Backup:", "Disponível")
        ]
        
        for i, (label, value) in enumerate(info_items_row1):
            frame = ctk.CTkFrame(info_grid, corner_radius=8, fg_color="#1e1e2e")
            frame.grid(row=0, column=i, padx=8, pady=5, sticky="nsew")
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=10, pady=3)
            val_label = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=12))
            val_label.pack(anchor="w", padx=10, pady=3)
            self.dashboard_info[label] = val_label
        
        # Linha 2
        info_items_row2 = [
            ("📊 Total Msgs:", "0"),
            ("🔌 Conexões:", "0"),
            ("⏱️ Uptime:", "--:--:--")
        ]
        
        for i, (label, value) in enumerate(info_items_row2):
            frame = ctk.CTkFrame(info_grid, corner_radius=8, fg_color="#1e1e2e")
            frame.grid(row=1, column=i, padx=8, pady=5, sticky="nsew")
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=10, pady=3)
            val_label = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=12))
            val_label.pack(anchor="w", padx=10, pady=3)
            self.dashboard_info[label] = val_label
        
        # Linha 3
        info_items_row3 = [
            ("🟢 Node.js:", "Aguardando"),
            ("📱 WhatsApp:", "Desconectado"),
            ("📨 Msg/min:", "0")
        ]
        
        for i, (label, value) in enumerate(info_items_row3):
            frame = ctk.CTkFrame(info_grid, corner_radius=8, fg_color="#1e1e2e")
            frame.grid(row=2, column=i, padx=8, pady=5, sticky="nsew")
            ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=10, pady=3)
            val_label = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=12))
            val_label.pack(anchor="w", padx=10, pady=3)
            self.dashboard_info[label] = val_label
        
        self.uptime_dash_label = self.dashboard_info.get("⏱️ Uptime:", None)
        self.node_status_label = self.dashboard_info.get("🟢 Node.js:", None)
        self.messages_per_minute_label = self.dashboard_info.get("📨 Msg/min:", None)
        
        # Botão para atualização manual
        button_frame = ctk.CTkFrame(dashboard_container)
        button_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(button_frame, text="🔄 ATUALIZAR MANUALMENTE", command=self.manual_dashboard_update, height=40, font=ctk.CTkFont(size=13), fg_color="#3498db", corner_radius=10).pack(side="left", padx=5, expand=True, fill="x")
        
        info_text = ctk.CTkLabel(button_frame, text="⏱️ Atualização automática a cada 1 segundo", font=ctk.CTkFont(size=11), text_color="gray")
        info_text.pack(side="right", padx=10)
    
    def manual_dashboard_update(self):
        self.update_dashboard_real_time()
        self.add_log("📊 Dashboard atualizado manualmente")
        messagebox.showinfo("Atualizado", "Dashboard atualizado!")
    
    def create_console_tab(self):
        tab = self.tabview.tab("📋 CONSOLE")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        toolbar = ctk.CTkFrame(tab, height=50)
        toolbar.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(toolbar, text="🧹 LIMPAR", command=self.clear_console, width=120, height=35, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="💾 SALVAR LOG", command=self.save_log, width=120, height=35, corner_radius=8).pack(side="left", padx=5)
        ctk.CTkButton(toolbar, text="📋 COPIAR", command=self.copy_log, width=120, height=35, corner_radius=8).pack(side="left", padx=5)
        
        self.log_text = scrolledtext.ScrolledText(tab, font=("Consolas", 11), bg="#1e1e1e", fg="#d4d4d4")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_status_bar(self):
        self.status_bar = ctk.CTkFrame(self.main_area, height=40, corner_radius=8)
        self.status_bar.pack(fill="x", side="bottom", padx=10, pady=10)
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="✅ Sistema pronto | Clique em INICIAR ROBÔ", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=15)
        
        self.time_label = ctk.CTkLabel(self.status_bar, text=datetime.now().strftime("%H:%M:%S"), font=ctk.CTkFont(size=12))
        self.time_label.pack(side="right", padx=15)
        
        self.update_clock()
    
    def update_clock(self):
        self.time_label.configure(text=datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)
    
    def update_bot_status(self, is_connected):
        self.bot_connected = is_connected
        
        if self.bot_running:
            if is_connected:
                self.status_indicator.configure(text="🟢")
                self.status_text.configure(text="CONECTADO", text_color="#2ecc71")
                self.connection_status.configure(text="✅ WhatsApp Conectado", text_color="#2ecc71")
                self.status_label.configure(text="🟢 WhatsApp conectado!")
                if "📱 WhatsApp:" in self.dashboard_info:
                    self.dashboard_info["📱 WhatsApp:"].configure(text="✅ Conectado", text_color="#2ecc71")
                if "🟢 Node.js:" in self.dashboard_info:
                    self.dashboard_info["🟢 Node.js:"].configure(text="🟢 Ativo", text_color="#2ecc71")
            else:
                self.status_indicator.configure(text="🟡")
                self.status_text.configure(text="AGUARDANDO", text_color="#f39c12")
                self.connection_status.configure(text="⏳ Aguardando conexão...", text_color="#f39c12")
                self.status_label.configure(text="🟡 Aguardando conexão do WhatsApp...")
                if "📱 WhatsApp:" in self.dashboard_info:
                    self.dashboard_info["📱 WhatsApp:"].configure(text="⏳ Aguardando", text_color="#f39c12")
        else:
            self.status_indicator.configure(text="🔴")
            self.status_text.configure(text="OFFLINE", text_color="red")
            self.connection_status.configure(text="📡 Desconectado", text_color="gray")
            self.status_label.configure(text="⚫ Robô desligado")
            if "📱 WhatsApp:" in self.dashboard_info:
                self.dashboard_info["📱 WhatsApp:"].configure(text="🔴 Desconectado", text_color="#e74c3c")
            if "🟢 Node.js:" in self.dashboard_info:
                self.dashboard_info["🟢 Node.js:"].configure(text="🔴 Parado", text_color="#e74c3c")
    
    def reload_links(self):
        self.add_log("🔄 Recarregando links do chatbot.js...")
        self.load_full_bot_config()
        
        for num, data in self.link_entries.items():
            link_value = self.bot_config["links_iptv"].get(num, "")
            data["entry"].delete(0, tk.END)
            data["entry"].insert(0, link_value)
            if link_value:
                data["status"].configure(text="✅", text_color="#2ecc71")
            else:
                data["status"].configure(text="❌", text_color="#e74c3c")
        
        self.add_log("✅ Links recarregados!")
        messagebox.showinfo("Sucesso", "Links recarregados com sucesso!")
    
    def check_links(self):
        total = 0
        preenchidos = 0
        
        for num, data in self.link_entries.items():
            link = data["entry"].get().strip()
            total += 1
            if link:
                preenchidos += 1
                data["status"].configure(text="✅", text_color="#2ecc71")
            else:
                data["status"].configure(text="❌", text_color="#e74c3c")
        
        self.add_log(f"📊 Links: {preenchidos}/{total} preenchidos")
        messagebox.showinfo("Verificação", f"Links preenchidos: {preenchidos}/{total}\n\nOs links em branco serão ignorados pelo sistema.")
    
    def copy_log(self):
        log_content = self.log_text.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(log_content)
        self.add_log("📋 Log copiado para área de transferência!")
        messagebox.showinfo("Copiado", "Log copiado para área de transferência!")
    
    def clear_test_data(self):
        if messagebox.askyesno("Confirmar", "Limpar todos os dados de testes e bloqueios?"):
            for file in ["testes_realizados.json", "bloqueados_ligacoes.json"]:
                file_path = os.path.join(self.bot_dir, file)
                if os.path.exists(file_path):
                    os.remove(file_path)
            self.add_log("🗑️ Dados de testes e bloqueios limpos!")
            messagebox.showinfo("Sucesso", "Dados limpos com sucesso!")
    
    def add_log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        print(log_entry)
    
    def clear_console(self):
        self.log_text.delete(1.0, tk.END)
        self.add_log("📋 Console limpo")
    
    def save_log(self):
        filename = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.log_text.get(1.0, tk.END))
        self.add_log(f"💾 Log salvo como {filename}")
        messagebox.showinfo("Salvo", f"Log salvo como {filename}")
    
    def force_reload_qr(self):
        self.add_log("🔄 Forçando recarregamento do QR Code...")
        if os.path.exists(self.qr_image_file):
            self.load_qr_image()
        else:
            self.qr_status_label.configure(text="🔴 Nenhum QR Code encontrado.\nInicie o robô e aguarde.", text_color="#ff6b6b")
            self.add_log("❌ Arquivo qrcode.png não encontrado!")
    
    def load_qr_image(self):
        if not os.path.exists(self.qr_image_file):
            return False
        
        try:
            self.add_log("📱 Carregando QR Code...")
            
            pil_image = Image.open(self.qr_image_file)
            pil_image = pil_image.resize((350, 350), Image.Resampling.LANCZOS)
            
            self.qr_ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,
                size=(350, 350)
            )
            
            self.qr_image_label.configure(image=self.qr_ctk_image, text="")
            self.qr_status_label.configure(text="✅ QR Code pronto! Escaneie com o WhatsApp", text_color="#2ecc71")
            
            self.add_log("✅ QR Code carregado com sucesso!")
            return True
            
        except Exception as e:
            self.add_log(f"❌ Erro ao carregar QR Code: {e}")
            self.qr_status_label.configure(text=f"❌ Erro ao carregar QR Code", text_color="#ff6b6b")
            return False
    
    def start_qr_monitoring(self):
        def monitor():
            last_exists = False
            while self.monitoring:
                try:
                    current_exists = os.path.exists(self.qr_image_file)
                    if current_exists and not last_exists:
                        self.add_log("📱 Novo arquivo QR Code detectado!")
                        self.after(500, self.load_qr_image)
                    last_exists = current_exists
                    time.sleep(2)
                except:
                    time.sleep(5)
        
        threading.Thread(target=monitor, daemon=True).start()
        self.add_log("✅ Monitoramento de QR Code iniciado")
    
    def start_bot(self):
        if not os.path.exists(self.bot_file):
            messagebox.showerror("Erro", "chatbot.js não encontrado!")
            return
        
        if self.bot_running:
            self.add_log("⚠️ Robô já está rodando!")
            return
        
        self.bot_connected = False
        self.update_bot_status(False)
        
        self.qr_image_label.configure(image="", text="")
        self.qr_status_label.configure(text="🟡 Iniciando robô... Aguarde QR Code", text_color="#f39c12")
        self.qr_ctk_image = None
        
        self.add_log("=" * 50)
        self.add_log("🚀 INICIANDO ROBÔ MTECH")
        
        try:
            self.bot_process = subprocess.Popen(
                ["node", self.bot_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=self.bot_dir,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            self.bot_running = True
            self.stats["start_time"] = time.time()
            self.update_bot_status(False)
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
            
            if "🟢 Node.js:" in self.dashboard_info:
                self.dashboard_info["🟢 Node.js:"].configure(text="🟡 Iniciando...", text_color="#f39c12")
            
            def read_output():
                while self.bot_running:
                    try:
                        if self.bot_process and self.bot_process.stdout:
                            line = self.bot_process.stdout.readline()
                            if line:
                                line = line.strip()
                                if line:
                                    self.add_log(f"📱 {line}")
                                    
                                    if "ready" in line.lower() or "conectado" in line.lower() or "✅ ATENDIMENTO MTECH" in line:
                                        self.add_log("✅ WhatsApp CONECTADO com sucesso!")
                                        self.stats["total_connections"] += 1
                                        self.bot_connected = True
                                        self.after(0, lambda: self.update_bot_status(True))
                                        self.after(0, lambda: self.qr_status_label.configure(
                                            text="✅ Robô conectado com sucesso!", text_color="#2ecc71"
                                        ))
                                    
                                    if "QR Code" in line and ("salvo" in line or "saved" in line):
                                        self.add_log("📱 QR Code detectado! Carregando...")
                                        self.after(1000, self.load_qr_image)
                                    
                                    if "disconnected" in line.lower():
                                        self.add_log("⚠️ WhatsApp desconectado!")
                                        self.bot_connected = False
                                        self.after(0, lambda: self.update_bot_status(False))
                                    
                                    if "message" in line.lower() and "from" in line.lower():
                                        self.stats["total_messages"] += 1
                                        
                    except:
                        break
            
            threading.Thread(target=read_output, daemon=True).start()
            self.add_log("✅ Robô iniciado! Aguardando QR Code...")
            
        except Exception as e:
            self.add_log(f"❌ ERRO: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao iniciar:\n{str(e)}")
            self.bot_running = False
            self.update_bot_status(False)
    
    def stop_bot(self):
        if not self.bot_running:
            return
        
        self.add_log("⏹️ Parando robô...")
        try:
            if self.bot_process:
                self.bot_process.terminate()
                time.sleep(2)
                if self.bot_process.poll() is None:
                    self.bot_process.kill()
                self.bot_process = None
            
            self.bot_running = False
            self.bot_connected = False
            self.update_bot_status(False)
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")
            self.qr_status_label.configure(text="🔴 Robô desligado\nInicie para gerar novo QR Code", text_color="#ff6b6b")
            
            if "🟢 Node.js:" in self.dashboard_info:
                self.dashboard_info["🟢 Node.js:"].configure(text="🔴 Parado", text_color="#e74c3c")
            
            self.add_log("✅ Robô parado")
        except Exception as e:
            self.add_log(f"❌ ERRO: {str(e)}")
    
    def restart_bot(self):
        self.add_log("🔄 Reiniciando robô...")
        self.stop_bot()
        time.sleep(2)
        self.start_bot()
    
    def save_owner_number(self):
        if not os.path.exists(self.bot_file):
            messagebox.showerror("Erro", "chatbot.js não encontrado!")
            return
        try:
            new_owner = self.owner_entry.get()
            with open(self.bot_file, "r", encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r'const numeroProprietario = "[0-9]+@', f'const numeroProprietario = "{new_owner}@', content)
            with open(self.bot_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.add_log(f"✅ Número do proprietário alterado para: {new_owner}")
            if "👤 Proprietário:" in self.dashboard_info:
                self.dashboard_info["👤 Proprietário:"].configure(text=new_owner)
            messagebox.showinfo("Sucesso", f"Número alterado para {new_owner}\nReinicie o robô para aplicar.")
        except Exception as e:
            self.add_log(f"❌ Erro: {e}")
    
    def save_all_menus(self):
        if not os.path.exists(self.bot_file):
            messagebox.showerror("Erro", "chatbot.js não encontrado!")
            return
        
        try:
            with open(self.bot_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            menus_map = {
                "principal": "menuPrincipal",
                "iptv": "menuIPTV",
                "internet": "menuInternet",
                "recargas": "menuRecargas",
                "consultas": "menuConsultas",
                "ajuda": "menuAjuda",
                "configuracoes": "menuConfiguracoes",
                "termos": "menuTermos"
            }
            
            for menu_key, var_name in menus_map.items():
                if menu_key in self.menu_texts:
                    new_content = self.menu_texts[menu_key].get("1.0", tk.END).strip()
                    new_content = new_content.replace("`", "\\`")
                    
                    pattern = rf'const {var_name} = `([^`]*)`'
                    replacement = f'const {var_name} = `{new_content}`'
                    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    self.add_log(f"✅ Menu {menu_key} atualizado")
            
            with open(self.bot_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.add_log("✅ TODOS OS MENUS salvos com sucesso!")
            messagebox.showinfo("Sucesso", "Todos os menus foram salvos!\nReinicie o robô para aplicar.")
        except Exception as e:
            self.add_log(f"❌ Erro ao salvar menus: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def save_all_submenus(self):
        if not os.path.exists(self.bot_file):
            messagebox.showerror("Erro", "chatbot.js não encontrado!")
            return
        try:
            with open(self.bot_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            iptv_content = self.submenu_iptv_text.get("1.0", tk.END).strip()
            iptv_content = iptv_content.replace("`", "\\`")
            pattern = r'const menuIPTV = `([^`]*)`'
            replacement = f'const menuIPTV = `{iptv_content}`'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            internet_content = self.submenu_internet_text.get("1.0", tk.END).strip()
            internet_content = internet_content.replace("`", "\\`")
            pattern = r'const menuInternet = `([^`]*)`'
            replacement = f'const menuInternet = `{internet_content}`'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            recargas_content = self.submenu_recargas_text.get("1.0", tk.END).strip()
            recargas_content = recargas_content.replace("`", "\\`")
            pattern = r'const menuRecargas = `([^`]*)`'
            replacement = f'const menuRecargas = `{recargas_content}`'
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            with open(self.bot_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.add_log("✅ TODOS OS SUBMENUS salvos com sucesso!")
            messagebox.showinfo("Sucesso", "Todos os submenus foram salvos!\nReinicie o robô para aplicar.")
        except Exception as e:
            self.add_log(f"❌ Erro ao salvar submenus: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def save_messages(self):
        if not os.path.exists(self.bot_file):
            messagebox.showerror("Erro", "chatbot.js não encontrado!")
            return
        try:
            with open(self.bot_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            boas_vindas = [f'"{line.strip()}"' for line in self.boas_vindas_text.get("1.0", tk.END).strip().split("\n") if line.strip()]
            agradecimento = [f'"{line.strip()}"' for line in self.agradecimento_text.get("1.0", tk.END).strip().split("\n") if line.strip()]
            despedida = [f'"{line.strip()}"' for line in self.despedida_text.get("1.0", tk.END).strip().split("\n") if line.strip()]
            nao_entendi = [f'"{line.strip()}"' for line in self.nao_entendi_text.get("1.0", tk.END).strip().split("\n") if line.strip()]
            
            content = re.sub(r'const respostasBoasVindas = \[[^\]]+\]', f'const respostasBoasVindas = [{", ".join(boas_vindas)}]', content)
            content = re.sub(r'const respostasAgradecimento = \[[^\]]+\]', f'const respostasAgradecimento = [{", ".join(agradecimento)}]', content)
            content = re.sub(r'const respostasDespedida = \[[^\]]+\]', f'const respostasDespedida = [{", ".join(despedida)}]', content)
            content = re.sub(r'const respostasNaoEntendi = \[[^\]]+\]', f'const respostasNaoEntendi = [{", ".join(nao_entendi)}]', content)
            
            with open(self.bot_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.add_log("✅ Mensagens salvas!")
            messagebox.showinfo("Sucesso", "Mensagens salvas! Reinicie o robô para aplicar.")
        except Exception as e:
            self.add_log(f"❌ Erro: {e}")
    
    def save_prices(self):
        if not os.path.exists(self.bot_file):
            messagebox.showerror("Erro", "chatbot.js não encontrado!")
            return
        try:
            self.add_log("✅ Preços salvos!")
            messagebox.showinfo("Sucesso", "Preços salvos! Reinicie o robô para aplicar.")
        except Exception as e:
            self.add_log(f"❌ Erro: {e}")
    
    def save_links(self):
        if not os.path.exists(self.bot_file):
            messagebox.showerror("Erro", "chatbot.js não encontrado!")
            return
        
        try:
            with open(self.bot_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            link_names = {
                "1": "teste1hr1",
                "2": "teste1hr2",
                "3": "teste1hrFutebol",
                "4": "teste2hrs",
                "5": "teste4hrs",
                "6": "teste6hrIbo",
                "7": "teste12hrSemAdultos",
                "8": "teste12hrSamsung",
                "9": "teste12hrLg",
                "10": "teste12hrAndroid",
                "11": "teste12hrIphone",
                "12": "teste12hrTvBox",
                "13": "testePcNotebook",
                "14": "testeRoku",
                "15": "testeFireStick"
            }
            
            links_updated = 0
            
            for num, data in self.link_entries.items():
                novo_link = data["entry"].get().strip()
                var_name = link_names.get(num)
                
                if var_name and novo_link:
                    pattern = rf'({var_name}:\s*)"[^"]*"'
                    replacement = rf'\1"{novo_link}"'
                    
                    if re.search(pattern, content):
                        content = re.sub(pattern, replacement, content)
                        links_updated += 1
                        self.add_log(f"🔗 Link {num} ({var_name}) atualizado")
                        data["status"].configure(text="✅", text_color="#2ecc71")
                    else:
                        self.add_log(f"⚠️ Link {num} ({var_name}) não encontrado no arquivo")
                        data["status"].configure(text="⚠️", text_color="#f39c12")
                elif not novo_link:
                    data["status"].configure(text="❌", text_color="#e74c3c")
            
            with open(self.bot_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            self.add_log(f"✅ {links_updated} links salvos com sucesso!")
            messagebox.showinfo("Sucesso", f"{links_updated} links foram salvos!\nReinicie o robô para aplicar.")
        except Exception as e:
            self.add_log(f"❌ Erro ao salvar links: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def save_recargas_config(self):
        """Salvar configurações de recargas e atualizar o menu do WhatsApp"""
        try:
            # Salvar VIVO
            for valor, entries in self.vivo_entries.items():
                paga = float(entries["paga"].get().replace(",", "."))
                recebe = float(entries["recebe"].get().replace(",", "."))
                self.recargas_config["vivo"][valor] = {"paga": paga, "recebe": recebe}
            
            # Salvar TIM
            for valor, entries in self.tim_entries.items():
                paga = float(entries["paga"].get().replace(",", "."))
                recebe = float(entries["recebe"].get().replace(",", "."))
                self.recargas_config["tim"][valor] = {"paga": paga, "recebe": recebe}
            
            # Salvar CLARO
            for valor, entries in self.claro_entries.items():
                paga = float(entries["paga"].get().replace(",", "."))
                recebe = float(entries["recebe"].get().replace(",", "."))
                self.recargas_config["claro"][valor] = {"paga": paga, "recebe": recebe}
            
            # Salvar no arquivo
            if self.save_recargas_config_to_file():
                # Atualizar o chatbot.js com as novas configurações
                self.update_chatbot_recargas_config()
                # Atualizar o menu visual
                self.update_menu_recargas_display()
                self.add_log("✅ Configurações de recargas salvas com sucesso!")
                messagebox.showinfo("Sucesso", "Configurações de recargas salvas!\nAs alterações foram aplicadas ao robô.")
            else:
                messagebox.showerror("Erro", "Erro ao salvar configurações de recargas!")
        except Exception as e:
            self.add_log(f"❌ Erro ao salvar: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def update_chatbot_recargas_config(self):
        """Atualizar as configurações de recargas no chatbot.js"""
        if not os.path.exists(self.bot_file):
            return
        
        try:
            with open(self.bot_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Criar o objeto de configuração de recargas
            recargas_json = json.dumps(self.recargas_config, indent=4, ensure_ascii=False)
            
            # Procurar e substituir a configuração de recargas
            pattern = r'(const recargasConfig = )\{[\s\S]*?\};'
            replacement = f'\\1{recargas_json};'
            
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                with open(self.bot_file, "w", encoding="utf-8") as f:
                    f.write(content)
                self.add_log("✅ Chatbot.js atualizado com novas configurações de recargas!")
                return True
            else:
                self.add_log("⚠️ Não foi possível encontrar a configuração de recargas no chatbot.js")
                return False
                
        except Exception as e:
            self.add_log(f"❌ Erro ao atualizar chatbot.js: {e}")
            return False
    
    def save_bot_config(self):
        try:
            novo_tempo = self.pausa_entry.get()
            novo_limite = self.limite_testes_entry.get()
            novo_antiflood = self.antiflood_entry.get()
            
            self.add_log(f"⚙️ Configurações salvas: Pausa={novo_tempo}min, Limite={novo_limite}, Antiflood={novo_antiflood}s")
            messagebox.showinfo("Sucesso", "Configurações salvas! Reinicie o robô para aplicar.")
        except Exception as e:
            self.add_log(f"❌ Erro: {e}")
    
    def create_backup(self):
        if os.path.exists(self.bot_file):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.bot_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(backup_dir, f"chatbot_backup_{timestamp}.js")
            shutil.copy2(self.bot_file, backup_file)
            self.add_log(f"📦 Backup criado: {backup_file}")
            messagebox.showinfo("Backup", f"Backup criado com sucesso!\n{backup_file}")
    
    def restore_backup(self):
        backup_dir = os.path.join(self.bot_dir, "backups")
        if not os.path.exists(backup_dir):
            messagebox.showwarning("Aviso", "Nenhum backup encontrado")
            return
        backups = [f for f in os.listdir(backup_dir) if f.startswith("chatbot_backup_")]
        if not backups:
            messagebox.showwarning("Aviso", "Nenhum backup encontrado")
            return
        latest = sorted(backups)[-1]
        if messagebox.askyesno("Restaurar", f"Restaurar backup {latest}?"):
            shutil.copy2(os.path.join(backup_dir, latest), self.bot_file)
            self.add_log("🔄 Backup restaurado")
            messagebox.showinfo("Restaurado", "Backup restaurado! Reinicie o robô.")
    
    def on_closing(self):
        self.real_time_update = False
        self.monitoring = False
        if self.bot_running:
            if messagebox.askyesno("Sair", "Robô está rodando. Deseja pará-lo e sair?"):
                self.stop_bot()
                self.destroy()
        else:
            self.destroy()


def main():
    app = MTechBotManager()
    app.mainloop()


if __name__ == "__main__":
    main()