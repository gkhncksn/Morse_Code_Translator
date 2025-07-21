import tkinter as tk
from tkinter import messagebox, scrolledtext
from ttkbootstrap import Style, ttk
import pygame
import threading
import time
import math
import random

# NumPy'yi import etmeyi dene, yoksa alternatif çözüm kullan
try:
    import pygame.sndarray
    import numpy as np
    USE_NUMPY = True
except ImportError:
    USE_NUMPY = False
    print("NumPy bulunamadı. Basit ses efektleri kullanılacak.")

# Pygame başlatma
pygame.init()
pygame.mixer.init()

# Morse Code Dictionary
morse_code_dict = {'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
                   'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
                   'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
                   'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
                   'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
                   'Z': '--..', '0': '-----', '1': '.----', '2': '..---', '3': '...--',
                   '4': '....-', '5': '.....', '6': '-....', '7': '--...', '8': '---..',
                   '9': '----.', '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
                   '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-', '&': '.-...',
                   ':': '---...', ';': '-.-.-.', '=': '-...-', '+': '.-.-.', '-': '-....-',
                   '_': '..--.-', '"': '.-..-.', '$': '...-..-', '@': '.--.-.', ' ': '/'
                   }

# Reverse Morse Code Dictionary
reverse_morse_code_dict = {v: k for k, v in morse_code_dict.items()}

# Mors Kodu Eğitim Setleri
morse_lessons = {
    "Temel Harfler": ["E", "T", "A", "O", "I", "N"],
    "Kolay Harfler": ["S", "H", "R", "D", "L", "U"],
    "Orta Seviye": ["C", "M", "W", "F", "G", "Y"],
    "Zor Harfler": ["P", "B", "V", "K", "J", "X", "Q", "Z"],
    "Sayılar": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
    "İşaretler": [".", ",", "?", "'", "!", "/", "(", ")", "&", ":", ";", "=", "+", "-", "_", '"', "$", "@"]
}

