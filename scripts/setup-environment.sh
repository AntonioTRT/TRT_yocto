#!/bin/bash

# TRT Yocto Project Environment Setup Script
# This script sets up the build environment for all supported platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
YOCTO_DIR="$HOME/yocto-trt"
POKY_BRANCH="scarthgap"
BUILD_DIR="build-trt"

# Help function
show_help() {
    echo "TRT Yocto Project Environment Setup"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --directory DIR    Set Yocto workspace directory (default: $YOCTO_DIR)"
    echo "  -b, --branch BRANCH    Set Poky branch (default: $POKY_BRANCH)"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Supported machines:"
    echo "  - raspberrypi-trt     Raspberry Pi (all models)"
    echo "  - beaglebone-trt      BeagleBone Black/Industrial"
    echo "  - imx7-trt           NXP i.MX7"
    echo ""
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--directory)
            YOCTO_DIR="$2"
            shift 2
            ;;
        -b|--branch)
            POKY_BRANCH="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

print_info "Setting up TRT Yocto Project environment..."
print_info "Workspace directory: $YOCTO_DIR"
print_info "Poky branch: $POKY_BRANCH"

# Check if directory exists
if [ -d "$YOCTO_DIR" ]; then
    print_warning "Directory $YOCTO_DIR already exists"
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Aborted by user"
        exit 0
    fi
else
    print_info "Creating workspace directory: $YOCTO_DIR"
    mkdir -p "$YOCTO_DIR"
fi

cd "$YOCTO_DIR"

# Clone or update repositories
clone_or_update() {
    local repo_url=$1
    local repo_dir=$2
    local branch=$3
    
    if [ -d "$repo_dir" ]; then
        print_info "Updating $repo_dir..."
        cd "$repo_dir"
        git fetch origin
        git checkout "$branch"
        git pull origin "$branch"
        cd ..
    else
        print_info "Cloning $repo_dir..."
        git clone -b "$branch" "$repo_url" "$repo_dir"
    fi
}

# Clone/update all required repositories
print_info "Setting up Yocto layers..."

clone_or_update "https://git.yoctoproject.org/poky" "poky" "$POKY_BRANCH"
clone_or_update "https://github.com/openembedded/meta-openembedded.git" "meta-openembedded" "$POKY_BRANCH"
clone_or_update "https://github.com/agherzan/meta-raspberrypi.git" "meta-raspberrypi" "$POKY_BRANCH"
clone_or_update "https://github.com/Freescale/meta-freescale.git" "meta-freescale" "$POKY_BRANCH"
clone_or_update "https://github.com/meta-ti/meta-ti.git" "meta-ti" "$POKY_BRANCH"

# Check if meta-trt exists
if [ ! -d "meta-trt" ]; then
    print_warning "meta-trt layer not found. Please clone it manually:"
    print_info "git clone https://github.com/AntonioTRT/TRT_yocto.git meta-trt"
else
    print_success "meta-trt layer found"
fi

print_success "All repositories are ready!"

# Create build environment setup script
cat > setup-build-env.sh << 'EOF'
#!/bin/bash

# Build environment setup for TRT Yocto Project

MACHINE=${1:-raspberrypi-trt}
BUILD_DIR="build-trt-$MACHINE"

echo "Setting up build environment for machine: $MACHINE"
echo "Build directory: $BUILD_DIR"

# Source the Yocto environment
source poky/oe-init-build-env "$BUILD_DIR"

# Configure bblayers.conf
if [ ! -f conf/bblayers.conf.backup ]; then
    cp conf/bblayers.conf conf/bblayers.conf.backup
fi

cat > conf/bblayers.conf << LAYERS_EOF
# POKY_BBLAYERS_CONF_VERSION is increased each time build/conf/bblayers.conf
# changes incompatibly
POKY_BBLAYERS_CONF_VERSION = "2"

BBPATH = "\${TOPDIR}"
BBFILES ?= ""

BBLAYERS ?= " \\
  $(pwd)/../poky/meta \\
  $(pwd)/../poky/meta-poky \\
  $(pwd)/../poky/meta-yocto-bsp \\
  $(pwd)/../meta-openembedded/meta-oe \\
  $(pwd)/../meta-openembedded/meta-python \\
  $(pwd)/../meta-openembedded/meta-networking \\
  $(pwd)/../meta-raspberrypi \\
  $(pwd)/../meta-freescale \\
  $(pwd)/../meta-ti/meta-ti-bsp \\
  $(pwd)/../meta-trt \\
  "
LAYERS_EOF

# Configure local.conf
if [ ! -f conf/local.conf.backup ]; then
    cp conf/local.conf conf/local.conf.backup
fi

# Add TRT specific configurations
cat >> conf/local.conf << LOCAL_EOF

# TRT Configuration
MACHINE = "$MACHINE"
DISTRO = "trt-distro"

# Build optimization
BB_NUMBER_THREADS = "$(nproc)"
PARALLEL_MAKE = "-j $(nproc)"

# Disk space monitoring
BB_DISKMON_DIRS = "\\
    STOPTASKS,\${TMPDIR},1G,100K \\
    STOPTASKS,\${DL_DIR},1G,100K \\
    STOPTASKS,\${SSTATE_DIR},1G,100K \\
    STOPTASKS,/tmp,100M,100K \\
    HALT,\${TMPDIR},100M,1K \\
    HALT,\${DL_DIR},100M,1K \\
    HALT,\${SSTATE_DIR},100M,1K \\
    HALT,/tmp,10M,1K"

# Package management
PACKAGE_CLASSES = "package_rpm"
EXTRA_IMAGE_FEATURES ?= "debug-tweaks tools-debug ssh-server-openssh package-management"

# Enable build history
INHERIT += "buildhistory"
BUILDHISTORY_COMMIT = "1"

LOCAL_EOF

echo "Build environment configured for $MACHINE"
echo "To build images, run:"
echo "  bitbake trt-base-image       # Minimal image"
echo "  bitbake trt-industrial-image # Industrial image"
echo "  bitbake trt-development-image # Development image"
EOF

chmod +x setup-build-env.sh

print_success "Environment setup complete!"
print_info "To start building:"
print_info "1. cd $YOCTO_DIR"
print_info "2. ./setup-build-env.sh [MACHINE]"
print_info "   Available machines: raspberrypi-trt, beaglebone-trt, imx7-trt"
print_info "3. bitbake trt-base-image"

print_info "For more information, check the README.md file in meta-trt layer"