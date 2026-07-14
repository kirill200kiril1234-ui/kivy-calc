from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window

Window.clearcolor = (0.07, 0.07, 0.07, 1)

class CalculatorApp(App):
    def build(self):
        self.title = "Калькулятор"
        self.expression = ""
        
        main_layout = BoxLayout(orientation="vertical", padding=15, spacing=10)
        
        self.display = Label(
            text="0",
            font_size=48,
            halign="right",
            valign="middle",
            size_hint=(1, 0.25),
            color=(1, 1, 1, 1)
        )
        self.display.bind(size=self.display.setter('text_size'))
        main_layout.add_widget(self.display)
        
        buttons_layout = GridLayout(cols=4, spacing=10, size_hint=(1, 0.75))
        
        buttons = [
            'C', '(', ')', '/',
            '7', '8', '9', '*',
            '4', '5', '6', '-',
            '1', '2', '3', '+',
            '.', '0', 'Back', '='
        ]
        
        for char in buttons:
            if char in ['/', '*', '-', '+', '=']:
                bg_color = (0.95, 0.6, 0.07, 1)
                text_color = (1, 1, 1, 1)
            elif char == 'C' or char == 'Back':
                bg_color = (0.8, 0.2, 0.2, 1)
                text_color = (1, 1, 1, 1)
            else:
                bg_color = (0.2, 0.2, 0.2, 1)
                text_color = (1, 1, 1, 1)
                
            btn = Button(
                text=char,
                font_size=28,
                background_normal='',
                background_color=bg_color,
                color=text_color
            )
            btn.bind(on_press=self.on_button_press)
            buttons_layout.add_widget(btn)
            
        main_layout.add_widget(buttons_layout)
        return main_layout

    def on_button_press(self, instance):
        text = instance.text
        
        if text == 'C':
            self.expression = ""
            self.display.text = "0"
        elif text == 'Back':
            self.expression = self.expression[:-1]
            self.display.text = self.expression if self.expression else "0"
        elif text == '=':
            if self.expression:
                try:
                    expr_to_eval = self.expression.replace('×', '*').replace('÷', '/')
                    result = eval(expr_to_eval)
                    if isinstance(result, float) and result.is_integer():
                        result = int(result)
                    self.expression = str(result)
                    self.display.text = self.expression
                except ZeroDivisionError:
                    self.display.text = "Ошибка: / 0"
                    self.expression = ""
                except Exception:
                    self.display.text = "Ошибка"
                    self.expression = ""
        else:
            if self.display.text == "0" and text not in ['.', '+', '-', '*', '/']:
                self.expression = text
            else:
                self.expression += text
            self.display.text = self.expression

if __name__ == "__main__":
    CalculatorApp().run()