class MorseVisualizer:
    def __init__(self):
        self.screen_width = 600
        self.screen_height = 400
        self.screen = None
        self.clock = None
        self.running = False
        self.animation_thread = None
        self.should_close = False
        self.pygame_display_active = False
        
        # Renkler - Modern tema
        self.BLACK = (15, 15, 23)
        self.DARK_BLUE = (25, 35, 60)
        self.ELECTRIC_BLUE = (64, 156, 255)
        self.CYAN = (0, 255, 255)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 215, 0)
        self.ORANGE = (255, 140, 0)
        self.GREEN = (50, 255, 50)
        self.PURPLE = (138, 43, 226)
        
        # Animasyon değişkenleri
        self.pulse_time = 0
        self.particles = []
        
        # Ses frekansları
        self.dot_freq = 800
        self.dash_freq = 500
        
    def init_display(self):
        """Pygame display'i güvenli şekilde başlat"""
        try:
            if not pygame.get_init():
                pygame.init()
            if not self.pygame_display_active:
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                pygame.display.set_caption("🎯 Mors Kodu Görselleştirici - ESC ile kapat")
                self.clock = pygame.time.Clock()
                self.pygame_display_active = True
            return True
        except Exception as e:
            print(f"Display başlatma hatası: {e}")
            return False
        
    def create_particle(self, x, y):
        """Işık partikülü oluştur"""
        return {
            'x': x,
            'y': y,
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-2, 2),
            'life': 1.0,
            'color': random.choice([self.CYAN, self.ELECTRIC_BLUE, self.YELLOW, self.GREEN])
        }
        
    def update_particles(self):
        """Partikülleri güncelle"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 0.02
            particle['vy'] += 0.1  # Yerçekimi
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def draw_modern_signal(self, intensity=0, signal_type="dot"):
            """Modern sinyal görselleştirmesi"""
            if not self.pygame_display_active:
                return

            # Olayları işle, pencereyi kapatma isteğini yakala
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        self.should_close = True
                        # Bu fonksiyonun içinden return veya close çağırma.
                        # Bırak ana döngü bayrağı görsün ve işlemi sonlandırsın.
            except pygame.error:
                return
            
            # Eğer kapatma bayrağı aktif olduysa daha fazla çizim yapma
            if self.should_close:
                # Pencereyi kapatma işlemini buradan tamamen kaldırıyoruz.
                # Sadece fonksiyondan çıkarak animasyon döngüsünün durmasını sağlıyoruz.
                return

            try:
                self.screen.fill(self.BLACK)
                
                # ... (geri kalan çizim kodları burada aynı kalacak) ...
                if intensity > 0:
                    center_x = self.screen_width // 2
                    center_y = self.screen_height // 2
                    
                    # Merkez noktası
                    core_radius = int(30 * intensity)
                    pygame.draw.circle(self.screen, self.WHITE, (center_x, center_y), core_radius)
                    
                    # Renkli halka efektleri
                    colors = [self.ELECTRIC_BLUE, self.CYAN, self.PURPLE] if signal_type == "dot" else [self.ORANGE, self.YELLOW, self.GREEN]
                    
                    for i, color in enumerate(colors):
                        radius = int((60 + i * 40) * intensity)
                        width = max(1, int(8 * intensity))
                        if radius < self.screen_width // 2:
                            pygame.draw.circle(self.screen, color, (center_x, center_y), radius, width)
                    
                    # Darbe efekti
                    pulse_intensity = abs(math.sin(self.pulse_time * 10)) * intensity
                    pulse_radius = int(100 * pulse_intensity)
                    if pulse_radius > 0:
                        pygame.draw.circle(self.screen, self.WHITE, (center_x, center_y), pulse_radius, 2)
                    
                    # Elektrik çizgileri
                    for i in range(12):
                        angle = (i * 30) + (self.pulse_time * 50)
                        start_radius = 50 * intensity
                        end_radius = 120 * intensity
                        
                        start_x = center_x + math.cos(math.radians(angle)) * start_radius
                        start_y = center_y + math.sin(math.radians(angle)) * start_radius
                        end_x = center_x + math.cos(math.radians(angle)) * end_radius
                        end_y = center_y + math.sin(math.radians(angle)) * end_radius
                        
                        color = colors[i % len(colors)]
                        pygame.draw.line(self.screen, color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), 3)
                    
                    # Partiküller ekle
                    if random.random() < 0.3:
                        for _ in range(5):
                            px = center_x + random.randint(-50, 50)
                            py = center_y + random.randint(-50, 50)
                            self.particles.append(self.create_particle(px, py))
                
                # Partikülleri güncelle ve çiz
                self.update_particles()
                for particle in self.particles:
                    alpha = int(255 * particle['life'])
                    size = max(1, int(5 * particle['life']))
                    color = tuple(min(255, max(0, c)) for c in particle['color'])
                    pygame.draw.circle(self.screen, color, (int(particle['x']), int(particle['y'])), size)
                
                # Sinyal türü göstergesi
                font = pygame.font.Font(None, 36)
                if intensity > 0:
                    text = "● DOT" if signal_type == "dot" else "▬ DASH"
                    color = self.CYAN if signal_type == "dot" else self.ORANGE
                    text_surface = font.render(text, True, color)
                    text_rect = text_surface.get_rect(center=(self.screen_width // 2, 50))
                    self.screen.blit(text_surface, text_rect)
                
                # ESC tuşu bilgisi
                info_font = pygame.font.Font(None, 24)
                info_text = info_font.render("ESC veya X ile kapat", True, self.WHITE)
                self.screen.blit(info_text, (10, 10))
                
                self.pulse_time += 0.1
                pygame.display.flip()
                
            except pygame.error as e:
                print(f"Pygame çizim hatası: {e}")
                self.pygame_display_active = False
        
    def generate_beep(self, frequency, duration):
        """Geliştirilmiş ses üretimi"""
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init()
            except:
                return
                
        if USE_NUMPY:
            try:
                sample_rate = 22050
                frames = int(duration * sample_rate)
                
                # Daha yumuşak ses dalgası (envelope ile)
                wave_array = np.zeros((frames, 2))
                for i in range(frames):
                    # Envelope (başlangıç ve bitiş yumuşak)
                    envelope = 1.0
                    if i < frames * 0.1:  # Fade in
                        envelope = i / (frames * 0.1)
                    elif i > frames * 0.9:  # Fade out
                        envelope = (frames - i) / (frames * 0.1)
                    
                    wave = 3000 * envelope * math.sin(2 * math.pi * frequency * i / sample_rate)
                    wave_array[i] = [wave, wave]
                
                wave_array = wave_array.astype(np.int16)
                sound = pygame.sndarray.make_sound(wave_array)
                sound.play()
                return
            except Exception as e:
                print(f"NumPy ses üretim hatası: {e}")
        
        # Basit ses alternatifi - ses çıkmazsa sessizce devam et
        try:
            # Pygame mixer ile basit ton
            pygame.mixer.quit()
            pygame.mixer.init(frequency=22050, size=-16, channels=2)
            
            # Basit sinüs dalgası
            duration_ms = int(duration * 1000)
            sample_rate = 22050
            frames = int(duration * sample_rate)
            
            arr = []
            for i in range(frames):
                wave = int(3000 * math.sin(2 * math.pi * frequency * i / sample_rate))
                arr.append([wave, wave])
            
            sound_array = pygame.array.array('h', arr)
            sound = pygame.sndarray.make_sound(sound_array)
            sound.play()
            
        except Exception as e:
            print(f"Ses üretilemedi: {e}")
            
    def show_morse_visually(self, morse_text):
        """Geliştirilmiş görsel gösterim"""
        if not self.init_display():
            print("Display başlatılamadı, sadece ses çalacak")
            # Sadece ses çal
            for char in morse_text:
                if char == '.':
                    self.generate_beep(self.dot_freq, 0.2)
                    time.sleep(0.3)
                elif char == '-':
                    self.generate_beep(self.dash_freq, 0.6)
                    time.sleep(0.3)
                elif char == ' ':
                    time.sleep(0.3)
                elif char == '/':
                    time.sleep(0.7)
            return
            
        self.running = True
        self.should_close = False
        self.particles = []
        
        def animation_loop():
            for char in morse_text:
                if not self.running or self.should_close:
                    break
                    
                if char == '.':  # Nokta
                    self.draw_modern_signal(1.0, "dot")
                    self.generate_beep(self.dot_freq, 0.2)
                    for _ in range(10):  # 0.2 saniye = 10 frame (20ms her frame)
                        if self.should_close:
                            break
                        self.draw_modern_signal(1.0, "dot")
                        self.clock.tick(50)
                    
                    for _ in range(5):  # 0.1 saniye ara
                        if self.should_close:
                            break
                        self.draw_modern_signal(0)
                        self.clock.tick(50)
                        
                elif char == '-':  # Çizgi
                    self.draw_modern_signal(1.0, "dash")
                    self.generate_beep(self.dash_freq, 0.6)
                    for _ in range(30):  # 0.6 saniye
                        if self.should_close:
                            break
                        self.draw_modern_signal(1.0, "dash")
                        self.clock.tick(50)
                    
                    for _ in range(5):  # 0.1 saniye ara
                        if self.should_close:
                            break
                        self.draw_modern_signal(0)
                        self.clock.tick(50)
                        
                elif char == ' ':  # Harf arası boşluk
                    for _ in range(15):  # 0.3 saniye
                        if self.should_close:
                            break
                        self.draw_modern_signal(0)
                        self.clock.tick(50)
                        
                elif char == '/':  # Kelime arası boşluk
                    for _ in range(35):  # 0.7 saniye
                        if self.should_close:
                            break
                        self.draw_modern_signal(0)
                        self.clock.tick(50)
                        
            # Animasyon bitince
            for _ in range(25):  # 0.5 saniye bekle
                if self.should_close:
                    break
                self.draw_modern_signal(0)
                self.clock.tick(50)
            
            self.running = False
            
        if self.animation_thread and self.animation_thread.is_alive():
            self.stop_animation()
            
        self.animation_thread = threading.Thread(target=animation_loop)
        self.animation_thread.daemon = True
        self.animation_thread.start()
        
    def stop_animation(self):
        """Animasyonu durdur"""
        self.running = False
        self.should_close = True
        if self.animation_thread:
            self.animation_thread.join(timeout=1.0)
        
    def close(self):
        """Pygame penceresini güvenli şekilde kapat"""
        self.stop_animation()
        try:
            if self.pygame_display_active:
                pygame.display.quit()
                self.pygame_display_active = False
        except Exception as e:
            print(f"Display kapatma hatası: {e}")

# Global değişkenler
morse_visualizer = None

def show_text_to_morse():
    home_frame.pack_forget()
    translation_frame.pack()
    translation_label.config(text="📝 Metni Girin:")
    translation_button.config(text="🔊 Mors Koduna Çevir (Ses+Görsel)")
    translation_button.config(command=text_to_morse_code)

def show_morse_code_to_text():
    home_frame.pack_forget()
    translation_frame.pack()
    translation_label.config(text="📻 Mors Kodunu Girin:")
    translation_button.config(text="📝 Metne Çevir")
    translation_button.config(command=morse_code_to_text)

def show_morse_table():
    home_frame.pack_forget()
    table_frame.pack(fill="both", expand=True)

def show_practice_mode():
    home_frame.pack_forget()
    practice_frame.pack(fill="both", expand=True)
    generate_practice_question()

def show_speed_test():
    home_frame.pack_forget()
    speed_frame.pack(fill="both", expand=True)
    start_speed_test()

def show_home_screen():
    global morse_visualizer
    # Tüm frame'leri gizle
    translation_frame.pack_forget()
    table_frame.pack_forget()
    practice_frame.pack_forget()
    speed_frame.pack_forget()
    
    home_frame.pack(fill="both", expand=True)
    
    # Input alanlarını temizle
    if 'input_text' in globals():
        input_text.delete("1.0", "end")
        output_text.delete("1.0", "end")
    
    # Görselleştiriciyi durdur
    if morse_visualizer:
        morse_visualizer.stop_animation()

def text_to_morse_code():
    global morse_visualizer
    
    text = input_text.get("1.0", "end").strip().upper()
    if not text:
        messagebox.showwarning("⚠️ Boş Giriş", "Lütfen çevrilecek metin girin.")
        return
        
    # Morse kodu girişini kontrol et
    for char in text:
        if char in ['.', '-']:
            messagebox.showwarning("⚠️ Geçersiz Giriş", "Bu seçenekte Mors kodu girişi yapılamaz.")
            return
    
    morse_code = ""
    for char in text:
        if char in morse_code_dict:
            morse_code += morse_code_dict[char] + " "
        else:
            morse_code += "? "  # Bilinmeyen karakterler için
            
    output_text.delete("1.0", "end")
    output_text.insert("1.0", morse_code)
    
    # Görsel ve ses efekti başlat
    if not morse_visualizer:
        morse_visualizer = MorseVisualizer()
    
    morse_visualizer.show_morse_visually(morse_code)

def morse_code_to_text():
    morse_input = input_text.get("1.0", "end").strip()
    if not morse_input:
        messagebox.showwarning("⚠️ Boş Giriş", "Lütfen Mors kodu girin.")
        return
    
    # Boşlukla ayır
    morse_codes = morse_input.split(" ")
    
    text = ""
    for code in morse_codes:
        if code.strip() in reverse_morse_code_dict:
            text += reverse_morse_code_dict[code.strip()]
        elif code.strip() == "":
            continue
        else:
            text += "?"  # Bilinmeyen kodlar için
            
    output_text.delete("1.0", "end")
    output_text.insert("1.0", text)

def clear_text():
    global morse_visualizer
    if 'input_text' in globals():
        input_text.delete("1.0", "end")
        output_text.delete("1.0", "end")
    if morse_visualizer:
        morse_visualizer.stop_animation()

# Pratik Modu Fonksiyonları
practice_score = 0
practice_total = 0
current_question = ""

def generate_practice_question():
    global current_question
    
    # Rastgele kategori ve karakter seç
    category = random.choice(list(morse_lessons.keys()))
    current_question = random.choice(morse_lessons[category])
    
    practice_question_label.config(text=f"Bu Mors kodunun karşılığı nedir?\n\n{morse_code_dict[current_question]}\n\nKategori: {category}")
    practice_entry.delete(0, tk.END)
    practice_result_label.config(text="")

def check_practice_answer():
    global practice_score, practice_total
    
    user_answer = practice_entry.get().strip().upper()
    practice_total += 1
    
    if user_answer == current_question:
        practice_score += 1
        practice_result_label.config(text="✅ Doğru!", foreground="green")
    else:
        practice_result_label.config(text=f"❌ Yanlış! Doğru cevap: {current_question}", foreground="red")
    
    practice_score_label.config(text=f"Skor: {practice_score}/{practice_total}")
    
    # 1 saniye sonra yeni soru
    window.after(1500, generate_practice_question)

# Hız Testi Fonksiyonları
speed_test_active = False
speed_test_start_time = 0
speed_test_words = []

def start_speed_test():
    global speed_test_active, speed_test_start_time, speed_test_words
    
    # Test kelimelerini oluştur
    test_chars = ['E', 'T', 'A', 'O', 'I', 'N', 'S', 'H', 'R', 'D', 'L', 'U']
    speed_test_words = [random.choice(test_chars) for _ in range(10)]
    
    speed_test_question.config(text=f"Bu karakterleri Mors koduna çevirin:\n\n{' '.join(speed_test_words)}")
    speed_test_entry.delete("1.0", "end")
    speed_test_result.config(text="⏱️ Zamanınız başladı!")
    
    speed_test_active = True
    speed_test_start_time = time.time()

def check_speed_test():
    global speed_test_active
    
    if not speed_test_active:
        messagebox.showinfo("ℹ️ Bilgi", "Önce hız testini başlatın!")
        return
    
    elapsed_time = time.time() - speed_test_start_time
    user_input = speed_test_entry.get("1.0", "end").strip()
    
    # Doğru cevabı oluştur
    correct_answer = " ".join([morse_code_dict[char] for char in speed_test_words])
    
    # Doğruluğu kontrol et
    if user_input == correct_answer:
        wpm = len(speed_test_words) / (elapsed_time / 60)
        speed_test_result.config(
            text=f"✅ Tebrikler!\nSüre: {elapsed_time:.2f} saniye\nHız: {wpm:.1f} karakter/dakika",
            foreground="green"
        )
    else:
        speed_test_result.config(
            text=f"❌ Hatalı çeviri!\nDoğru cevap:\n{correct_answer}",
            foreground="red"
        )
    
    speed_test_active = False

def on_closing():
    """Program kapatılırken pygame'i temizle"""
    global morse_visualizer
    try:
        if morse_visualizer:
            morse_visualizer.close()
    except Exception as e:
        print(f"Visualizer kapatma hatası: {e}")
    
    try:
        pygame.quit()  # Düzeltildi
    except Exception as e:
        print(f"Pygame kapatma hatası: {e}")
    
    try:
        window.destroy()
    except Exception as e:
        print(f"Pencere kapatma hatası: {e}")

