import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout

required_conan_version = ">=1.47.0"


class Perf(ConanFile):
    name = "perf"
    description = "Linux profiling with performance counters"
    license = "GPL-2.0 WITH Linux-syscall-note"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://perf.wiki.kernel.org/index.php"
    topics = ("linux", "profiling")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            raise ConanInvalidConfiguration("perf is supported only on Linux")

    def build_requirements(self):
        self.tool_requires("flex/2.6.4")
        self.tool_requires("bison/3.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.make_args += ["NO_LIBPYTHON=1"]
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

        # TODO: remove in conan v2
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
