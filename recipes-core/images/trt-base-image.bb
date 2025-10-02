SUMMARY = "TRT Base Image - Minimal industrial Linux image"
DESCRIPTION = "A minimal image with basic industrial functionality for embedded systems"

IMAGE_FEATURES += "splash"

IMAGE_INSTALL = "\
    packagegroup-core-boot \
    packagegroup-trt-base-base \
    packagegroup-trt-base-connectivity \
    trt-config \
    arduino-drivers \
    custom-drivers \
    ${CORE_IMAGE_EXTRA_INSTALL} \
"

IMAGE_LINGUAS = " "

LICENSE = "MIT"

inherit core-image

IMAGE_ROOTFS_SIZE ?= "8192"
IMAGE_ROOTFS_EXTRA_SPACE_append = "${@bb.utils.contains("DISTRO_FEATURES", "systemd", " + 4096", "", d)}"

# Enable SSH root login for development (disable in production)
set_permissions() {
    # Allow root login via SSH (for development only)
    if [ -f ${IMAGE_ROOTFS}/etc/ssh/sshd_config ]; then
        sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' ${IMAGE_ROOTFS}/etc/ssh/sshd_config
    fi
    
    # Set default root password: 2020
    echo 'root:2020' | chpasswd -R ${IMAGE_ROOTFS}
}

ROOTFS_POSTPROCESS_COMMAND += "set_permissions; "