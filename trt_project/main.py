# main.py - Simple main program

import config
import datas
import ui

def main():
    print("Hello world")
    
    # Use config variables
    print(f"Program: {config.NOMBRE_PROGRAMA}")
    print(f"Port: {config.PUERTO}")
    
    # Simple calculation
    datas.resultado_suma = config.NUMERO_X + config.NUMERO_Y
    print(f"Sum: {config.NUMERO_X} + {config.NUMERO_Y} = {datas.resultado_suma}")
    
    # Update variables
    datas.contador += 1
    datas.estado_sistema = "running"
    
    print(f"Counter: {datas.contador}")
    print(f"Status: {datas.estado_sistema}")
    
    # Show graphical interface
    print("\n🚀 Starting graphical interface...")
    if not ui.mostrar_interfaz():
        print("⚠️ Graphical interface not available, continuing in console")

if __name__ == "__main__":
    main()