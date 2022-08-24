from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration

import os

required_conan_version = ">=1.43.0"

class HyperscanConan(ConanFile):
    name = "hyperscan"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.hyperscan.io"
    description = "High-performance regular expression matching library"
    topics = ("regex", "regular expressions")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake", "cmake_find_package"

    _cmake = None

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "optimise": [True, False, "auto"],
        "debug_output": [True, False, "auto"],
        "build_avx512": [True, False],
        "fat_runtime": [True, False],
        "build_chimera": [True, False],
        "dump_support": [True, False, "auto"]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "optimise": "auto",
        "debug_output": "auto",
        "build_avx512": False,
        "fat_runtime": False,
        "build_chimera": False,
        "dump_support": "auto"
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version])
        os.rename("hyperscan-{0}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        self.build_requires("ragel/6.10");

    def requirements(self):
        self.requires("boost/1.79.0");
        if self.options.build_chimera:
            self.requires("pcre/8.45")

    def validate(self):
        tools.check_min_cppstd(self, "11")

        if self.settings.arch not in ["x86", "x86_64"]:
            raise ConanInvalidConfiguration("Hyperscan only support x86 architecture")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self);
        if self.options.optimise != "auto":
            self._cmake.definitions["OPTIMISE"] = self.options.optimise
        if self.options.debug_output != "auto":
            self._cmake.definitions["DEBUG_OUTPUT"] = self.options.debug_output
        self._cmake.definitions["BUILD_AVX512"] = self.options.build_avx512
        self._cmake.definitions["FAT_RUNTIME"] = self.options.fat_runtime
        self._cmake.definitions["BUILD_CHIMERA"] = self.options.build_chimera
        if self.options.dump_support != "auto":
            self._cmake.definitions["DUMP_SUPPORT"] = self.options.dump_support
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.options.shared and self.options.build_chimera:
            raise ConanInvalidConfiguration("Chimera build requires static building")

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "hyperscan"
        self.cpp_info.names["cmake_find_package_multi"] = "hyperscan"

        self.cpp_info.components["hs"].libs = ["hs"]
        self.cpp_info.components["hs"].requires = ["boost::headers"]
        self.cpp_info.components["hs"].names["cmake_find_package"] = "hs"
        self.cpp_info.components["hs"].names["cmake_find_package_multi"] = "hs"
        self.cpp_info.components["hs"].set_property("cmake_target_name", "hyperscan::hs")
        self.cpp_info.components["hs"].set_property("pkg_config_name", "libhs")


        self.cpp_info.components["hs_runtime"].libs = ["hs_runtime"]
        self.cpp_info.components["hs_runtime"].names["cmake_find_package"] = "hs_runtime"
        self.cpp_info.components["hs_runtime"].names["cmake_find_package_multi"] = "hs_runtime"
        self.cpp_info.components["hs_runtime"].set_property("cmake_target_name", "hyperscan::hs_runtime")
        self.cpp_info.components["hs_runtime"].set_property("pkg_config_name", "libhs_runtime")


        if self.options.build_chimera:
            self.cpp_info.components["chimera"].libs = ["chimera"]
            self.cpp_info.components["chimera"].requires = ["pcre::libpcre", "hs"]
            self.cpp_info.components["chimera"].names["cmake_find_package"] = "chimera"
            self.cpp_info.components["chimera"].names["cmake_find_package_multi"] = "chimera"
            self.cpp_info.components["chimera"].set_property("cmake_target_name", "hyperscan::chimera")
            self.cpp_info.components["chimera"].set_property("pkg_config_name", "libchimera")



        if not self.options.shared:
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.components["hs"].system_libs = ["m"]
                self.cpp_info.components["hs_runtime"].system_libs = ["m"]

                if self.options.build_chimera:
                    self.cpp_info.components["chimera"].system_libs = ["m"]

