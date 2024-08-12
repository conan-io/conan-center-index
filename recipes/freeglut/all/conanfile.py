from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class freeglutConan(ConanFile):
    name = "freeglut"
    description = "Open-source alternative to the OpenGL Utility Toolkit (GLUT) library"
    topics = ("gl", "glut", "graphics," "opengl", "toolkit", "utility")
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
        "with_wayland": [True, False],

    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "gles": False,
        "print_errors_at_runtime": True,
        "print_warnings_at_runtime": True,
        "replace_glut": True,
        "with_wayland": True,
    }

    @property
    def _requires_libglvnd_egl(self):
        return self._requires_libglvnd_gles or self.options.get_safe("with_wayland")

    @property
    def _requires_libglvnd_gles(self):
        return self._with_libglvnd and self.options.get_safe("gles")

    @property
    def _requires_libglvnd_glx(self):
        return self._with_libglvnd and not self.options.get_safe("gles")

    @property
    def _with_libglvnd(self):
        return self.settings.os in ["FreeBSD", "Linux"]

    @property
    def _with_x11(self):
        return self.settings.os in ["FreeBSD", "Linux"] and not self.options.get_safe("with_wayland")

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")
        if self.settings.os not in ["Android", "FreeBSD", "Linux"]:
            self.options.rm_safe("gles")
        else:
            self.options.gles = self.settings.os == "Android"
        if self.settings.os != "Linux":
            self.options.rm_safe("with_wayland")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

        if self._requires_libglvnd_egl:
            self.options["libglvnd"].egl = True
        if self._requires_libglvnd_gles:
            self.options["libglvnd"].gles1 = True
            self.options["libglvnd"].gles2 = True
        if self._requires_libglvnd_glx:
            self.options["libglvnd"].glx = True
        if self.options.get_safe("with_wayland"):
            self.options["xkbcommon"].with_wayland = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if is_apple_os(self) or self.settings.os == "Windows":
            self.requires("glu/system")
        else:
            # FreeGLUT includes glu.h in freeglut_std.h.
            self.requires("mesa-glu/9.0.3", transitive_headers=True)
        if self._with_libglvnd:
            self.requires("libglvnd/1.7.0")
        else:
            self.requires("opengl/system")
        if self.options.get_safe("with_wayland"):
            self.requires("wayland/1.22.0")
            self.requires("xkbcommon/1.6.0")
        if self._with_x11:
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
        if self._requires_libglvnd_egl and not self.dependencies["libglvnd"].options.egl:
            raise ConanInvalidConfiguration(f"{self.ref} requires the egl option of libglvnd to be enabled when either the gles option or with_wayland option is enabled")
        if self._requires_libglvnd_gles and not self.dependencies["libglvnd"].options.gles1:
            raise ConanInvalidConfiguration(f"{self.ref} requires the gles1 option of libglvnd to be enabled when the gles option is enabled")
        if self._requires_libglvnd_gles and not self.dependencies["libglvnd"].options.gles2:
            raise ConanInvalidConfiguration(f"{self.ref} requires the gles2 option of libglvnd to be enabled when the gles option is enabled")
        if self._requires_libglvnd_glx and not self.dependencies["libglvnd"].options.glx:
            raise ConanInvalidConfiguration(f"{self.ref} requires the glx option of libglvnd to be enabled when the gles option is disabled")
        if self.options.get_safe("with_wayland") and not self.dependencies["xkbcommon"].options.with_wayland:
            raise ConanInvalidConfiguration(f"{self.ref} requires the with_wayland option of xkbcommon to be enabled when the with_wayland option is enabled")


    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FREEGLUT_BUILD_DEMOS"] = False
        tc.variables["FREEGLUT_BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["FREEGLUT_BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["FREEGLUT_GLES"] = self.options.get_safe("gles", False)
        tc.variables["FREEGLUT_PRINT_ERRORS"] = self.options.print_errors_at_runtime
        tc.variables["FREEGLUT_PRINT_WARNINGS"] = self.options.print_warnings_at_runtime
        tc.variables["FREEGLUT_WAYLAND"] = self.options.get_safe("with_wayland", False)
        tc.variables["FREEGLUT_INSTALL_PDB"] = False
        tc.variables["INSTALL_PDB"] = False
        tc.variables["FREEGLUT_REPLACE_GLUT"] = self.options.replace_glut
        tc.preprocessor_definitions["FREEGLUT_LIB_PRAGMAS"] = "0"
        tc.generate()
        cmake_deps = CMakeDeps(self)
        cmake_deps.generate()
        pkg_config_deps = PkgConfigDeps(self)
        pkg_config_deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"))
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
        if self.settings.os in ["FreeBSD", "Linux"]:
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
        if self._requires_libglvnd_egl:
            self.cpp_info.components["freeglut_"].requires.append("libglvnd::egl")
        if self._requires_libglvnd_gles:
            self.cpp_info.components["freeglut_"].requires.append("libglvnd::gles1")
            self.cpp_info.components["freeglut_"].requires.append("libglvnd::gles2")
        if self._requires_libglvnd_glx:
            self.cpp_info.components["freeglut_"].requires.append("libglvnd::gl")
        if self._with_libglvnd:
            self.cpp_info.components["freeglut_"].requires.append("libglvnd::opengl")
        else:
            self.cpp_info.components["freeglut_"].requires.append("opengl::opengl")
        if self._with_x11:
            self.cpp_info.components["freeglut_"].requires.append("xorg::xorg")
        if self.options.get_safe("with_wayland"):
            self.cpp_info.components["freeglut_"].requires.extend(["wayland::wayland-client", "wayland::wayland-cursor", "wayland::wayland-egl", "xkbcommon::xkbcommon"])
        if is_apple_os(self) or self.settings.os == "Windows":
            self.cpp_info.components["freeglut_"].requires.append("glu::glu")
        else:
            self.cpp_info.components["freeglut_"].requires.append("mesa-glu::mesa-glu")
