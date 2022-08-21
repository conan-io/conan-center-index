from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rm, rmdir
from conans import tools as tools_legacy
import os

required_conan_version = ">=1.50.0"


class NloptConan(ConanFile):
    name = "nlopt"
    description = "Library for nonlinear optimization, wrapping many " \
                  "algorithms for global and local, constrained or " \
                  "unconstrained, optimization."
    license = ["LGPL-2.1-or-later", "MIT"]
    topics = ("nlopt", "optimization", "nonlinear")
    homepage = "https://github.com/stevengj/nlopt"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cxx_routines": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cxx_routines": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.enable_cxx_routines:
            try:
                del self.settings.compiler.libcxx
            except Exception:
                pass
            try:
                del self.settings.compiler.cppstd
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NLOPT_CXX"] = self.options.enable_cxx_routines
        tc.variables["NLOPT_FORTRAN"] = False
        tc.variables["NLOPT_PYTHON"] = False
        tc.variables["NLOPT_OCTAVE"] = False
        tc.variables["NLOPT_MATLAB"] = False
        tc.variables["NLOPT_GUILE"] = False
        tc.variables["NLOPT_SWIG"] = False
        tc.variables["NLOPT_TESTS"] = False
        tc.variables["WITH_THREADLOCAL"] = True
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def _patch_sources(self):
        # don't force PIC
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        replace_in_file(self, cmakelists, "set (CMAKE_C_FLAGS \"-fPIC ${CMAKE_C_FLAGS}\")", "")
        replace_in_file(self, cmakelists, "set (CMAKE_CXX_FLAGS \"-fPIC ${CMAKE_CXX_FLAGS}\")", "")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        algs_licenses = [
            {"subdir": "ags"   , "license_name": "COPYRIGHT"},
            {"subdir": "bobyqa", "license_name": "COPYRIGHT"},
            {"subdir": "cobyla", "license_name": "COPYRIGHT"},
            {"subdir": "direct", "license_name": "COPYING"  },
            {"subdir": "esch"  , "license_name": "COPYRIGHT"},
            {"subdir": "luskan", "license_name": "COPYRIGHT"},
            {"subdir": "newuoa", "license_name": "COPYRIGHT"},
            {"subdir": "slsqp" , "license_name": "COPYRIGHT"},
            {"subdir": "stogo" , "license_name": "COPYRIGHT"},
        ]
        for alg_license in algs_licenses:
            copy(self, alg_license["license_name"],
                      src=os.path.join(self.source_folder, "src", "algs", alg_license["subdir"]),
                      dst=os.path.join(self.package_folder, "licenses", alg_license["subdir"]))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "NLopt")
        self.cpp_info.set_property("cmake_target_name", "NLopt::nlopt")
        self.cpp_info.set_property("pkg_config_name", "nlopt")

        self.cpp_info.names["cmake_find_package"] = "NLopt"
        self.cpp_info.names["cmake_find_package_multi"] = "NLopt"
        self.cpp_info.components["nloptlib"].names["cmake_find_package"] = "nlopt"
        self.cpp_info.components["nloptlib"].names["cmake_find_package_multi"] = "nlopt"
        self.cpp_info.components["nloptlib"].set_property("cmake_target_name", "NLopt::nlopt")
        self.cpp_info.components["nloptlib"].set_property("pkg_config_name", "nlopt")

        self.cpp_info.components["nloptlib"].libs = ["nlopt"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["nloptlib"].system_libs.append("m")
        if not self.options.shared and self.options.enable_cxx_routines:
            libcxx = tools_legacy.stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["nloptlib"].system_libs.append(libcxx)
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["nloptlib"].defines.append("NLOPT_DLL")
