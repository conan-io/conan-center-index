import os
import textwrap

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, load, mkdir, rmdir, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class LzipConan(ConanFile):
    name = "lzip"
    description = "Lzip is a lossless data compressor with a user interface similar to the one of gzip or bzip2"
    license = "GPL-v2-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.nongnu.org/lzip/"
    topics = ("compressor", "lzma")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler

    def validate(self):
        if is_msvc(self):
            raise ConanInvalidConfiguration("Visual Studio is not supported")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.win_bash = True
            if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                self.tool_requires("msys2/cci.latest")

    def _detect_compilers(self):
        rmdir(self, "detectdir")
        mkdir(self, "detectdir")
        with chdir(self, "detectdir"):
            save(
                self,
                "CMakeLists.txt",
                textwrap.dedent("""\
                cmake_minimum_required(VERSION 2.8)
                project(test C CXX)
                message(STATUS "CC=${CMAKE_C_COMPILER}")
                message(STATUS "CXX=${CMAKE_CXX_COMPILER}")
                file(WRITE cc.txt "${CMAKE_C_COMPILER}")
                file(WRITE cxx.txt "${CMAKE_CXX_COMPILER}")
                """),
            )
            CMake(self).configure(source_folder="detectdir", build_folder="detectdir")
            cc = load(self, "cc.txt").strip()
            cxx = load(self, "cxx.txt").strip()
        return cc, cxx

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()

    def package(self):
        copy(self, "COPYING",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.configure()
            autotools.install(args=["-j1"])

        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info(f"Appending PATH environment variable: {bin_path}")
        self.env_info.PATH.append(bin_path)
