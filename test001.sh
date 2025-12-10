#!/bin/bash
# test001.sh - Verificación rápida de la receta trt-project en Yocto
#
# Instrucciones de uso:
#
# 1. Abre una terminal en Linux o WSL (no funciona en PowerShell de Windows)
# 2. Navega a la raíz de tu proyecto Yocto (ejemplo: cd /mnt/c/repos/TRT_yocto)
# 3. Da permisos de ejecución al script:
#      chmod +x test001.sh
# 4. Inicializa el entorno Yocto:
#      source poky/oe-init-build-env
# 5. Ejecuta el script:
#      ./test001.sh
#
# El script verificará sintaxis, dependencias, fetch y build de la receta 'trt-project'.
# Si no hay errores, tu receta está bien integrada.
# =============================================================

set -e

RECIPE=trt-project

# 1. Verificar sintaxis y dependencias
printf "\n== 1. Verificando sintaxis y dependencias (parse)...\n"
bitbake -c parse $RECIPE

# 2. Verificar acceso a fuentes
printf "\n== 2. Verificando acceso a fuentes (fetch)...\n"
bitbake -c fetch $RECIPE

# 3. Intentar compilación de la receta
printf "\n== 3. Intentando compilación de la receta (build)...\n"
bitbake $RECIPE

# 4. Mostrar variables de entorno relevantes (opcional)
printf "\n== 4. Variables de entorno de la receta (opcional):\n"
bitbake -e $RECIPE | grep ^FILE

printf "\n== 5. Listo. Si no hubo errores, la receta está bien integrada.\n"
