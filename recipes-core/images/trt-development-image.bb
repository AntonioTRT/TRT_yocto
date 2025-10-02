SUMMARY = "TRT Development Image - Development tools and debugging"
DESCRIPTION = "Image with development tools, compilers, and debugging utilities"

require trt-industrial-image.bb

IMAGE_INSTALL += "\
    packagegroup-trt-base-development \
    eclipse-debug-plugins \
    gdb-cross \
    gdbserver \
    tcf-agent \
    openssh-sftp-server \
    nfs-utils \
    nfs-utils-client \
    kernel-devsrc \
    kernel-dev \
    build-essential \
    autotools-dev \
    libtool \
    automake \
    flex \
    bison \
    gawk \
    device-tree-compiler \
    u-boot-tools \
    mtd-utils \
    e2fsprogs-resize2fs \
    parted \
    dosfstools \
    kmod \
    ldd \
    rpm \
    smart \
    opkg \
    opkg-utils \
"

# More space for development tools
IMAGE_ROOTFS_SIZE = "24576"

# Development-specific configurations
configure_development() {
    # Configure NFS for development
    echo '/home *(rw,sync,no_root_squash,no_subtree_check)' >> ${IMAGE_ROOTFS}/etc/exports
    echo '/opt/trt *(rw,sync,no_root_squash,no_subtree_check)' >> ${IMAGE_ROOTFS}/etc/exports
    
    # Enable development services
    systemctl --root=${IMAGE_ROOTFS} enable rpcbind
    systemctl --root=${IMAGE_ROOTFS} enable nfs-server
    
    # Create development user
    useradd --root=${IMAGE_ROOTFS} -m -s /bin/bash developer
    echo 'developer:2020' | chpasswd -R ${IMAGE_ROOTFS}
    
    # Add developer to sudoers
    echo 'developer ALL=(ALL) NOPASSWD:ALL' >> ${IMAGE_ROOTFS}/etc/sudoers
    
    # Install vim configuration
    install -d ${IMAGE_ROOTFS}/home/developer/.vim
    echo 'set number
set autoindent
set smartindent
set tabstop=4
set shiftwidth=4
set expandtab
syntax on
colorscheme default' > ${IMAGE_ROOTFS}/home/developer/.vimrc
    
    chown -R 1001:1001 ${IMAGE_ROOTFS}/home/developer
}

ROOTFS_POSTPROCESS_COMMAND += "configure_development; "