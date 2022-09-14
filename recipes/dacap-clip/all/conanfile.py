import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.build import check_min_cppstd

required_conan_version = ">=1.50.0"

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

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_png

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.get_safe("with_png", False):
            self.requires("libpng/1.6.37")
        if self.settings.os == "Linux":
            self.requires("xorg/system")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        if is_msvc(self) and self.info.settings.build_type == "Debug" and self.info.options.shared == True:
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support MSVC debug shared build (now).")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self.source_folder)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["CLIP_EXAMPLES"] = False
        toolchain.variables["CLIP_TESTS"] = False
        toolchain.variables["CLIP_X11_WITH_PNG"] = self.options.get_safe("with_png", False)
        if is_msvc(self):
            toolchain.cache_variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = bool(self.options.shared)
        toolchain.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "clip.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "*.a", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.so", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dylib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.lib", src=self.build_folder, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.dll", src=self.build_folder, dst=os.path.join(self.package_folder, "bin"), keep_path=False)

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

        # TODO: Remove on Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "clip"
        self.cpp_info.names["cmake_find_package_multi"] = "clip"
