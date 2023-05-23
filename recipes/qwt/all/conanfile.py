from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class QwtConan(ConanFile):
    name = "qwt"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://qwt.sourceforge.io/"
    topics = ("archive", "compression")
    description = (
        "The Qwt library contains GUI Components and utility classes which are primarily useful for programs "
        "with a technical background. Beside a framework for 2D plots it provides scales, sliders, dials, compasses, "
        "thermometers, wheels and knobs to control or display values, arrays, or ranges of type double."
    )
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "plot": [True, False],
        "widgets": [True, False],
        "svg": [True, False],
        "opengl": [True, False],
        "designer": [True, False],
        "polar": [True, False],
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
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("qt/5.15.7")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Qwt recipe does not support cross-compilation yet")
        qt_options = self.dependencies["qt"].options
        if self.info.options.widgets and not qt_options.widgets:
            raise ConanInvalidConfiguration("qwt:widgets=True requires qt:widgets=True")
        if self.info.options.svg and not qt_options.qtsvg:
            raise ConanInvalidConfiguration("qwt:svg=True requires qt:qtsvg=True")
        if self.info.options.opengl and qt_options.opengl == "no":
            raise ConanInvalidConfiguration("qwt:opengl=True is not compatible with qt:opengl=no")
        if self.info.options.designer and not (qt_options.qttools and qt_options.gui and qt_options.widgets):
            raise ConanInvalidConfiguration("qwt:designer=True requires qt:qttools=True, qt::gui=True and qt::widgets=True")

    def build_requirements(self):
        if hasattr(self, "settings_build") and cross_building(self):
            self.tool_requires("qt/5.15.7")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            env = VirtualBuildEnv(self)
            env.generate()
        else:
            env = VirtualRunEnv(self)
            env.generate(scope="build")

        tc = CMakeToolchain(self)
        tc.variables["QWT_DLL"] = self.options.shared
        tc.variables["QWT_STATIC "] = not self.options.shared
        tc.variables["QWT_PLOT"] = self.options.plot
        tc.variables["QWT_WIDGETS"] = self.options.widgets
        tc.variables["QWT_SVG"] = self.options.svg
        tc.variables["QWT_OPENGL"] =self.options.opengl
        tc.variables["QWT_DESIGNER"] = self.options.designer
        tc.variables["QWT_POLAR"] = self.options.polar
        tc.variables["QWT_BUILD_PLAYGROUND"] = False
        tc.variables["QWT_BUILD_EXAMPLES"] = False
        tc.variables["QWT_BUILD_TESTS"] = False
        tc.variables["QWT_FRAMEWORK"] = False
        tc.variables["CMAKE_INSTALL_DATADIR"] = "res"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["qwt"]
        self.cpp_info.requires = ["qt::qtCore", "qt::qtConcurrent", "qt::qtPrintSupport"]
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("QWT_DLL")
        if not self.options.plot:
            self.cpp_info.defines.append("NO_QWT_PLOT")
        if not self.options.polar:
            self.cpp_info.defines.append("NO_QWT_POLAR")
        if self.options.widgets:
            self.cpp_info.requires.append("qt::qtWidgets")
        else:
            self.cpp_info.defines.append("NO_QWT_WIDGETS")
        if self.options.opengl:
            self.cpp_info.requires.append("qt::qtOpenGL")
            if Version(self.dependencies["qt"].ref.version).major >= "6":
                self.cpp_info.requires.append("qt::qtOpenGLWidgets")
        else:
            self.cpp_info.defines.append("QWT_NO_OPENGL")
        if self.options.svg:
            self.cpp_info.requires.append("qt::qtSvg")
        else:
            self.cpp_info.defines.append("QWT_NO_SVG")

        if self.options.designer:
            qt_plugin_path = os.path.join(
                self.package_folder, "res" if self.settings.os == "Windows" else "lib",
                f"qt{Version(self.dependencies['qt'].ref.version).major}", "plugins",
            )
            self.runenv_info.prepend_path("QT_PLUGIN_PATH", qt_plugin_path)

            # TODO: to remove in conan v2
            self.env_info.QT_PLUGIN_PATH.append(qt_plugin_path)
