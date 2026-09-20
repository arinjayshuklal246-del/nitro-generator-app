import threading
import time
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

class PromoGeneratorApp(App):
    def build(self):
        self.is_running = False
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.status_label = Label(text="Status: Stopped")
        
        self.toggle_button = Button(text="Start Generating")
        self.toggle_button.bind(on_press=self.toggle_generation)
        
        layout.add_widget(self.status_label)
        layout.add_widget(self.toggle_button)
        return layout

    def toggle_generation(self, instance):
        if not self.is_running:
            self.is_running = True
            self.toggle_button.text = "Stop Generating"
            # Run the generation loop in a background thread
            threading.Thread(target=self.generation_loop, daemon=True).start()
        else:
            self.is_running = False
            self.toggle_button.text = "Start Generating"
            self.update_status("Status: Stopped")

    def update_status(self, text):
        # Update the UI on the main thread safely
        Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', text))

    def generation_loop(self):
        url = "https://api.discord.gx.games/v1/direct-fulfillment"
        payload = {
            "partnerUserId": "0770c0a8152ccab26e014e5733a1f07a2940ef8826366709271b28605acc458f"
        }
        
        while self.is_running:
            try:
                self.update_status("Sending request...")
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    response_json = response.json()
                    token_value = response_json.get('token')
                    if token_value:
                        result = f"https://discord.com/billing/partner-promotions/1180231712274387115/{token_value}\n"
                        with open("nitro-promo-codes.txt", "a") as file:
                            file.write(result)
                        self.update_status("Token found and saved!")
                    else:
                        self.update_status("Token not found in response.")
                else:
                    self.update_status(f"Failed (Status: {response.status_code})")
            except Exception as e:
                self.update_status(f"Error: {str(e)}")
            
            # Delay to prevent rapid rate limiting and allow thread termination
            time.sleep(2)

if __name__ == '__main__':
    PromoGeneratorApp().run()
