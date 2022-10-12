from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import apply_conandata_patches, copy, download, export_conandata_patches, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout, vs_layout
from conan.tools.microsoft import is_msvc

import os


required_conan_version = ">=1.52.0"

class YASMConan(ConanFile):
    name = "yasm"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/yasm/yasm"
    description = "Yasm is a complete rewrite of the NASM assembler under the 'new' BSD License"
    topics = ("yasm", "installer", "assembler")
    license = "BSD-2-Clause"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def layout(self):
        if is_msvc(self):
            vs_layout(self)
        else:
            basic_layout(self)

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        get(self, **self.conan_data["sources"][self.version][0],
                  destination=self.source_folder, strip_root=True)
        download(self, **self.conan_data["sources"][self.version][1],
                       filename=os.path.join(self.source_folder, "YASM-VERSION-GEN.bat"))

    @property
    def _msvc_subfolder(self):
        return os.path.join(self.source_folder, "Mkfiles", "vc12")

    def _generate_autotools(self):
        tc = AutotoolsToolchain(self)
        enable_debug = "yes" if self.settings.build_type == "Debug" else "no"
        tc.configure_args.extend([
            f"--enable-debug={enable_debug}",
            "--disable-rpath",
            "--disable-nls",
        ])
        tc.generate()

    def _generate_cmake(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["YASM_BUILD_TESTS"] = False
        tc.generate()

    def generate(self):
        if is_msvc(self):
            self._generate_cmake()
        else:
            self._generate_autotools()

    def build(self):
        apply_conandata_patches(self)
        if is_msvc(self):
            cmake = CMake(self)
            cmake.configure()
            cmake.build()
        else:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, pattern="BSD.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, pattern="COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        if is_msvc(self):
            cmake = CMake(self)
            cmake.install()
            rmdir(self, os.path.join(self.package_folder, "include"))
            rmdir(self, os.path.join(self.package_folder, "lib"))
        else:
            autotools = Autotools(self)
            autotools.install()
            rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
