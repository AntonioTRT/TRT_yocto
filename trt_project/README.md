# TRT Industrial Control - Proyecto Python

Este es el proyecto Python que se ejecutará tanto localmente como en las boards reales.

## Estructura del Proyecto

```
proyecto_python/
├── config.py     # ⚙️ Constantes y parámetros del sistema
├── datas.py      # 📊 Variables dinámicas que cambian durante ejecución
├── programa.py   # 🏭 Programa principal
└── README.md     # 📖 Esta documentación
```

## Descripción de Archivos

### 📁 config.py
- **Propósito**: Contiene todas las CONSTANTES y PARÁMETROS del sistema
- **Contenido**: 
  - Umbrales de temperatura, presión, nivel
  - Configuración de puertos COM, MQTT, web
  - Pines GPIO para diferentes boards
  - Tiempos e intervalos
  - Configuración PID
- **Modificación**: Cambiar valores aquí afecta el comportamiento del sistema

### 📁 datas.py  
- **Propósito**: Variables DINÁMICAS que cambian durante la ejecución
- **Contenido**:
  - Valores actuales de sensores (temperatura, presión, nivel)
  - Estados de relés y actuadores
  - Contadores y estadísticas
  - Históricos de datos
  - Estados de conexión
- **Modificación**: Estas variables se actualizan automáticamente

### 📁 programa.py
- **Propósito**: Programa PRINCIPAL que ejecuta toda la lógica
- **Funcionalidad**:
  - Lee sensores usando configuración de `config.py`
  - Actualiza variables en `datas.py`
  - Ejecuta control PID para temperatura
  - Maneja alarmas y seguridad
  - Proporciona interfaz web en puerto 5000
  - Comunica por MQTT (opcional)

## Cómo Ejecutar

### 1. Instalar dependencias (opcional)
```bash
pip install flask paho-mqtt
```

### 2. Ejecutar el programa
```bash
cd c:\repos\TRT_yocto\proyecto_python
python programa.py
```

### 3. Acceder al dashboard
- **URL**: http://localhost:5000
- **APIs**: 
  - `GET /api/estado` - Estado completo del sistema
  - `GET /api/config` - Configuración actual
  - `POST /api/control_rele` - Controlar relés
  - `POST /api/set_setpoint` - Cambiar temperatura objetivo

## Características

### 🎮 Modo Simulación
- **Configurado en**: `config.py` → `MODO_SIMULACION = True`
- **Función**: Simula sensores sin necesidad de hardware real
- **Ideal para**: Testing en Windows antes de compilar Yocto

### 🏭 Modo Producción
- **Configurado en**: `config.py` → `MODO_SIMULACION = False`
- **Función**: Se conecta a hardware real (GPIO, sensores)
- **Ideal para**: Ejecución en Raspberry Pi, BeagleBone, i.MX7

### ⚙️ Control Automático
- **Control PID** para mantener temperatura
- **Verificación de alarmas** automática
- **Activación de relés** según condiciones
- **Logging** completo de eventos

### 🌐 Interfaz Web
- **Dashboard visual** con estado en tiempo real
- **Control manual** de relés
- **Cambio de setpoints** desde web
- **Históricos** y estadísticas

## Configuraciones Importantes

### En config.py:
```python
# Para testing local
MODO_SIMULACION = True
WEB_PORT = 5000
MQTT_BROKER = "localhost"  # Cambiar por IP real si tienes broker

# Umbrales críticos
TEMP_CRITICA = 30.0      # °C - Alarma crítica
PRESION_ALARMA = 9.0     # bar - Presión máxima
NIVEL_BAJO = 20.0        # % - Nivel mínimo tanque
```

### En datas.py:
```python
# Variables que verás cambiar en tiempo real
temperatura_actual = 22.5
presion_actual = 4.2
nivel_tanque = 65.0
rele_bomba_activo = False
```

## Testing Local vs Boards Reales

| Aspecto | Local (Windows) | Boards Reales |
|---------|----------------|---------------|
| **Sensores** | Simulados con valores aleatorios | Hardware real (GPIO) |
| **Relés** | Simulados en software | Control real de GPIO |
| **Dashboard** | http://localhost:5000 | http://IP_BOARD:5000 |
| **GPIO** | No requiere librerías | RPi.GPIO / Adafruit GPIO |
| **Configuración** | `MODO_SIMULACION = True` | `MODO_SIMULACION = False` |

## Lo Que Verás Al Ejecutar

1. **Consola**: Log de eventos, lecturas de sensores, cambios de estado
2. **Dashboard Web**: Interfaz visual con controles interactivos  
3. **APIs**: Endpoints para integración con otros sistemas
4. **MQTT** (opcional): Publicación de datos en tiempo real

## Equivalencia con Yocto

Este código es **IDÉNTICO** al que se ejecutará en las boards cuando compiles el proyecto Yocto:

- Los mismos archivos van en `/opt/trt/` en las boards
- Se ejecuta automáticamente como servicio systemd
- La interfaz web está disponible en la IP de la board
- Los valores de configuración son los mismos

**¡Es exactamente lo mismo que funcionará en producción!** 🎯