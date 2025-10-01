#!/bin/bash

# TRT Yocto Project - Build All Platforms Script
# This script builds images for all supported platforms

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

# Configuration
MACHINES=("raspberrypi-trt" "beaglebone-trt" "imx7-trt")
IMAGES=("trt-base-image" "trt-industrial-image" "trt-development-image")
BUILD_BASE_DIR="build-trt"
FAILED_BUILDS=()

# Help function
show_help() {
    echo "TRT Yocto Project - Build All Platforms"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -m, --machines MACHINES   Comma-separated list of machines to build"
    echo "                           (default: raspberrypi-trt,beaglebone-trt,imx7-trt)"
    echo "  -i, --images IMAGES       Comma-separated list of images to build"
    echo "                           (default: trt-base-image,trt-industrial-image,trt-development-image)"
    echo "  -j, --parallel JOBS       Number of parallel jobs (default: auto-detect)"
    echo "  -c, --clean              Clean builds before building"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Build all images for all machines"
    echo "  $0 -m raspberrypi-trt               # Build only for Raspberry Pi"
    echo "  $0 -i trt-base-image                # Build only base image for all machines"
    echo "  $0 -m raspberrypi-trt -i trt-base-image # Build base image for Raspberry Pi only"
    echo ""
}

# Parse command line arguments
CLEAN_BUILD=false
PARALLEL_JOBS=$(nproc)

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--machines)
            IFS=',' read -ra MACHINES <<< "$2"
            shift 2
            ;;
        -i|--images)
            IFS=',' read -ra IMAGES <<< "$2"
            shift 2
            ;;
        -j|--parallel)
            PARALLEL_JOBS="$2"
            shift 2
            ;;
        -c|--clean)
            CLEAN_BUILD=true
            shift
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

print_info "TRT Yocto Project - Building all platforms"
print_info "Machines: ${MACHINES[*]}"
print_info "Images: ${IMAGES[*]}"
print_info "Parallel jobs: $PARALLEL_JOBS"
print_info "Clean build: $CLEAN_BUILD"

# Function to build for a specific machine
build_machine() {
    local machine=$1
    local build_dir="${BUILD_BASE_DIR}-${machine}"
    
    print_info "Setting up build environment for $machine..."
    
    # Source the build environment
    source poky/oe-init-build-env "$build_dir"
    
    # Configure build
    if [ ! -f conf/configured ]; then
        print_info "Configuring build for $machine..."
        
        # Configure bblayers.conf
        cat > conf/bblayers.conf << EOF
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
EOF

        # Configure local.conf
        cat >> conf/local.conf << EOF

# TRT Configuration for $machine
MACHINE = "$machine"
DISTRO = "trt-distro"

# Build optimization
BB_NUMBER_THREADS = "$PARALLEL_JOBS"
PARALLEL_MAKE = "-j $PARALLEL_JOBS"

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

EOF
        touch conf/configured
    fi
    
    # Clean if requested
    if [ "$CLEAN_BUILD" = true ]; then
        print_info "Cleaning previous builds for $machine..."
        rm -rf tmp sstate-cache
    fi
    
    # Build each image
    for image in "${IMAGES[@]}"; do
        print_info "Building $image for $machine..."
        local start_time=$(date +%s)
        
        if bitbake "$image"; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            print_success "Successfully built $image for $machine ($(date -u -d @$duration +%H:%M:%S))"
            
            # Copy images to a common directory
            local deploy_dir="tmp/deploy/images/$machine"
            local output_dir="../images/$machine"
            mkdir -p "$output_dir"
            
            if [ -d "$deploy_dir" ]; then
                cp "$deploy_dir"/*.{img,tar.*,manifest} "$output_dir/" 2>/dev/null || true
                print_info "Images copied to $output_dir"
            fi
        else
            print_error "Failed to build $image for $machine"
            FAILED_BUILDS+=("$machine:$image")
        fi
    done
    
    # Return to main directory
    cd ..
}

# Main build loop
start_total_time=$(date +%s)

for machine in "${MACHINES[@]}"; do
    print_info "Starting build for machine: $machine"
    build_machine "$machine"
    print_info "Completed build for machine: $machine"
    echo "----------------------------------------"
done

end_total_time=$(date +%s)
total_duration=$((end_total_time - start_total_time))

# Build summary
echo ""
print_info "Build Summary"
echo "============="
echo "Total build time: $(date -u -d @$total_duration +%H:%M:%S)"
echo "Machines built: ${MACHINES[*]}"
echo "Images built: ${IMAGES[*]}"

if [ ${#FAILED_BUILDS[@]} -eq 0 ]; then
    print_success "All builds completed successfully!"
else
    print_error "Some builds failed:"
    for failed in "${FAILED_BUILDS[@]}"; do
        echo "  - $failed"
    done
    exit 1
fi

print_info "Built images can be found in the 'images/' directory"
print_info "Build logs are available in each build directory under tmp/log/"