from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.build import cross_building
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.50"

class QwtConan(ConanFile):
    name = "qwt"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://qwt.sourceforge.io/"
    topics = ("conan", "archive", "compression")
    description = (
        "The Qwt library contains GUI Components and utility classes which are primarily useful for programs "
        "with a technical background. Beside a framework for 2D plots it provides scales, sliders, dials, compasses, "
        "thermometers, wheels and knobs to control or display values, arrays, or ranges of type double."
    )
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "plot": [True, False],
        "widgets": [True, False],
        "svg": [True, False],
        "opengl": [True, False],
        "designer": [True, False],
        "polar": [True, False],
        "playground": [True, False],
        "examples": [True, False],
        "test": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "plot": True,
        "widgets": True,
        "svg": False,
        "opengl": True,
        "designer": False,
        "polar": True,
        "playground": False,
        "examples": False,
        "test": False
    }

    tool_requires  = (
        "cmake/3.23.2",
        "ninja/1.11.0"
    )

    def _patch_sources(self):
        apply_conandata_patches(self)

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)


    def requirements(self):
        self.requires("qt/5.15.5")

    def build_requirements(self):
        if self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self.build_requires("jom/1.1.3")
        self.tool_requires("qt/5.15.5") 

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Qwt recipe does not support cross-compilation yet")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = CMakeToolchain(self, generator="Ninja")

        tc.variables["QWT_DLL"] = "ON" if self.options.shared else "OFF"
        tc.variables["QWT_STATIC "] = "ON" if not self.options.shared else "OFF"
        tc.variables["QWT_PLOT"] = "ON" if self.options.plot else "OFF"
        tc.variables["QWT_WIDGETS"] = "ON" if self.options.widgets else "OFF"
        tc.variables["QWT_SVG"] = "ON" if self.options.svg else "OFF"
        tc.variables["QWT_OPENGL"] = "ON" if self.options.opengl else "OFF"
        tc.variables["QWT_DESIGNER"] = "ON" if self.options.designer else "OFF"
        tc.variables["QWT_POLAR"] = "ON" if self.options.polar else "OFF"
        tc.variables["QWT_BUILD_PLAYGROUND"] = "ON" if self.options.playground else "OFF"
        tc.variables["QWT_BUILD_EXAMPLES"] = "ON" if self.options.examples else "OFF"
        tc.variables["QWT_BUILD_TESTS"] = "ON" if self.options.test else "OFF"
        tc.variables["QWT_FRAMEWORK"] = "OFF"

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

        if self.options.test:
            cmake.test()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, f"{self.package_folder}/lib/pkgconfig")        
        rmdir(self, f"{self.package_folder}/lib/cmake")
        self.copy("COPYING", src=self.folders.source, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = ["qwt"]
        self.env_info.QT_PLUGIN_PATH.append(os.path.join(self.package_folder, 'bin'))
        self.env_info.QT_PLUGIN_PATH.append(os.path.join(self.package_folder, 'lib'))
        self.cpp_info.defines = ['HAVE_QWT', 'QWT_DLL'] if self.options.shared else ['HAVE_QWT']
        if not self.options.plot:
            self.cpp_info.defines.append("NO_QWT_PLOT")
        if not self.options.polar:
            self.cpp_info.defines.append("NO_QWT_POLAR")
        if not self.options.widgets:
            self.cpp_info.defines.append("NO_QWT_WIDGETS")
        if not self.options.opengl:
            self.cpp_info.defines.append("NO_QWT_OPENGL")
        if not self.options.svg:
            self.cpp_info.defines.append("QWT_NO_SVG")

