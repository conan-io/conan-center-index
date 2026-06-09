import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=2.0"


class Perf(ConanFile):
    name = "perf"
    description = "Linux profiling with performance counters"
    license = "GPL-2.0 WITH Linux-syscall-note"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://perf.wiki.kernel.org/index.php"
    topics = ("linux", "profiling")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def _get_linux_arch(self):
        # INFO: Map based on https://github.com/torvalds/linux/tree/master/arch
        arch = str(self.settings.arch)
        if arch.startswith("armv8"):
            return "arm64"
        if arch.startswith("armv"):
            return "arm"
        if arch.startswith("ppc"):
            return "powerpc"
        if arch.startswith("e2k-"):
            return "e2k"
        if arch.startswith("xtensa"):
            return "xtensa"
        if arch.startswith("tc"):
            return "arc"
        if arch.startswith("riscv"):
            return "riscv"
        if arch.startswith("sparc"):
            return "sparc"
        if arch.startswith("mips"):
            return "mips"
        if arch.startswith("s390"):
            return "s390"
        if arch.startswith("x86"):
            return "x86"
        if arch.startswith("avr"):
            return "avr"
        if arch.startswith("sh4le"):
            return "sh"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("perf is supported only on Linux")
        if not self._get_linux_arch():
            raise ConanInvalidConfiguration(f"Unsupported architecture: {self.settings.arch}")

    def build_requirements(self):
        self.tool_requires("flex/2.6.4")
        self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.make_args += ["NO_LIBPYTHON=1"]
        tc.make_args += ["WERROR=0"]
        tc.make_args += [f"ARCH={self._get_linux_arch()}"]
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        with chdir(self, os.path.join(self.source_folder, "tools", "perf")):
            autotools.make()

    def package(self):
        copy(self, "COPYING",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "LICENSES/**",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "perf",
            src=os.path.join(self.source_folder, "tools", "perf"),
            dst=os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []
