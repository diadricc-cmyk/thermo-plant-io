import os
import random
from datetime import datetime
from collections import deque

from kivy.app import App
from kivy.utils import platform
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.graphics import Color, Line, Rectangle

try:
    from plyer import share
except ImportError:
    share = None


KV = '''
<TempGraph>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.13, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: 0.2, 0.2, 0.25, 0.6
        Line:
            points: [self.x, self.y + self.height*0.25, self.x + self.width, self.y + self.height*0.25]
            width: 1
        Line:
            points: [self.x, self.y + self.height*0.5, self.x + self.width, self.y + self.height*0.5]
            width: 1
        Line:
            points: [self.x, self.y + self.height*0.75, self.x + self.width, self.y + self.height*0.75]
            width: 1
        Line:
            points: [self.x + self.width*0.33, self.y, self.x + self.width*0.33, self.y + self.height]
            width: 1
        Line:
            points: [self.x + self.width*0.66, self.y, self.x + self.width*0.66, self.y + self.height]
            width: 1
        Color:
            rgba: 0.3, 0.3, 0.38, 1
        Line:
            rectangle: self.x, self.y, self.width, self.height
            width: 1


<TempCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: '240dp'
    padding: '12dp'
    spacing: '6dp'

    canvas.before:
        Color:
            rgba: 0.15, 0.15, 0.19, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]

    BoxLayout:
        size_hint_y: None
        height: '28dp'

        Label:
            text: root.temp_name
            bold: True
            font_size: '14sp'
            color: 0.95, 0.95, 0.95, 1
            halign: 'left'
            text_size: self.size

        Button:
            text: 'X'
            size_hint_x: None
            width: '26dp'
            background_color: 0.85, 0.25, 0.25, 1
            background_normal: ''
            bold: True
            font_size: '12sp'
            on_press: root.remove_callback(root)

    BoxLayout:
        size_hint_y: None
        height: '32dp'
        spacing: '6dp'

        Label:
            text: f"Actual: {root.current_temp:.1f}°C"
            font_size: '13sp'
            color: 0.2, 0.8, 0.9, 1
            halign: 'left'
            text_size: self.size

        BoxLayout:
            orientation: 'horizontal'
            spacing: '3dp'
            size_hint_x: 1.4

            Label:
                text: "Set:"
                font_size: '11sp'
                color: 0.7, 0.7, 0.7, 1
                size_hint_x: None
                width: '24dp'

            TextInput:
                id: setpoint_input
                text: str(root.setpoint)
                multiline: False
                input_filter: 'float'
                font_size: '12sp'
                on_text_validate: root.enviar_setpoint(self.text)

            Button:
                text: 'Enviar'
                size_hint_x: None
                width: '45dp'
                background_color: 0.2, 0.6, 0.86, 1
                background_normal: ''
                font_size: '10sp'
                bold: True
                on_press: root.enviar_setpoint(setpoint_input.text)

    BoxLayout:
        orientation: 'horizontal'
        spacing: '4dp'

        BoxLayout:
            orientation: 'vertical'
            size_hint_x: None
            width: '35dp'

            Label:
                text: f"{root.max_val:.0f}°"
                font_size: '9sp'
                color: 0.6, 0.6, 0.6, 1
                halign: 'right'
                text_size: self.size

            Label:
                text: f"{root.mid_val:.0f}°"
                font_size: '9sp'
                color: 0.6, 0.6, 0.6, 1
                halign: 'right'
                text_size: self.size

            Label:
                text: f"{root.min_val:.0f}°"
                font_size: '9sp'
                color: 0.6, 0.6, 0.6, 1
                halign: 'right'
                text_size: self.size

        TempGraph:
            id: graph_widget
            size_hint: (1, 1)

    BoxLayout:
        size_hint_y: None
        height: '18dp'

        Label:
            text: "-30s"
            font_size: '9sp'
            color: 0.5, 0.5, 0.5, 1
            halign: 'left'
            text_size: self.size

        Label:
            text: "-15s"
            font_size: '9sp'
            color: 0.5, 0.5, 0.5, 1
            halign: 'center'
            text_size: self.size

        Label:
            text: "Ahora"
            font_size: '9sp'
            color: 0.5, 0.5, 0.5, 1
            halign: 'right'
            text_size: self.size


<MainScreen>:
    orientation: 'vertical'
    padding: '14dp'
    spacing: '12dp'

    canvas.before:
        Color:
            rgba: 0.08, 0.08, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        size_hint_y: None
        height: '45dp'
        spacing: '10dp'

        Widget:
            size_hint_x: None
            width: '40dp'

            canvas:
                Color:
                    rgba: 0.2, 0.8, 0.9, 1
                Line:
                    circle: (self.center_x, self.center_y, 14)
                    width: 2

                Color:
                    rgba: 1, 0.6, 0.2, 1
                Rectangle:
                    pos: self.center_x - 3, self.center_y - 3
                    size: 6, 6

        BoxLayout:
            orientation: 'vertical'

            Label:
                text: 'THERMO-PLANT IO'
                font_size: '16sp'
                bold: True
                color: 1, 1, 1, 1
                halign: 'left'
                text_size: self.size

            Label:
                text: 'Control con envío de Setpoint integrado'
                font_size: '10sp'
                color: 0.6, 0.6, 0.6, 1
                halign: 'left'
                text_size: self.size

    ScrollView:
        GridLayout:
            id: container
            cols: 2
            spacing: '12dp'
            size_hint_y: None
            height: self.minimum_height
            row_default_height: '240dp'
            row_force_default: True

    BoxLayout:
        size_hint_y: None
        height: '42dp'
        spacing: '10dp'

        Button:
            text: '+ Agregar Sensor'
            background_color: 0.15, 0.6, 0.8, 1
            background_normal: ''
            font_size: '13sp'
            bold: True
            on_press: root.add_temperature_sensor()

        Button:
            text: 'Exportar / Compartir'
            background_color: 0.2, 0.7, 0.4, 1
            background_normal: ''
            font_size: '13sp'
            bold: True
            on_press: app.exportar_archivo()
'''


