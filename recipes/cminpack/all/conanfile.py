from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools import files
from conan import ConanFile
import os
import textwrap

required_conan_version = ">=1.45.0"


class CMinpackConan(ConanFile):
    name = "cminpack"
    url = "https://github.com/conan-io/conan-center-index"
    description = "About A C/C++ rewrite of the MINPACK software (originally in FORTRAN)" \
                  "for solving nonlinear equations and nonlinear least squares problems"
    topics = ("nonlinear", "solver")
    homepage = "http://devernay.free.fr/hacks/cminpack/"
    license = "BSD-like"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = "OFF"
        tc.variables["CMINPACK_LIB_INSTALL_DIR"] = "lib"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

        # cminpack is a c library
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self.source_folder)

    def build(self):
        cmake = CMake(self)
        # moving this into the toolchain variables is not sufficient
        # right now. required for setting shared option
        cmake.configure(variables={
            "CMAKE_POLICY_DEFAULT_CMP0077":  "NEW"
        })
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.copy(self, "CopyrightMINPACK.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        files.rmdir(self, os.path.join(self.package_folder, "share")) # contains cmake config files

    def library_postfix(self):
        postfix = ""
        if not self.options.shared:
            postfix += "_s" # for static
        if self.settings.build_type == "Debug":
            postfix += "_d"

        return postfix

    def package_info(self):
        minpack_include_dir = os.path.join("include", "cminpack-1")
        
        # the double precision version
        self.cpp_info.libs = ['cminpack' + self.library_postfix()]
        self.cpp_info.includedirs.append(minpack_include_dir)
        
        # the single precision version
        self.cpp_info.components['cminpacks'].libs = ['cminpacks' + self.library_postfix()]
        self.cpp_info.components['cminpacks'].includedirs.append(minpack_include_dir)
        self.cpp_info.components['cminpacks'].defines.append("__cminpack_float__")

        if self.settings.os != "Windows":
            self.cpp_info.system_libs.append("m")
            self.cpp_info.components['cminpacks'].system_libs.append("m")

        if not self.options.shared and self.settings.os == "Windows":
            self.cpp_info.defines.append("CMINPACK_NO_DLL")
            self.cpp_info.components['cminpacks'].defines.append("CMINPACK_NO_DLL")