# Ana pencereyi oluştur
window = tk.Tk()
window.title("🎯 Gelişmiş Mors Kodu Öğrenme ve Çeviri Merkezi")
window.geometry("500x680")
window.protocol("WM_DELETE_WINDOW", on_closing)
style = Style(theme="cosmo")

# Ana ekran
home_frame = ttk.Frame(window, padding="20")
home_frame.pack(fill="both", expand=True)

# Başlık
title_frame = ttk.Frame(home_frame)
title_frame.pack(pady=(0, 20))

home_label = ttk.Label(title_frame, text="🎯 Mors Kodu Merkezi", 
                       font=('Segoe UI', 28, 'bold'))
home_label.pack()

subtitle_label = ttk.Label(title_frame, text="Öğrenin • Pratik Yapın • Çevirin", 
                          font=('Segoe UI', 14))
subtitle_label.pack(pady=(5, 0))

# Ana butonlar - 2x3 grid
buttons_frame = ttk.Frame(home_frame)
buttons_frame.pack(pady=20)

# Sol kolon
left_col = ttk.Frame(buttons_frame)
left_col.pack(side=tk.LEFT, padx=20)

text_to_morse_btn = ttk.Button(left_col, text="📝 Metin → Mors Kodu\n(Görsel + Ses)", 
                               command=show_text_to_morse, width=25)
