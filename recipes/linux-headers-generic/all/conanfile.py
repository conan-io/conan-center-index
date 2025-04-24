import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import chdir, copy, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.build import cross_building

required_conan_version = ">=1.53.0"


class LinuxHeadersGenericConan(ConanFile):
    name = "linux-headers-generic"
    description = "Generic Linux kernel headers"
    license = "GPL-2.0-only"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.kernel.org/"
    topics = ("linux", "headers", "generic", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.os
        del self.info.settings.build_type
        del self.info.settings.compiler

    @property
    def _is_legacy_one_profile(self):
        return not hasattr(self, "settings_build")

    @property
    def _conan_arch_to_linux_arch(self):
        # INFO: Conan architecture to Linux architecture mapping
        # https://www.kernel.org/doc/html/latest/arch/index.html
        # https://github.com/torvalds/linux/tree/v6.14/arch
        arch_mapping = {
            "armv8": "arm64",
            "armv7": "arm",
            "x86": "x86",
            "ppc": "powerpc",
            "riscv": "riscv",
            "mips": "mips",
            "sparc": "sparc",
            "s390": "s390",
            "sh4le": "sh"
        }
        arch = str(self.settings.arch)
        return next((value for prefix, value in arch_mapping.items()
                    if arch.startswith(prefix)), arch)

    def validate(self):
        if self.settings.os != "Linux" or (not self._is_legacy_one_profile and self.settings_build.os != "Linux"):
            raise ConanInvalidConfiguration("linux-headers-generic supports only Linux")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        if cross_building(self):
            # INFO: When cross-compiling, the build system needs to know the target architecture
            # https://github.com/torvalds/linux/blob/v6.14/Makefile#L394
            tc.make_args.append(f"ARCH={self._conan_arch_to_linux_arch}")
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make(target="headers")

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "include/*.h",
             dst=self.package_folder,
             src=os.path.join(self.source_folder, "usr"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
