# TRT Yocto Project

Este es un meta-layer personalizado de Yocto Project diseñado para trabajar con múltiples plataformas de hardware industriales y de desarrollo.

## Plataformas Soportadas

- **Raspberry Pi** (todos los modelos)
- **BeagleBone Black/Industrial**
- **NXP i.MX7**

## Características

- Configuraciones optimizadas para cada plataforma
- Imágenes personalizadas con software industrial
- Soporte para conectividad IoT
- Herramientas de desarrollo incluidas

## Estructura del Proyecto

```
meta-trt/
├── conf/
│   ├── layer.conf                    # Configuración del layer
│   ├── machine/                      # Definiciones de máquinas
│   │   ├── raspberrypi-trt.conf     # Configuración Raspberry Pi
│   │   ├── beaglebone-trt.conf      # Configuración BeagleBone
│   │   └── imx7-trt.conf            # Configuración i.MX7
│   └── distro/
│       └── trt-distro.conf          # Configuración de distribución
├── recipes-core/
│   ├── images/                       # Recetas de imágenes
│   │   ├── trt-base-image.bb        # Imagen base
│   │   ├── trt-industrial-image.bb  # Imagen industrial
│   │   └── trt-development-image.bb # Imagen de desarrollo
│   └── packagegroups/               # Grupos de paquetes
│       └── packagegroup-trt-base.bb
├── recipes-connectivity/            # Conectividad IoT
├── recipes-industrial/             # Software industrial
└── scripts/
    ├── setup-environment.sh        # Script de configuración
    └── build-all-platforms.sh      # Build para todas las plataformas
```

## Instalación y Configuración

### Prerequisitos

**Para Linux (Recomendado):**
- Ubuntu 20.04 LTS o superior (recomendado)
- Al menos 50GB de espacio libre en disco
- 8GB de RAM (16GB recomendado)

**Para Windows (con WSL2):**
- Windows 10/11 con WSL2 habilitado
- Ubuntu 20.04 LTS en WSL2
- Al menos 50GB de espacio libre en disco
- 8GB de RAM (16GB recomendado)

### 1. Instalar dependencias del sistema

**En Linux:**
```bash
sudo apt update
sudo apt install -y gawk wget git diffstat unzip texinfo gcc build-essential \
chrpath socat cpio python3 python3-pip python3-pexpect xz-utils debianutils \
iputils-ping python3-git python3-jinja2 libegl1-mesa libsdl1.2-dev pylint3 \
xterm python3-subunit mesa-common-dev zstd liblz4-tool
```

**En Windows (WSL2):**
1. Instalar WSL2 y Ubuntu 20.04 LTS
2. Ejecutar el mismo comando de Linux dentro de WSL2
3. Configurar el límite de memoria de WSL2 en `.wslconfig`:

### 2. Clonar Poky y layers necesarios

```bash
mkdir ~/yocto-trt
cd ~/yocto-trt

# Clonar Poky (Yocto reference distribution)
git clone -b scarthgap https://git.yoctoproject.org/poky

# Clonar meta-openembedded
git clone -b scarthgap https://github.com/openembedded/meta-openembedded.git

# Clonar meta-raspberrypi
git clone -b scarthgap https://github.com/agherzan/meta-raspberrypi.git

# Clonar meta-freescale para i.MX7
git clone -b scarthgap https://github.com/Freescale/meta-freescale.git

# Clonar meta-ti para BeagleBone
git clone -b scarthgap https://github.com/meta-ti/meta-ti.git

# Clonar este meta-layer
git clone https://github.com/AntonioTRT/TRT_yocto.git meta-trt
```

### 3. Configurar el entorno de build

```bash
cd ~/yocto-trt
source poky/oe-init-build-env build-trt
```

### 4. Configurar bblayers.conf

Editar `conf/bblayers.conf`:

```bitbake
# POKY_BBLAYERS_CONF_VERSION is increased each time build/conf/bblayers.conf
# changes incompatibly
POKY_BBLAYERS_CONF_VERSION = "2"

BBPATH = "${TOPDIR}"
BBFILES ?= ""

BBLAYERS ?= " \\
  /home/user/yocto-trt/poky/meta \\
  /home/user/yocto-trt/poky/meta-poky \\
  /home/user/yocto-trt/poky/meta-yocto-bsp \\
  /home/user/yocto-trt/meta-openembedded/meta-oe \\
  /home/user/yocto-trt/meta-openembedded/meta-python \\
  /home/user/yocto-trt/meta-openembedded/meta-networking \\
  /home/user/yocto-trt/meta-raspberrypi \\
  /home/user/yocto-trt/meta-freescale \\
  /home/user/yocto-trt/meta-ti/meta-ti-bsp \\
  /home/user/yocto-trt/meta-trt \\
  "
```

### 5. Configurar local.conf para cada plataforma

#### Para Raspberry Pi:
```bash
echo 'MACHINE = "raspberrypi-trt"' >> conf/local.conf
echo 'DISTRO = "trt-distro"' >> conf/local.conf
```

#### Para BeagleBone:
```bash
echo 'MACHINE = "beaglebone-trt"' >> conf/local.conf
echo 'DISTRO = "trt-distro"' >> conf/local.conf
```