text_to_morse_btn.pack(pady=8)

morse_to_text_btn = ttk.Button(left_col, text="📻 Mors Kodu → Metin", 
                               command=show_morse_code_to_text, width=25)
morse_to_text_btn.pack(pady=8)

table_btn = ttk.Button(left_col, text="📚 Mors Alfabesi Tablosu", 
                       command=show_morse_table, width=25)
table_btn.pack(pady=8)

# Sağ kolon
right_col = ttk.Frame(buttons_frame)
right_col.pack(side=tk.LEFT, padx=20)

practice_btn = ttk.Button(right_col, text="🎮 Pratik Modu\n(Öğrenme Oyunu)", 
                          command=show_practice_mode, width=25)
practice_btn.pack(pady=8)

speed_btn = ttk.Button(right_col, text="⚡ Hız Testi\n(WPM Ölçümü)", 
                       command=show_speed_test, width=25)
speed_btn.pack(pady=8)

# Bilgi paneli
info_frame = ttk.LabelFrame(home_frame, text="💡 Bilgi", padding="15")
info_frame.pack(pady=20, fill="x")

info_text = ttk.Label(info_frame, 
                     text="• Metin → Mors seçeneği görsel fener efektleri ve ses içerir\n"
                          "• Pratik modunda farklı kategorilerden sorular çözün\n"
                          "• Hız testinde karakter/dakika hızınızı ölçün\n"
                          "• Mors alfabesi tablosunu referans olarak kullanın",
                     font=('Segoe UI', 10), justify="left")
