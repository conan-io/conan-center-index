import os

from conan import ConanFile
from conan import tools
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout

from conans.tools import check_min_cppstd

required_conan_version = ">=1.43.0"

class DacapClipConan(ConanFile):
    name = "dacap-clip"
    description = "Cross-platform C++ library to copy/paste clipboard content"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dacap/clip/"
    topics = ("clipboard", "copy", "paste")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        tools.files.copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_png

    def layout(self):
        cmake_layout(self)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        if self.options.get_safe("with_png", False):
            self.requires("libpng/1.6.37")
        if self.settings.os == "Linux":
            self.requires("xorg/system")

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["CLIP_EXAMPLES"] = False
        toolchain.variables["CLIP_TESTS"] = False
        toolchain.variables["CLIP_X11_WITH_PNG"] = self.options.get_safe("with_png", False)
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        tools.files.copy(self, "LICENSE.txt", os.path.join(self.source_folder, self._source_subfolder), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["clip"]

        if self.options.get_safe("with_png", False):
            self.cpp_info.requires.append("libpng::libpng")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.requires.append("xorg::xcb")
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Macos":
            self.cpp_info.frameworks = ['Cocoa', 'Carbon', 'CoreFoundation']
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend([
                "shlwapi",
                "windowscodecs",
            ])

        self.cpp_info.set_property("cmake_file_name", "clip")
        self.cpp_info.set_property("cmake_target_name", "clip::clip")
