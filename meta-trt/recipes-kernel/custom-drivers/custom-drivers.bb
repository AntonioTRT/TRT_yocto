SUMMARY = "Custom Hardware Drivers for TRT Devices"
DESCRIPTION = "Custom kernel modules and drivers for specific hardware components"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

inherit module

SRC_URI = "file://custom-driver.c \
           file://Makefile \
           file://custom-driver.h"

S = "${WORKDIR}"

# Kernel modules needed for various hardware
RDEPENDS_${PN} += "\
    kernel-module-i2c-dev \
    kernel-module-spi-dev \
    kernel-module-gpio-mockup \
    kernel-module-w1-gpio \
    kernel-module-w1-therm \
    kernel-module-dht22 \
"

do_install() {
    # Install the custom kernel module
    install -d ${D}${base_libdir}/modules/${KERNEL_VERSION}/extra
    install -m 0644 ${S}/custom-driver.ko ${D}${base_libdir}/modules/${KERNEL_VERSION}/extra/
    
    # Install module configuration
    install -d ${D}${sysconfdir}/modules-load.d
    echo "custom-driver" > ${D}${sysconfdir}/modules-load.d/custom-hardware.conf
    
    # Install hardware initialization script
    install -d ${D}${sysconfdir}/init.d
    install -m 0755 ${S}/init-hardware.sh ${D}${sysconfdir}/init.d/
}

FILES_${PN} = "\
    ${base_libdir}/modules/${KERNEL_VERSION}/extra/custom-driver.ko \
    ${sysconfdir}/modules-load.d/custom-hardware.conf \
    ${sysconfdir}/init.d/init-hardware.sh \
"