info_text.pack()

# Çeviri ekranı
translation_frame = ttk.Frame(window, padding="20")

translation_label = ttk.Label(translation_frame, text="Input Text:", 
                              font=('Segoe UI', 16, 'bold'))
translation_label.pack(pady=(0, 10))

input_text = tk.Text(translation_frame, height=4, font=('Consolas', 12), wrap=tk.WORD)
input_text.pack(pady=(0, 10), fill="x")

output_text_label = ttk.Label(translation_frame, text="🎯 Çıktı:",
                              font=('Segoe UI', 16, 'bold'))
output_text_label.pack(pady=(10, 5))

output_text = tk.Text(translation_frame, height=4, font=('Consolas', 12), wrap=tk.WORD)
output_text.pack(pady=(0, 15), fill="x")

# Çeviri butonları
trans_button_frame = ttk.Frame(translation_frame)
trans_button_frame.pack(pady=10)

translation_button = ttk.Button(trans_button_frame, text="🔄 Çevir", width=20)
translation_button.pack(side=tk.LEFT, padx=5)

back_button = ttk.Button(trans_button_frame, text="🏠 Ana Sayfa", command=show_home_screen, width=15)
back_button.pack(side=tk.LEFT, padx=5)

clear_button = ttk.Button(trans_button_frame, text="🗑️ Temizle", command=clear_text, width=15)
clear_button.pack(side=tk.LEFT, padx=5)

