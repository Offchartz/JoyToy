# JoyToy 🎮

Turn your Android phone into a fully customizable, wireless Xbox 360 controller and PC mouse over Wi-Fi. 
Made by **off chartz**.

## Features
* **Drag-and-Drop Layout Canvas:** Move, resize, add, and delete buttons or joysticks directly on your phone screen. Your layout saves automatically.
* **True Hardware Emulation:** The PC reads the app as a genuine physical Xbox 360 controller using XInput.
* **Integrated Mouse Control:** Control your Windows desktop cursor with the right joystick and trigger mouse clicks.
* **Low-Latency Wi-Fi Connection:** Communicates instantly via local network UDP sockets (Port 8080).
* **Modern PC Dashboard:** Automatically detects your local IP address for easy pairing and features a live mouse sensitivity slider.

## 📥 How to Install (For Gamers)
You do not need to install Python or any coding tools to use JoyToy.

1. Go to the **Releases** tab on the right side of this GitHub page.
2. **For Android:** Download and install `JoyToy.apk` on your phone.
3. **For PC:** Download and run `JoyToy_Setup.exe`. This installer will automatically set up the required ViGEmBus controller driver and place a JoyToy shortcut on your desktop.
4. Ensure both your PC and phone are connected to the same Wi-Fi network.
5. Open the JoyToy PC app, note the displayed IP address, and type it into your phone!

## 💻 How to Build (For Developers)
If you want to view, modify, or compile the source code yourself:

1. Clone this repository to your local machine.
2. Run `setup_dev.bat` (or manually run `pip install -r requirements.txt`) to install the required Python dependencies (`vgamepad`, `pynput`, `customtkinter`, `pyinstaller`).
3. Run `python server.py` to test the PC server GUI.
4. To compile the standalone executable, use PyInstaller:
   ```bash
   pyinstaller --noconsole --onefile --collect-data vgamepad --icon=server_icon.ico --name JoyToy server.py