class TempGraph(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = deque([25.0] * 30, maxlen=30)
        self.bind(pos=self.update_graph, size=self.update_graph)

    def add_value(self, val):
        self.history.append(val)
        self.update_graph()

    def update_graph(self, *args):
        self.canvas.clear()

        with self.canvas:
            Color(0.2, 0.8, 0.9, 1)

            points = []
            w = self.width
            h = self.height

            x_step = w / (len(self.history) - 1)

            min_v = min(self.history) - 3
            max_v = max(self.history) + 3

            if max_v - min_v == 0:
                max_v += 1

            for i, val in enumerate(self.history):
                x = self.x + i * x_step
                y = self.y + 6 + ((val - min_v) / (max_v - min_v)) * (h - 12)
                points.extend([x, y])

            if len(points) >= 4:
                Line(points=points, width=1.5)


class TempCard(BoxLayout):
    temp_name = StringProperty("Sensor")
    current_temp = NumericProperty(25.0)
    setpoint = NumericProperty(30.0)
    min_val = NumericProperty(20.0)
    mid_val = NumericProperty(25.0)
    max_val = NumericProperty(30.0)

    def __init__(
        self,
        name,
        current=25.0,
        setpoint=30.0,
        remove_callback=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.temp_name = name
        self.current_temp = current
        self.setpoint = setpoint
        self.remove_callback = remove_callback

    def enviar_setpoint(self, value_str):
        try:
            self.setpoint = float(value_str)

            print(
                f"[ACCIÓN] Enviando setpoint de "
                f"'{self.temp_name}': {self.setpoint}°C"
            )

            # AQUÍ irá posteriormente la comunicación
            # Wi-Fi o Bluetooth con el controlador.

        except ValueError:
            print("Setpoint no válido.")

    def simulate_data(self):
        self.current_temp += random.uniform(-0.4, 0.4)

        graph = self.ids.graph_widget
        graph.add_value(self.current_temp)

        self.min_val = min(graph.history) - 2
        self.max_val = max(graph.history) + 2
        self.mid_val = (self.min_val + self.max_val) / 2


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.sensors = []

        self.add_temperature_sensor(
            "Reactor Principal",
            24.5,
            35.0
        )

        self.add_temperature_sensor(
            "Sistema Enfriamiento",
            26.0,
            32.0
        )

        self.add_temperature_sensor(
            "Zona Calentamiento",
            22.8,
            30.0
        )

        Clock.schedule_interval(
            self.update_simulation,
            1.0
        )

    def add_temperature_sensor(
        self,
        name=None,
        current=25.0,
        setpoint=30.0
    ):
        if not name:
            name = f"Sensor {len(self.sensors) + 1}"

        card = TempCard(
            name=name,
            current=current,
            setpoint=setpoint,
            remove_callback=self.remove_sensor
        )

        self.sensors.append(card)
        self.ids.container.add_widget(card)

        App.get_running_app().actualizar_cabecera_txt(
            self.sensors
        )

    def remove_sensor(self, card):
        if card in self.sensors:
            self.sensors.remove(card)
            self.ids.container.remove_widget(card)

        App.get_running_app().actualizar_cabecera_txt(
            self.sensors
        )

    def update_simulation(self, dt):
        for sensor in self.sensors:
            sensor.simulate_data()

        App.get_running_app().registrar_fila_txt(
            self.sensors
        )


class TemperatureApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.txt_path = ""

    def build(self):
        self.txt_path = os.path.join(
            self.user_data_dir,
            "historial_temperaturas.txt"
        )

        self.reiniciar_archivo_base()

        Builder.load_string(KV)

        return MainScreen()

    def reiniciar_archivo_base(self):
        try:
            with open(
                self.txt_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(
                    "Timestamp ; "
                    "Reactor Principal ; "
                    "Sistema Enfriamiento ; "
                    "Zona Calentamiento\n"
                )

        except Exception as e:
            print("Error al inicializar TXT:", e)

    def actualizar_cabecera_txt(self, sensors):
        try:
            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            nombres = " ; ".join(
                [s.temp_name for s in sensors]
            )

            with open(
                self.txt_path,
                "a",
                encoding="utf-8"
            ) as f:

                f.write(
                    f"\n--- CAMBIO DE SENSORES "
                    f"[{timestamp}] ---\n"
                )

                f.write(
                    f"Timestamp ; {nombres}\n"
                )

        except Exception as e:
            print("Error al actualizar cabecera:", e)

    def registrar_fila_txt(self, sensors):
        try:
            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            valores = " ; ".join(
                [f"{s.current_temp:.2f}" for s in sensors]
            )

            linea = f"{timestamp} ; {valores}\n"

            with open(
                self.txt_path,
                "a",
                encoding="utf-8"
            ) as f:

                f.write(linea)

        except Exception as e:
            print("Error al escribir fila:", e)

    def exportar_archivo(self):
        if share is None:
            print("Plyer no está disponible.")
            return

        try:
            share.share_file(
                filepath=self.txt_path,
                text="Registro de temperaturas de la planta:"
            )

        except Exception as e:
            print(
                "Error al compartir archivo:",
                e
            )


if __name__ == "__main__":
    TemperatureApp().run()