# Mors Alfabesi Tablosu Ekranı
table_frame = ttk.Frame(window, padding="20")

table_title = ttk.Label(table_frame, text="📚 Mors Alfabesi Tablosu", 
                        font=('Segoe UI', 20, 'bold'))
table_title.pack(pady=(0, 20))

# Tablo için notebook (sekmeler)
table_notebook = ttk.Notebook(table_frame)
table_notebook.pack(fill="both", expand=True, pady=(0, 15))

# Her kategori için sekme oluştur
for category, chars in morse_lessons.items():
    tab_frame = ttk.Frame(table_notebook)
    table_notebook.add(tab_frame, text=category)
    
    # Tablo için frame
    tab_content = ttk.Frame(tab_frame, padding="10")
    tab_content.pack(fill="both", expand=True)
    
    # Başlık
    ttk.Label(tab_content, text=f"{category} Kategorisi", 
              font=('Segoe UI', 14, 'bold')).pack(pady=(0, 10))
    
    # Tablo
    cols = 3
    for i, char in enumerate(chars):
        if i % cols == 0:
            row_frame = ttk.Frame(tab_content)
            row_frame.pack(fill="x", pady=2)
        
        char_frame = ttk.LabelFrame(row_frame, text=char, padding="10")
        char_frame.pack(side=tk.LEFT, padx=5, fill="x", expand=True)
        
        morse_label = ttk.Label(char_frame, text=morse_code_dict.get(char, "?"), 
                               font=('Consolas', 16, 'bold'))
        morse_label.pack()

table_back_btn = ttk.Button(table_frame, text="🏠 Ana Sayfaya Dön", 
                           command=show_home_screen)
table_back_btn.pack(pady=10)

# Pratik Modu Ekranı (656. satırdan devam)
practice_frame = ttk.Frame(window, padding="20")

practice_title = ttk.Label(practice_frame, text="🎮 Pratik Modu - Öğrenme Oyunu", 
                          font=('Segoe UI', 20, 'bold'))
