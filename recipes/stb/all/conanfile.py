from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, rm
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class StbConan(ConanFile):
    name = "stb"
    description = "single-file public domain libraries for C/C++"
    license = ("Unlicense", "MIT")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nothings/stb"
    topics = ("stb", "single-file", "header-only")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    options = {
        "with_deprecated": [True, False],
        "image": [True, False],
    }

    default_options = {
        "with_deprecated": True,
        "image": False,
    }

    @property
    def _version(self):
        # HACK: Used to circumvent the incompatibility
        #       of the format cci.YYYYMMDD in tools.Version
        return str(self.version)[4:]

    @property
    def _build_library(self):
        return self.options.image

    def config_options(self):
        if Version(self._version) < "20210713":
            del self.options.with_deprecated

    def export_sources(self):
        copy(self, pattern="CMakeLists.txt", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src"))
        copy(self, pattern="stb_image.cpp", src=self.recipe_folder, dst=os.path.join(self.export_sources_folder, "src"))

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.image:
            tc.variables["STB_IMAGE"] = "ON"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "stb_vorbis.c", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        rmdir(self, os.path.join(self.package_folder, "include", "tests"))
        if Version(self._version) >= "20210713":
            rmdir(self, os.path.join(self.package_folder, "include", "deprecated"))
        if self.options.get_safe("with_deprecated"):
            copy(self, "*.h", src=os.path.join(self.source_folder, "deprecated"), dst=os.path.join(self.package_folder, "include"))
            copy(self, "stb_image.c", src=os.path.join(self.source_folder, "deprecated"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "lib*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"))
        if not self.options.image:
            rm(self, pattern="stb_image.h", folder=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libs = ["stb"] if self._build_library else []
        self.cpp_info.defines.append("STB_TEXTEDIT_KEYTYPE=unsigned")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
