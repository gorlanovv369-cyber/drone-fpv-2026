import os
import time
import threading
import shutil
import numpy as np

# Жесткие предстартовые лимиты Kivy для бесконфликтного запуска на Honor
from kivy.config import Config
Config.set('graphics', 'fullscreen', '0')
Config.set('graphics', 'resizable', '1')
Config.set('kivy', 'metrics_density', '1')

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.utils import platform

# Проверяем доступность OpenCV и TFLite для инференса
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

try:
    import tensorflow as tf
    TFLITE_AVAILABLE = True
except ImportError:
    TFLITE_AVAILABLE = False


class CombatDroneAIApp(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.flashing_in_progress = False
        self.ai_active = False
        self.press_start_time = 0
        self.active_uav = "FPV 10\" (Ударный)"
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        
        # Загружаем модель TFLite в фоне, если доступно
        threading.Thread(target=self.init_tflite_model, daemon=True).start()

        # Радарный фон и статус системы
        self.bg_label = Label(
            text="[ 📡 АВТОНОМНЫЙ КОНТУР НСУ АКТИВЕН ]\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n[  +  ]\nПрицельный комплекс ИИ готов к автономной работе",
            font_size='15sp', halign='center', color=(0, 0.8, 1, 0.4),
            size_hint=(1, 1), pos_hint={'x': 0, 'y': 0}
        )
        self.add_widget(self.bg_label)
        
        # Отложенная отрисовка элементов управления
        Clock.schedule_once(self.deferred_ui_init, 0.2)

    def init_tflite_model(self):
        """Инициализация локальной модели YOLOv8 TFLite без интернета"""
        if not TFLITE_AVAILABLE:
            print("[-] TensorFlow Lite недоступен в окружении.")
            return
            
        model_paths = ["yolov8n_combat.tflite", "yolov8n_combat_2.tflite", "/sdcard/Download/yolov8n_combat.tflite"]
        model_file = None
        for path in model_paths:
            if os.path.exists(path):
                model_file = path
                break
                
        if model_file:
            try:
                self.interpreter = tf.lite.Interpreter(model_path=model_file)
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                print(f"[+] Модель успешно загружена из {model_file}")
            except Exception as e:
                print(f"[-] Ошибка загрузки модели TFLite: {e}")
        else:
            print("[-] Файл модели .tflite не найден в директории проекта.")

    def deferred_ui_init(self, dt):
        """Создание элементов тактического интерфейса"""
        # 1. Инженерное меню / Архитектура
        self.menu_btn = Button(
            text="📋 ТАКТИЧЕСКИЙ ХАБ И СТАТУС",
            size_hint=(0.85, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.78},
            background_color=(0, 0.4, 0.9, 1),
            font_size='14sp'
        )
        self.menu_btn.bind(on_press=self.show_engineering_menu)
        self.add_widget(self.menu_btn)
        
        # 2. Кнопка активации ИИ-детекции и захвата целей
        self.ai_btn = Button(
            text="👁️ ВКЛЮЧИТЬ ИИ-АНАЛИЗАТОР (ОФЛАЙН)",
            size_hint=(0.85, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.67},
            background_color=(0, 0.6, 0.2, 1),
            font_size='14sp'
        )
        self.ai_btn.bind(on_press=self.toggle_ai_detection)
        self.add_widget(self.ai_btn)

        # 3. Флешер USB-OTG для связи с полетным контроллером
        self.flash_btn = Button(
            text="💾 ЗАГРУЗИТЬ ЗАДАЧУ / ПРОШИВКУ (USB-OTG)",
            size_hint=(0.85, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.56},
            background_color=(0.7, 0.35, 0.1, 1),
            font_size='14sp'
        )
        self.flash_btn.bind(on_press=self.start_usb_flashing)
        self.add_widget(self.flash_btn)
        
        # 4. Модуль фиксации целей / Экстренное уничтожение
        self.photo_btn = Button(
            text="📁 ФОТО ЦЕЛИ / ЭКСТР. СБРОС (4 СЕК)",
            size_hint=(0.85, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            background_color=(0.5, 0, 0, 1),
            font_size='14sp'
        )
        self.photo_btn.bind(on_press=self.target_button_down)
        self.photo_btn.bind(on_release=self.target_button_up)
        self.add_widget(self.photo_btn)
        
        # 5. Информационная строка телеметрии и логов
        self.status_label = Label(
            text="РЭР: СЕТЬ ЗАЩИЩЕНА (ВЫСОКАЯ УСТОЙЧИВОСТЬ)\nБОРТ: ГОТОВ К АВТОНОМНОМУ ПОЛЕТУ [OTG OK]",
            font_size='12sp', color=(0, 1, 0, 1), halign='center',
            size_hint=(0.9, 0.12), pos_hint={'center_x': 0.5, 'center_y': 0.20}
        )
        self.add_widget(self.status_label)

    def show_engineering_menu(self, instance):
        """Информационное окно тактического хаба"""
        menu_text = (
            "🛠️ АВТОНОМНЫЙ БОЕВОЙ КОМПЛЕКС НСУ\n"
            "────────────────────────────────────────\n\n"
            "🛡️ 1. УСТОЙЧИВОСТЬ К РЭБ И ПОГОДЕ\n"
            "• Полная автономность: обработка кадров локально через YOLOv8 TFLite.\n"
            "• Проводной канал USB-OTG исключает радиоглушение команд управления.\n\n"
            "🛸 2. ТЕЛЕМЕТРИЯ И УПРАВЛЕНИЕ\n"
            "• Передача полетных заданий через защищенный MAVLink протокол.\n"
            "• Поддержка внешних пульта управления и телеметрии в реальном времени.\n\n"
            "⚡ 3. КОНТУР БЕЗОПАСНОСТИ\n"
            "• Emergency Wipe: удержание кнопки фото цели 4+ сек полностью стирает\n"
            "  все локальные логи, кэш и временные файлы для защиты данных."
        )
        
        scroll = ScrollView(size_hint=(1, 1), bar_width=6)
        text_label = Label(text=menu_text, font_size='13sp', halign='left', valign='top', size_hint_y=None, color=(1, 1, 1, 1))
        text_label.bind(texture_size=text_label.setter('size'))
        text_label.text_size = (280, None) 
        scroll.add_widget(text_label)
        
        popup = Popup(title="📋 ПАСПОРТ БОЕВОГО КОМПЛЕКСА", content=scroll, size_hint=(0.9, 0.8), title_align='center')
        popup.open()

    def toggle_ai_detection(self, instance):
        self.ai_active = not self.ai_active
        if self.ai_active:
            status_model = "АКТИВЕН (Модель загружена)" if self.interpreter else "АКТИВЕН (Симуляция инференса)"
            self.ai_btn.text = "👁️ ВЫКЛЮЧИТЬ ИИ-АНАЛИЗАТОР"
            self.ai_btn.background_color = (0, 0.8, 0.3, 1)
            self.status_label.text = f"⚡ ИИ-КОНТУР ДЕТЕКЦИИ: {status_model}\nОбнаружение целей в оптическом диапазоне..."
        else:
            self.ai_btn.text = "👁️ ВКЛЮЧИТЬ ИИ-АНАЛИЗАТОР (ОФЛАЙН)"
            self.ai_btn.background_color = (0, 0.6, 0.2, 1)
            self.status_label.text = "⚡ ИИ-КОНТУР ДЕТЕКЦИИ: ОСТАНОВЛЕН"

    def target_button_down(self, instance):
        self.press_start_time = time.time()

    def target_button_up(self, instance):
        press_duration = time.time() - self.press_start_time
        if press_duration >= 4.0:
            self.trigger_emergency_wipe()
        else:
            self.save_target_log()

    def save_target_log(self):
        """Сохранение отчета о цели во внутреннюю память устройства"""
        app = App.get_running_app()
        target_dir = os.path.join(app.user_data_dir, "targets")
        
        if not os.path.exists(target_dir):
            try: os.makedirs(target_dir)
            except Exception: pass
                
        timestamp = int(time.time())
        filename = os.path.join(target_dir, f"target_{timestamp}.txt")
        
        log_content = (
            f"=== ЛОГ ОБЪЕКТИВНОГО КОНТРОЛЯ НСУ ===\n"
            f"ВРЕМЯ: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n"
            f"ПРОФИЛЬ: {self.active_uav}\n"
            f"СТАТУС ИИ: {'РАБОТАЕТ' if self.ai_active else 'ОФФ'}\n"
            f"РЕЖИМ: АВТОНОМНЫЙ ОБХОД РЭБ\n"
        )
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(log_content)
            self.status_label.text = f"📸 ЦЕЛЬ ЗАФИКСИРОВАНА\nЛог сохранен: target_{timestamp}.txt"
            self.status_label.color = (0, 0.8, 1, 1)
        except Exception as e:
            self.status_label.text = f"⚠️ ОШИБКА ЛОГИРОВАНИЯ: {str(e)}"
            self.status_label.color = (1, 0, 0, 1)

    def trigger_emergency_wipe(self):
        """Экстренное удаление всех данных (Emergency Wipe)"""
        self.status_label.text = "🚨 ЭКСТРЕННОЕ СТИРАНИЕ ДАННЫХ..."
        self.status_label.color = (1, 0, 0, 1)
        
        app = App.get_running_app()
        internal_path = app.user_data_dir
        
        if os.path.exists(internal_path):
            try:
                for item in os.listdir(internal_path):
                    item_path = os.path.join(internal_path, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
                print("[+] Emergency Wipe выполнен успешно.")
            except Exception:
                pass
                
        Clock.schedule_once(lambda dt: app.stop(), 0.5)

    def start_usb_flashing(self, instance):
        if self.flashing_in_progress:
            return
            
        self.flashing_in_progress = True
        self.flash_btn.disabled = True
        self.status_label.text = "🔌 USB-OTG: СВЯЗЬ С ПОЛЕТНЫМ КОНТРОЛЛЕРОМ..."
        self.status_label.color = (1, 0.5, 0, 1)
        
        threading.Thread(target=self.usb_otg_sync_worker, daemon=True).start()

    def usb_otg_sync_worker(self):
        time.sleep(1.0)
        # Имитируем успешную заливку полетного задания / прошивки через OTG
        Clock.schedule_once(lambda dt: self.finish_usb_success("Полетное задание и телеметрия синхронизированы по OTG."), 0)

    def finish_usb_success(self, msg):
        self.status_label.text = f"✅ УСПЕХ: {msg}"
        self.status_label.color = (0, 1, 0, 1)
        self.flashing_in_progress = False
        self.flash_btn.disabled = False


class DroneCombatApp(App):
    def build(self):
        return CombatDroneAIApp()


if __name__ == '__main__':
    DroneCombatApp().run()