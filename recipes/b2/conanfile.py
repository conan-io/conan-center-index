from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.files import chdir, copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import VCVars, is_msvc
from conan.tools.gnu import AutotoolsToolchain

import os

required_conan_version = ">=2.0"

class B2Conan(ConanFile):
    name = "b2"
    homepage = "https://www.bfgroup.xyz/b2/"
    description = "B2 makes it easy to build C++ projects, everywhere."
    topics = ("installer", "builder", "build", "build-system")
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler"
    package_type = "application"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        if is_msvc(self):
            ms = VCVars(self)
            ms.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()

    @property
    def _b2_engine_dir(self):
        return os.path.join(self.source_folder, "src", "engine")

    @property
    def _b2_output_dir(self):
        return os.path.join(self.build_folder, "output")

    @property
    def _exe_suffix(self):
        return ".exe" if self.settings.os == "Windows" else ""

    @property
    def _b2_command(self):
        return os.path.join(self._b2_engine_dir, f"b2{self._exe_suffix}")

    def build(self):
        if cross_building(self):
            raise ConanException("Cross-building is not supported for b2.")

        self.output.info("Build engine...")

        if is_msvc(self):
            command = "build.bat msvc"
        else:
            command = "./build.sh cxx"

        with chdir(self, self._b2_engine_dir):
            self.run(command)

        self.output.info("Install...")

        install_command = " ".join([
            self._b2_command,
            "--ignore-site-config",
            f"--prefix={self._b2_output_dir}",
            "--abbreviate-paths",
            "install",
            "b2-install-layout=portable"
        ])

        with chdir(self, self.source_folder):
            self.run(install_command)

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.LICENSE", src=self._b2_engine_dir, dst=os.path.join(self.package_folder, "licenses"))

        bin_dir = os.path.join(self.package_folder, "bin")
        copy(self, "*b2", dst=bin_dir, src=self._b2_output_dir)
        copy(self, "*b2.exe", dst=bin_dir, src=self._b2_output_dir)
        copy(self, "*.jam", dst=bin_dir, src=self._b2_output_dir)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

