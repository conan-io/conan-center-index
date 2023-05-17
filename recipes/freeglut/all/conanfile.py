from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class freeglutConan(ConanFile):
    name = "freeglut"
    description = "Open-source alternative to the OpenGL Utility Toolkit (GLUT) library"
    topics = ("opengl", "gl", "glut", "utility", "toolkit", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://freeglut.sourceforge.net"
    license = "X11"
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "gles": [True, False],
        "print_errors_at_runtime": [True, False],
        "print_warnings_at_runtime": [True, False],
        "replace_glut": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "gles": False,
        "print_errors_at_runtime": True,
        "print_warnings_at_runtime": True,
        "replace_glut": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("opengl/system")
        self.requires("glu/system")
        if self.settings.os == "Linux":
            self.requires("xorg/system")

    def validate(self):
        if self.settings.os == "Macos":
            # see https://github.com/dcnieho/FreeGLUT/issues/27
            # and https://sourceforge.net/p/freeglut/bugs/218/
            # also, it seems to require `brew cask install xquartz`
            raise ConanInvalidConfiguration(f"{self.ref} does not support macos")
        if Version(self.version) < "3.2.2":
            if (self.settings.compiler == "gcc" and Version(self.settings.compiler.version) >= "10.0") or \
                (self.settings.compiler == "clang" and Version(self.settings.compiler.version) >= "11.0"):
                # see https://github.com/dcnieho/FreeGLUT/issues/86
                raise ConanInvalidConfiguration(f"{self.ref} does not support gcc >= 10 and clang >= 11")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FREEGLUT_BUILD_DEMOS"] = False
        tc.variables["FREEGLUT_BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["FREEGLUT_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["FREEGLUT_GLES"] = self.options.gles
        tc.variables["FREEGLUT_PRINT_ERRORS"] = self.options.print_errors_at_runtime
        tc.variables["FREEGLUT_PRINT_WARNINGS"] = self.options.print_warnings_at_runtime
        tc.variables["FREEGLUT_INSTALL_PDB"] = False
        tc.variables["INSTALL_PDB"] = False
        tc.variables["FREEGLUT_REPLACE_GLUT"] = self.options.replace_glut
        tc.preprocessor_definitions["FREEGLUT_LIB_PRAGMAS"] = "0"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        config_target = "freeglut" if self.options.shared else "freeglut_static"
        pkg_config = "freeglut" if self.settings.os == "Windows" else "glut"

        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "GLUT")
        self.cpp_info.set_property("cmake_module_target_name", "GLUT::GLUT")
        self.cpp_info.set_property("cmake_file_name", "FreeGLUT")
        self.cpp_info.set_property("cmake_target_name", f"FreeGLUT::{config_target}")
        self.cpp_info.set_property("pkg_config_name", pkg_config)

        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["freeglut_"].libs = collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.components["freeglut_"].system_libs.extend(["pthread", "m", "dl", "rt"])
        elif self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.components["freeglut_"].defines.append("FREEGLUT_STATIC=1")
            self.cpp_info.components["freeglut_"].defines.append("FREEGLUT_LIB_PRAGMAS=0")
            self.cpp_info.components["freeglut_"].system_libs.extend(["glu32", "gdi32", "winmm", "user32"])

        # TODO: to remove in conan v2 once cmake_find_package_* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "GLUT"
        self.cpp_info.names["cmake_find_package_multi"] = "FreeGLUT"
        self.cpp_info.names["pkg_config"] = pkg_config
        self.cpp_info.components["freeglut_"].names["cmake_find_package"] = "GLUT"
        self.cpp_info.components["freeglut_"].set_property("cmake_module_target_name", "GLUT::GLUT")
        self.cpp_info.components["freeglut_"].names["cmake_find_package_multi"] = config_target
        self.cpp_info.components["freeglut_"].set_property("cmake_target_name", f"FreeGLUT::{config_target}")
        self.cpp_info.components["freeglut_"].set_property("pkg_config_name", pkg_config)
        self.cpp_info.components["freeglut_"].requires.extend(["opengl::opengl", "glu::glu"])
        if self.settings.os == "Linux":
            self.cpp_info.components["freeglut_"].requires.append("xorg::xorg")
