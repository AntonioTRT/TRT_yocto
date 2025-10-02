# ui.py - Simple graphical interface

import tkinter as tk
from tkinter import ttk
import config
import datas

class TRTInterface:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title(f"{config.NOMBRE_PROGRAMA} v{config.VERSION}")
        self.window.geometry("600x400")
        
        # Remove the small icon from title bar (feather/python icon)
        self.window.wm_iconbitmap(bitmap="")
            
        self.setup_ui()
        
    def setup_ui(self):
        # Title
        title_label = tk.Label(self.window, text=config.NOMBRE_PROGRAMA, 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame for information
        info_frame = tk.LabelFrame(self.window, text="System Information", 
                                  font=("Arial", 12))
        info_frame.pack(padx=20, pady=10, fill="x")
        
        # Information labels
        self.temp_label = tk.Label(info_frame, text=f"Temperature: {datas.temperatura_actual}°C")
        self.temp_label.pack(anchor="w", padx=10, pady=5)
        
        self.contador_label = tk.Label(info_frame, text=f"Counter: {datas.contador}")
        self.contador_label.pack(anchor="w", padx=10, pady=5)
        
        self.estado_label = tk.Label(info_frame, text=f"Status: {datas.estado_sistema}")
        self.estado_label.pack(anchor="w", padx=10, pady=5)
        
        self.resultado_label = tk.Label(info_frame, text=f"Last sum: {datas.resultado_suma}")
        self.resultado_label.pack(anchor="w", padx=10, pady=5)
        
        # Frame for controls
        control_frame = tk.LabelFrame(self.window, text="Controls", 
                                     font=("Arial", 12))
        control_frame.pack(padx=20, pady=10, fill="x")
        
        # Calculate button
        calc_button = tk.Button(control_frame, text="Run Calculation", 
                               command=self.ejecutar_calculo,
                               bg="#4CAF50", fg="white", font=("Arial", 10))
        calc_button.pack(side="left", padx=10, pady=10)
        
        # Update button
        update_button = tk.Button(control_frame, text="Update Data", 
                                 command=self.actualizar_interfaz,
                                 bg="#2196F3", fg="white", font=("Arial", 10))
        update_button.pack(side="left", padx=10, pady=10)
        
        # Exit button
        exit_button = tk.Button(control_frame, text="Exit", 
                               command=self.window.quit,
                               bg="#f44336", fg="white", font=("Arial", 10))
        exit_button.pack(side="right", padx=10, pady=10)
        
        # Frame for configuration
        config_frame = tk.LabelFrame(self.window, text="Configuration", 
                                    font=("Arial", 12))
        config_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Show configuration
        config_text = tk.Text(config_frame, height=8, width=70)
        config_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Load configuration
        config_info = f"""Port: {config.PUERTO}
Max Temperature: {config.TEMPERATURA_MAXIMA}°C
Number X: {config.NUMERO_X}
Number Y: {config.NUMERO_Y}
Version: {config.VERSION}"""
        
        config_text.insert("1.0", config_info)
        config_text.config(state="disabled")  # Read only
        
        self.config_text = config_text
        
    def ejecutar_calculo(self):
        """Execute calculation and update result"""
        datas.resultado_suma = config.NUMERO_X + config.NUMERO_Y
        datas.contador += 1
        datas.estado_sistema = "calculating"
        self.actualizar_interfaz()
        
    def actualizar_interfaz(self):
        """Update all values in interface"""
        self.temp_label.config(text=f"Temperature: {datas.temperatura_actual}°C")
        self.contador_label.config(text=f"Counter: {datas.contador}")
        self.estado_label.config(text=f"Status: {datas.estado_sistema}")
        self.resultado_label.config(text=f"Last sum: {datas.resultado_suma}")
        
    def run(self):
        """Run the interface"""
        print("🖥️ Starting graphical interface...")
        self.window.mainloop()

def mostrar_interfaz():
    """Function to show interface from main.py"""
    try:
        app = TRTInterface()
        app.run()
    except Exception as e:
        print(f"❌ Error in graphical interface: {e}")
        print("💡 Running in console mode...")
        return False
    return True

if __name__ == "__main__":
    mostrar_interfaz()