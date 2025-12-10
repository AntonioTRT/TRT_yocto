SUMMARY = "TRT Project About Program"
DESCRIPTION = "Installs and auto-starts the TRT Project About UI on boot"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"

SRC_URI = "file://start-trt-project.sh \
           file://trt-project.service"

S = "${WORKDIR}"

inherit systemd

SYSTEMD_SERVICE_${PN} = "trt-project.service"
SYSTEMD_AUTO_ENABLE = "enable"

RDEPENDS_${PN} = "python3"

# Copy the trt_project sources from the build context (assumes you copy them to files/ before build)
do_install() {
    install -d ${D}/opt/trt_project
    cp -r ${WORKDIR}/trt_project/* ${D}/opt/trt_project/
    install -m 0755 ${WORKDIR}/start-trt-project.sh ${D}/opt/trt_project/
    install -d ${D}${systemd_unitdir}/system
    install -m 0644 ${WORKDIR}/trt-project.service ${D}${systemd_unitdir}/system/
}

FILES_${PN} += "/opt/trt_project /opt/trt_project/start-trt-project.sh ${systemd_unitdir}/system/trt-project.service"