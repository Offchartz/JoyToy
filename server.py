import socket
import json
import time
import threading
import customtkinter as ctk
import vgamepad as vg
from pynput.mouse import Controller as MouseController, Button

gamepad = vg.VX360Gamepad()
mouse = MouseController()

BUTTON_MAP = {
    "A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A, "B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "X": vg.XUSB_BUTTON.XUSB_GAMEPAD_X, "Y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "LB": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, "RB": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START, "BACK": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    "GUIDE": vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE, "L3": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    "R3": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    "DPAD_UP": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, "DPAD_DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    "DPAD_LEFT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT, "DPAD_RIGHT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class ServerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Universal Controller")
        self.geometry("400x500")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.mouse_sens = 30
        
        # Header
        self.header = ctk.CTkLabel(self, text="PC Gamepad Server", font=("Segoe UI", 26, "bold"))
        self.header.pack(pady=(35, 25))
        
        # IP Address Card
        self.ip_card = ctk.CTkFrame(self, corner_radius=12)
        self.ip_card.pack(pady=10, padx=35, fill="x")
        self.ip_title = ctk.CTkLabel(self.ip_card, text="Phone App IP Address", font=("Segoe UI", 12), text_color="gray70")
        self.ip_title.pack(pady=(15, 0))
        self.ip_value = ctk.CTkLabel(self.ip_card, text=get_local_ip(), font=("Segoe UI", 24, "bold"), text_color="#3a7ebf")
        self.ip_value.pack(pady=(0, 15))
        
        # Sensitivity Card
        self.settings_card = ctk.CTkFrame(self, corner_radius=12)
        self.settings_card.pack(pady=10, padx=35, fill="x")
        
        self.sens_header = ctk.CTkFrame(self.settings_card, fg_color="transparent")
        self.sens_header.pack(fill="x", padx=20, pady=(15, 5))
        self.sens_label = ctk.CTkLabel(self.sens_header, text="Mouse Sensitivity", font=("Segoe UI", 13))
        self.sens_label.pack(side="left")
        self.sens_val_label = ctk.CTkLabel(self.sens_header, text=str(self.mouse_sens), font=("Segoe UI", 13, "bold"))
        self.sens_val_label.pack(side="right")
        
        self.sens_slider = ctk.CTkSlider(self.settings_card, from_=5, to=100, command=self.update_sens)
        self.sens_slider.set(self.mouse_sens)
        self.sens_slider.pack(pady=(0, 20), padx=20, fill="x")
        
        # Status Label
        self.status_label = ctk.CTkLabel(self, text="● Server Stopped", text_color="#ff5555", font=("Segoe UI", 13, "bold"))
        self.status_label.pack(pady=(25, 10))
        
        # Button Container
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(padx=35, fill="x")
        
        self.start_btn = ctk.CTkButton(self.btn_frame, text="START", font=("Segoe UI", 14, "bold"), height=45, corner_radius=8, command=self.start_server)
        self.start_btn.pack(side="left", expand=True, padx=(0, 5), fill="x")
        
        self.stop_btn = ctk.CTkButton(self.btn_frame, text="STOP", font=("Segoe UI", 14, "bold"), height=45, corner_radius=8, fg_color="#ff4c4c", hover_color="#ff3333", state="disabled", command=self.stop_server)
        self.stop_btn.pack(side="right", expand=True, padx=(5, 0), fill="x")
        
        # Footer
        self.footer = ctk.CTkLabel(self, text="made by off chartz", font=("Segoe UI", 11), text_color="gray40")
        self.footer.pack(side="bottom", pady=15)
        
        self.is_running = False

    def update_sens(self, value):
        self.mouse_sens = int(value)
        self.sens_val_label.configure(text=str(self.mouse_sens))

    def start_server(self):
        self.is_running = True
        self.status_label.configure(text="● Running on UDP 8080", text_color="#50fa7b")
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        threading.Thread(target=self.udp_listener, daemon=True).start()

    def stop_server(self):
        self.is_running = False
        self.status_label.configure(text="● Server Stopped", text_color="#ff5555")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        gamepad.reset()
        gamepad.update()

    def udp_listener(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", 8080))
        sock.settimeout(1.0)
        last_packet = time.time()

        while self.is_running:
            try:
                data, _ = sock.recvfrom(1024)
                msg = json.loads(data.decode("utf-8"))
                last_packet = time.time()

                if "btn" in msg:
                    btn_name, action = msg["btn"], msg["state"]
                    if btn_name == "M_LEFT":
                        mouse.press(Button.left) if action == "DOWN" else mouse.release(Button.left)
                    elif btn_name == "M_RIGHT":
                        mouse.press(Button.right) if action == "DOWN" else mouse.release(Button.right)
                    elif btn_name in ["LT", "RT"]:
                        val = 255 if action == "DOWN" else 0
                        gamepad.left_trigger(value=val) if btn_name == "LT" else gamepad.right_trigger(value=val)
                    else:
                        btn = BUTTON_MAP.get(btn_name)
                        if btn:
                            gamepad.press_button(button=btn) if action == "DOWN" else gamepad.release_button(button=btn)
                    gamepad.update()

                elif "stick" in msg:
                    x_val = int(max(min(msg["x"], 1.0), -1.0) * 32767)
                    y_val = int(max(min(-msg["y"], 1.0), -1.0) * 32767)
                    if msg["stick"] == "L":
                        gamepad.left_joystick(x_value=x_val, y_value=y_val)
                    elif msg["stick"] == "R":
                        gamepad.right_joystick(x_value=x_val, y_value=y_val)
                    gamepad.update()

            except socket.timeout:
                if time.time() - last_packet > 2.0:
                    gamepad.reset()
                    gamepad.update()
            except Exception:
                pass
        
        # Close the socket when the loop breaks
        sock.close()

if __name__ == "__main__":
    app = ServerGUI()
    app.mainloop()

# import socket
# import json
# import time
# import threading
# import customtkinter as ctk
# import vgamepad as vg
# from pynput.mouse import Controller as MouseController, Button
# from pynput.keyboard import Controller as KeyboardController

# gamepad = vg.VX360Gamepad()
# mouse = MouseController()
# keyboard = KeyboardController()

# BUTTON_MAP = {
#     "A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A, "B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
#     "X": vg.XUSB_BUTTON.XUSB_GAMEPAD_X, "Y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
#     "LB": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, "RB": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
#     "START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START, "BACK": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
#     "GUIDE": vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE, "L3": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
#     "R3": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
#     "DPAD_UP": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, "DPAD_DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
#     "DPAD_LEFT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT, "DPAD_RIGHT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
# }

# def get_local_ip():
#     try:
#         s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         s.connect(("8.8.8.8", 80))
#         ip = s.getsockname()[0]
#         s.close()
#         return ip
#     except Exception:
#         return "127.0.0.1"

# class ServerGUI(ctk.CTk):
#     def __init__(self):
#         super().__init__()
#         self.title("Universal Controller Server")
#         self.geometry("450x600")
#         ctk.set_appearance_mode("dark")
#         self.mouse_sens = 30
#         self.key_mappings = {} # Stores active button-to-key binds
        
#         self.title_label = ctk.CTkLabel(self, text="PC Gamepad Server", font=("Arial", 24, "bold"))
#         self.title_label.pack(pady=(20, 10))
        
#         # Network Info Card
#         self.ip_frame = ctk.CTkFrame(self)
#         self.ip_frame.pack(pady=5, padx=30, fill="x")
#         self.ip_label = ctk.CTkLabel(self.ip_frame, text=f"Phone App IP: {get_local_ip()}", font=("Arial", 16, "bold"), text_color="#00BFFF")
#         self.ip_label.pack(pady=10)
        
#         # Settings Card
#         self.settings_frame = ctk.CTkFrame(self)
#         self.settings_frame.pack(pady=5, padx=30, fill="x")
#         self.sens_label = ctk.CTkLabel(self.settings_frame, text=f"Mouse Sensitivity: {self.mouse_sens}")
#         self.sens_label.pack(pady=(10, 0))
#         self.sens_slider = ctk.CTkSlider(self.settings_frame, from_=5, to=100, command=self.update_sens)
#         self.sens_slider.set(self.mouse_sens)
#         self.sens_slider.pack(pady=10, padx=20)
        
#         # Keyboard Mapping Card
#         self.map_frame = ctk.CTkFrame(self)
#         self.map_frame.pack(pady=5, padx=30, fill="x")
#         ctk.CTkLabel(self.map_frame, text="Keyboard Mapping (e.g. DPAD_UP -> w)", font=("Arial", 12, "bold")).pack(pady=5)
        
#         self.map_inputs = ctk.CTkFrame(self.map_frame, fg_color="transparent")
#         self.map_inputs.pack(pady=5)
        
#         self.btn_dropdown = ctk.CTkOptionMenu(self.map_inputs, values=list(BUTTON_MAP.keys()), width=120)
#         self.btn_dropdown.pack(side="left", padx=5)
        
#         self.key_entry = ctk.CTkEntry(self.map_inputs, placeholder_text="key", width=50)
#         self.key_entry.pack(side="left", padx=5)
        
#         self.add_map_btn = ctk.CTkButton(self.map_inputs, text="Bind", width=60, command=self.add_mapping)
#         self.add_map_btn.pack(side="left", padx=5)
        
#         self.active_maps_label = ctk.CTkLabel(self.map_frame, text="Active Binds: None", font=("Arial", 12))
#         self.active_maps_label.pack(pady=5)
        
#         # Server Controls
#         self.status_label = ctk.CTkLabel(self, text="Server Stopped", text_color="#ff4c4c", font=("Arial", 16))
#         self.status_label.pack(pady=(10, 5))
#         self.start_btn = ctk.CTkButton(self, text="Start Server", font=("Arial", 16), height=40, command=self.start_server)
#         self.start_btn.pack(pady=10)
        
#         self.is_running = False

#     def update_sens(self, value):
#         self.mouse_sens = int(value)
#         self.sens_label.configure(text=f"Mouse Sensitivity: {self.mouse_sens}")

#     def add_mapping(self):
#         controller_btn = self.btn_dropdown.get()
#         keyboard_key = self.key_entry.get().lower()
#         if keyboard_key:
#             self.key_mappings[controller_btn] = keyboard_key
#             binds_text = " | ".join([f"{k}->{v}" for k, v in self.key_mappings.items()])
#             self.active_maps_label.configure(text=f"Active Binds: {binds_text}")
#             self.key_entry.delete(0, 'end')

#     def start_server(self):
#         self.is_running = True
#         self.status_label.configure(text="Running on UDP 8080", text_color="#4cff4c")
#         self.start_btn.configure(state="disabled")
#         threading.Thread(target=self.udp_listener, daemon=True).start()

#     def udp_listener(self):
#         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         sock.bind(("0.0.0.0", 8080))
#         sock.settimeout(1.0)
#         last_packet = time.time()

#         while self.is_running:
#             try:
#                 data, _ = sock.recvfrom(1024)
#                 msg = json.loads(data.decode("utf-8"))
#                 last_packet = time.time()

#                 if "btn" in msg:
#                     btn_name, action = msg["btn"], msg["state"]
                    
#                     # 1. Check if button is mapped to a keyboard key
#                     if btn_name in self.key_mappings:
#                         key_char = self.key_mappings[btn_name]
#                         if action == "DOWN": keyboard.press(key_char)
#                         elif action == "UP": keyboard.release(key_char)
                    
#                     # 2. Check for Mouse Clicks
#                     elif btn_name == "M_LEFT":
#                         mouse.press(Button.left) if action == "DOWN" else mouse.release(Button.left)
#                     elif btn_name == "M_RIGHT":
#                         mouse.press(Button.right) if action == "DOWN" else mouse.release(Button.right)
                    
#                     # 3. Process as standard Xbox Gamepad
#                     elif btn_name in ["LT", "RT"]:
#                         val = 255 if action == "DOWN" else 0
#                         gamepad.left_trigger(value=val) if btn_name == "LT" else gamepad.right_trigger(value=val)
#                     else:
#                         btn = BUTTON_MAP.get(btn_name)
#                         if btn:
#                             gamepad.press_button(button=btn) if action == "DOWN" else gamepad.release_button(button=btn)
                    
#                     gamepad.update()

#                 elif "stick" in msg:
#                     x_val = int(max(min(msg["x"], 1.0), -1.0) * 32767)
#                     y_val = int(max(min(-msg["y"], 1.0), -1.0) * 32767)
#                     if msg["stick"] == "L":
#                         gamepad.left_joystick(x_value=x_val, y_value=y_val)
#                     elif msg["stick"] == "R":
#                         gamepad.right_joystick(x_value=x_val, y_value=y_val)
#                     gamepad.update()

#             except socket.timeout:
#                 if time.time() - last_packet > 2.0:
#                     gamepad.reset()
#                     gamepad.update()
#             except Exception:
#                 pass

# if __name__ == "__main__":
#     app = ServerGUI()
#     app.mainloop()

# import socket
# import json
# import time
# import threading
# import customtkinter as ctk
# import vgamepad as vg
# from pynput.mouse import Controller as MouseController, Button

# # Initialize hardware emulators
# gamepad = vg.VX360Gamepad()
# mouse = MouseController()

# BUTTON_MAP = {
#     "A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A, "B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
#     "X": vg.XUSB_BUTTON.XUSB_GAMEPAD_X, "Y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
#     "LB": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, "RB": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
#     "START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START, "BACK": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
#     "GUIDE": vg.XUSB_BUTTON.XUSB_GAMEPAD_GUIDE, "L3": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
#     "R3": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
#     "DPAD_UP": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP, "DPAD_DOWN": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
#     "DPAD_LEFT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT, "DPAD_RIGHT": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
# }

# class ServerGUI(ctk.CTk):
#     def __init__(self):
#         super().__init__()
#         self.title("Universal Wireless Controller")
#         self.geometry("400x250")
#         ctk.set_appearance_mode("dark")
        
#         self.status_label = ctk.CTkLabel(self, text="Server Stopped", text_color="#ff4c4c", font=("Arial", 20, "bold"))
#         self.status_label.pack(pady=30)
        
#         self.start_btn = ctk.CTkButton(self, text="Start Server", font=("Arial", 16), command=self.start_server)
#         self.start_btn.pack(pady=10)
        
#         self.is_running = False

#     def start_server(self):
#         self.is_running = True
#         self.status_label.configure(text="Running on UDP 8080", text_color="#4cff4c")
#         self.start_btn.configure(state="disabled")
#         threading.Thread(target=self.udp_listener, daemon=True).start()

#     def udp_listener(self):
#         sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         sock.bind(("0.0.0.0", 8080))
#         sock.settimeout(1.0)
#         last_packet = time.time()

#         while self.is_running:
#             try:
#                 data, _ = sock.recvfrom(1024)
#                 msg = json.loads(data.decode("utf-8"))
#                 last_packet = time.time()

#                 if "btn" in msg:
#                     btn_name, action = msg["btn"], msg["state"]
                    
#                     if btn_name == "M_LEFT":
#                         mouse.press(Button.left) if action == "DOWN" else mouse.release(Button.left)
#                     elif btn_name == "M_RIGHT":
#                         mouse.press(Button.right) if action == "DOWN" else mouse.release(Button.right)
#                     elif btn_name in ["LT", "RT"]:
#                         val = 255 if action == "DOWN" else 0
#                         gamepad.left_trigger(value=val) if btn_name == "LT" else gamepad.right_trigger(value=val)
#                     else:
#                         btn = BUTTON_MAP.get(btn_name)
#                         if btn:
#                             gamepad.press_button(button=btn) if action == "DOWN" else gamepad.release_button(button=btn)
#                     gamepad.update()

#                 elif "stick" in msg:
#                     x_val = int(max(min(msg["x"], 1.0), -1.0) * 32767)
#                     y_val = int(max(min(-msg["y"], 1.0), -1.0) * 32767)
#                     if msg["stick"] == "L":
#                         gamepad.left_joystick(x_value=x_val, y_value=y_val)
#                     elif msg["stick"] == "R":
#                         gamepad.right_joystick(x_value=x_val, y_value=y_val)
#                     gamepad.update()

#             except socket.timeout:
#                 if time.time() - last_packet > 2.0:
#                     gamepad.reset()
#                     gamepad.update()
#             except Exception as e:
#                 print(f"Error: {e}")

# if __name__ == "__main__":
#     app = ServerGUI()
#     app.mainloop()