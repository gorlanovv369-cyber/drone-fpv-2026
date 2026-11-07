from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class DroneApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=20, spacing=20)
        self.label = Label(text='Drone FPV Control System\nStatus: Ready', font_size=24, halign='center')
        root.add_widget(self.label)
        btn = Button(text='Connect to Drone', size_hint=(1, 0.3), font_size=20)
        btn.bind(on_press=self.on_connect_pressed)
        root.add_widget(btn)
        return root

    def on_connect_pressed(self, instance):
        self.label.text = 'Drone FPV Control System\nStatus: Connecting...'

if __name__ == '__main__':
    DroneApp().run()
