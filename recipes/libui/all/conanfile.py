import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get
from conan.tools.gnu import PkgConfigDeps

required_conan_version = ">=1.53.0"


class libuiConan(ConanFile):
    name = "libui"
    description = "Simple and portable GUI library in C that uses the native GUI technologies of each platform it supports."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/andlabs/libui"
    topics = ("ui", "gui")

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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.options["gtk"].version = 3

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("gtk/system")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()
        tc = PkgConfigDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=self.source_folder)
        copy(self, "*.dll",
             dst=os.path.join(self.package_folder, "bin"),
             src=self.build_folder,
             keep_path=False)
        for pattern in ["*.a", "*.so*", "*.dylib*", "*.lib"]:
            copy(self, pattern,
                 dst=os.path.join(self.package_folder, "lib"),
                 src=self.build_folder,
                 keep_path=False)

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs += ["dl"]
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs += [
                "user32",
                "kernel32",
                "gdi32",
                "comctl32",
                "msimg32",
                "comdlg32",
                "d2d1",
                "dwrite",
                "ole32",
                "oleaut32",
                "oleacc",
                "uuid",
                "windowscodecs",
            ]