#### Para i.MX7:
```bash
echo 'MACHINE = "imx7-trt"' >> conf/local.conf
echo 'DISTRO = "trt-distro"' >> conf/local.conf
```

## Build de Imágenes

### Imagen base (minimal)
```bash
bitbake trt-base-image
```

### Imagen industrial (con herramientas industriales)
```bash
bitbake trt-industrial-image
```

### Imagen de desarrollo (con herramientas de debugging)
```bash
bitbake trt-development-image
```

**Credenciales por defecto:**
- Usuario: `root`
- Contraseña: `2020`
- Usuario desarrollador: `developer`
- Contraseña desarrollador: `2020`

## Scripts de Automatización

### Build para todas las plataformas
```bash
./scripts/build-all-platforms.sh
```

### Configuración rápida del entorno
```bash
source ./scripts/setup-environment.sh
```

## Personalización

### Agregar nuevos paquetes

1. Crear recetas en `recipes-*/`
2. Agregar al grupo de paquetes correspondiente
3. Incluir en la imagen deseada

### Modificar configuraciones de máquina

Editar los archivos en `conf/machine/` para ajustar configuraciones específicas de hardware.

### Personalizar la distribución

Modificar `conf/distro/trt-distro.conf` para cambiar configuraciones globales.

## Características Incluidas

### Conectividad IoT
- WiFi y Bluetooth configurados
- Soporte para protocolos industriales (Modbus, OPC-UA)
- Cliente MQTT
- Servidor web ligero

### Herramientas Industriales
- Herramientas de monitoreo del sistema
- Interfaces para sensores industriales
- Logging y telemetría
- Watchdog configurado

### Desarrollo
- SSH habilitado por defecto
- Herramientas de debugging (gdb, strace)
- Python 3 con librerías científicas
- Git y herramientas de desarrollo

## Contribución

1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit los cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## Contacto

Antonio TRT - [@AntonioTRT](https://github.com/AntonioTRT)

Project Link: [https://github.com/AntonioTRT/TRT_yocto](https://github.com/AntonioTRT/TRT_yocto)

## Troubleshooting

### Problemas comunes

1. **Error de espacio en disco**: Asegurar al menos 50GB libres
2. **Dependencias faltantes**: Verificar que todas las dependencias estén instaladas
3. **Versiones incompatibles**: Usar la misma rama (scarthgap) para todos los layers

### Logs útiles

- Build logs: `tmp/work/*/temp/log.do_*`
- Kernel logs: `tmp/work/*linux*/temp/`
- Package logs: `tmp/work/*/temp/`

### Limpiar builds

```bash
# Limpiar un paquete específico
bitbake -c cleanall <package-name>

# Limpiar todo
rm -rf tmp sstate-cache
```

## Ejecución automática de TRT Project

El programa `trt_project` es el software que se ejecutará por defecto al arrancar la imagen generada. Este programa puede mostrar información del sistema, versión, autor, o servir como pantalla de bienvenida (About this system).

La integración se realiza mediante una receta Yocto que instala el contenido de la carpeta `trt_project` y configura un servicio systemd para ejecutarlo automáticamente al inicio.

---

## Verificación rápida de recetas Yocto (`test001.sh`)

El script `test001.sh` permite comprobar rápidamente si la receta `trt-project` está correctamente integrada y lista para compilar, sin necesidad de construir toda la imagen.

### ¿Qué hace?
- Verifica sintaxis y dependencias de la receta (`bitbake -c parse`)
- Comprueba acceso a fuentes (`bitbake -c fetch`)
- Intenta compilar solo la receta (`bitbake trt-project`)
- Muestra variables de entorno relevantes
- Permite verificar que el archivo y la integración de `trt_project` funcionan correctamente

### Uso

1. Abre una terminal en Linux o WSL (no funciona en PowerShell de Windows)
2. Navega a la raíz del proyecto:
   ```bash
   cd /ruta/a/TU/PROYECTO/TRT_yocto
   ```
3. Da permisos de ejecución al script:
   ```bash
   chmod +x test001.sh
   ```
4. Inicializa el entorno Yocto:
   ```bash
   source poky/oe-init-build-env
   ```
5. Ejecuta el script:
   ```bash
   ./test001.sh
   ```

Si no hay errores, la receta y el programa `trt_project` están bien integrados y listos para usarse en la imagen.

---

## Configuración de pines y buses por hardware

Los archivos `conf/hwmap-raspberrypi.conf` y `conf/hwmap-beaglebone.conf` definen el mapeo lógico de buses y pines (I2C, UART, ADC, PWM, etc.) para cada plataforma. Tus scripts y aplicaciones pueden leer `/etc/hwmap.conf` para acceder a los dispositivos correctos de forma portable, sin importar la board.

Ejemplo de uso en Python:
```python
import os

def get_hw_value(key, default=None):
    with open('/etc/hwmap.conf') as f:
        for line in f:
            if line.startswith(key + '='):
                return line.strip().split('=',1)[1]
    return default

adc1 = get_hw_value('ADC1_DEV')
pwm1 = get_hw_value('PWM1_DEV')
```

Esto permite que tu código sea portable y fácil de mantener entre diferentes plataformas.

## Nota de prueba
Este es un cambio simple para probar el flujo de commit y push en el repositorio TRT_yocto.