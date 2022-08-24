from conan import ConanFile, tools
from conans import CMake
import os

required_conan_version = ">=1.43.0"


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

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if not self.options.enable_cxx_routines:
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _patch_sources(self):
        # don't force PIC
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.replace_in_file(cmakelists, "set (CMAKE_C_FLAGS \"-fPIC ${CMAKE_C_FLAGS}\")", "")
        tools.replace_in_file(cmakelists, "set (CMAKE_CXX_FLAGS \"-fPIC ${CMAKE_CXX_FLAGS}\")", "")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["NLOPT_CXX"] = self.options.enable_cxx_routines
        self._cmake.definitions["NLOPT_FORTRAN"] = False
        self._cmake.definitions["NLOPT_PYTHON"] = False
        self._cmake.definitions["NLOPT_OCTAVE"] = False
        self._cmake.definitions["NLOPT_MATLAB"] = False
        self._cmake.definitions["NLOPT_GUILE"] = False
        self._cmake.definitions["NLOPT_SWIG"] = False
        self._cmake.definitions["NLOPT_TESTS"] = False
        self._cmake.definitions["WITH_THREADLOCAL"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
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
            self.copy(alg_license["license_name"],
                      dst=os.path.join("licenses", alg_license["subdir"]),
                      src= os.path.join(self._source_subfolder, "src", "algs", alg_license["subdir"]))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")

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
        if not self.options.shared and self.options.enable_cxx_routines and tools.stdcpp_library(self):
            self.cpp_info.components["nloptlib"].system_libs.append(tools.stdcpp_library(self))
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.components["nloptlib"].defines.append("NLOPT_DLL")
