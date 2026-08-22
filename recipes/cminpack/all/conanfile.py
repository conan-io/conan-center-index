from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.apple import is_apple_os
import os

required_conan_version = ">=2.1"


class CMinpackConan(ConanFile):
    name = "cminpack"
    url = "https://github.com/conan-io/conan-center-index"
    description = "About A C/C++ rewrite of the MINPACK software (originally in FORTRAN)" \
                  "for solving nonlinear equations and nonlinear least squares problems"
    topics = ("nonlinear", "solver")
    homepage = "http://devernay.free.fr/hacks/cminpack/"
    license = "LicenseRef-CopyrightMINPACK.txt"
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
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_EXAMPLES"] = "OFF"
        tc.cache_variables["CMINPACK_LIB_INSTALL_DIR"] = "lib"
        tc.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5" # CMake 4 support
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "CopyrightMINPACK.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share")) # contains cmake config files

    def _library_postfix(self):
        postfix = ""
        if not self.options.shared:
            postfix += "_s" # for static
        if self.settings.build_type == "Debug":
            postfix += "_d"

        return postfix

    def package_info(self):
        minpack_include_dir = os.path.join("include", "cminpack-1")
        self.cpp_info.set_property("cmake_target_name", "cminpack")
        # the double precision version
        self.cpp_info.components['cminpack-double'].libs = ['cminpack' + self._library_postfix()]
        self.cpp_info.components['cminpack-double'].includedirs.append(minpack_include_dir)
        self.cpp_info.components["cminpack-double"].set_property("cmake_target_name", "cminpack::cminpack")

        # the single precision version
        self.cpp_info.components['cminpack-single'].libs = ['cminpacks' + self._library_postfix()]
        self.cpp_info.components['cminpack-single'].includedirs.append(minpack_include_dir)
        self.cpp_info.components['cminpack-single'].defines.append("__cminpack_float__")
        self.cpp_info.components["cminpack-single"].set_property("cmake_target_name", "cminpack::cminpacks")

        if self.settings.os != "Windows":
            self.cpp_info.components['cminpack-double'].system_libs.append("m")
            self.cpp_info.components['cminpack-single'].system_libs.append("m")

        # required apple frameworks
        if is_apple_os(self):
            self.cpp_info.components['cminpack-double'].frameworks.append("Accelerate")
            self.cpp_info.components['cminpack-single'].frameworks.append("Accelerate")

        if not self.options.shared and self.settings.os == "Windows":
            self.cpp_info.components['cminpack-double'].defines.append("CMINPACK_NO_DLL")
            self.cpp_info.components['cminpack-single'].defines.append("CMINPACK_NO_DLL")
