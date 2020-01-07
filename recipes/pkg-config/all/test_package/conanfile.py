from conans import ConanFile, tools
import os

libastral_pc = """
PC FILE EXAMPLE:

prefix=/usr/local
exec_prefix=${prefix}
libdir=${exec_prefix}/lib
includedir=${prefix}/include

Name: libastral
Description: Interface library for Astral data flows
Version: 6.6.6
Libs: -L${libdir}/libastral -lastral -Wl,--whole-archive
Cflags: -I${includedir}/libastral -D_USE_LIBASTRAL
"""


class TestPackageConan(ConanFile):

    def test(self):
        self.run("pkg-config --version")
        tools.save(os.path.join(os.getcwd(), "libastral.pc"), libastral_pc)
        with tools.environment_append({"PKG_CONFIG_PATH": [os.getcwd()]}):
            self.run("pkg-config --modversion libastral")