practice_title.pack(pady=(0, 20))

practice_question_label = ttk.Label(practice_frame, text="Soru yükleniyor...", 
                                   font=('Segoe UI', 14), justify="center")
practice_question_label.pack(pady=20)

practice_entry = ttk.Entry(practice_frame, font=('Segoe UI', 16), width=10, justify="center")
practice_entry.pack(pady=10)

practice_entry.bind('<Return>', lambda event: check_practice_answer())

practice_button_frame = ttk.Frame(practice_frame)
practice_button_frame.pack(pady=15)

practice_check_btn = ttk.Button(practice_button_frame, text="✅ Cevapla", 
                               command=check_practice_answer)
practice_check_btn.pack(side=tk.LEFT, padx=5)

practice_skip_btn = ttk.Button(practice_button_frame, text="⏭️ Atla", 
                              command=generate_practice_question)
practice_skip_btn.pack(side=tk.LEFT, padx=5)

practice_result_label = ttk.Label(practice_frame, text="", font=('Segoe UI', 12, 'bold'))
practice_result_label.pack(pady=10)

practice_score_label = ttk.Label(practice_frame, text="Skor: 0/0", 
                                font=('Segoe UI', 12))
practice_score_label.pack(pady=5)

practice_back_btn = ttk.Button(practice_frame, text="🏠 Ana Sayfaya Dön", 
                              command=show_home_screen)
practice_back_btn.pack(pady=20)

# Hız Testi Ekranı
speed_frame = ttk.Frame(window, padding="20")

speed_title = ttk.Label(speed_frame, text="⚡ Hız Testi - WPM Ölçümü", 
                       font=('Segoe UI', 20, 'bold'))
speed_title.pack(pady=(0, 20))

speed_test_question = ttk.Label(speed_frame, text="Başlamak için 'Test Başlat' butonuna basın", 
                               font=('Segoe UI', 14), justify="center")
speed_test_question.pack(pady=20)

speed_test_entry = tk.Text(speed_frame, height=3, font=('Consolas', 12), wrap=tk.WORD)
speed_test_entry.pack(pady=10, fill="x")

speed_button_frame = ttk.Frame(speed_frame)
speed_button_frame.pack(pady=15)

speed_start_btn = ttk.Button(speed_button_frame, text="🚀 Test Başlat", 
                            command=start_speed_test)
speed_start_btn.pack(side=tk.LEFT, padx=5)

speed_check_btn = ttk.Button(speed_button_frame, text="✅ Kontrol Et", 
                            command=check_speed_test)
speed_check_btn.pack(side=tk.LEFT, padx=5)

speed_test_result = ttk.Label(speed_frame, text="", font=('Segoe UI', 12, 'bold'), 
                             justify="center")
speed_test_result.pack(pady=20)

speed_back_btn = ttk.Button(speed_frame, text="🏠 Ana Sayfaya Dön", 
                           command=show_home_screen)
speed_back_btn.pack(pady=10)

# Hız testi bilgi paneli
speed_info_frame = ttk.LabelFrame(speed_frame, text="💡 Nasıl Çalışır?", padding="15")
speed_info_frame.pack(pady=20, fill="x")

speed_info_text = ttk.Label(speed_info_frame, 
                           text="• Size 10 rastgele karakter verilecek\n"
                                "• Bu karakterleri Mors koduna çevirin\n"
                                "• Süreniz otomatik olarak ölçülecek\n"
                                "• Doğru çeviri yaparsanız WPM hızınızı göreceksiniz\n"
                                "• Formatı doğru kullanın: '.- / -... / ...'",
                           font=('Segoe UI', 10), justify="left")
speed_info_text.pack()

# Program başlatma
if __name__ == "__main__":
    try:
        # İlk ekranı göster
        show_home_screen()
        
        # Pencereyi başlat
        window.mainloop()
        
    except KeyboardInterrupt:
        print("\nProgram kullanıcı tarafından sonlandırıldı.")
        
    except Exception as e:
        print(f"Program hatası: {e}")
        messagebox.showerror("❌ Hata", f"Beklenmeyen hata: {e}")
        
    finally:
        # Temizlik
        if morse_visualizer:
            morse_visualizer.close()
        try:
            pygame.quit()
        except:
            pass
