from conans import ConanFile, CMake, tools

import os

class HyperscanConan(ConanFile):
    name = "hyperscan"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.hyperscan.io"
    description = "High-performance regular expression matching library"
    topics = ("regex", "regular expressions")
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "optimise": [True, False],
        "debug_output": [True, False],
        "build_avx512": [True, False],
        "fat_runtime": [True, False],
        "build_chimera": [True, False],
        "dump_support": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "optimise": True,
        "debug_output": False,
        "build_avx512": False,
        "fat_runtime": False,
        "build_chimera": False,
        "dump_support": False
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("hyperscan-{0}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        self.build_requires("boost/1.73.0");
        self.build_requires("ragel/6.10");

    def requirements(self):
        if self.options.build_chimera:
            self.required("pcre/8.41")

    def _configure_cmake(self):
        cmake = CMake(self);
        cmake.definitions["OPTIMISE"] = self.options.optimise
        cmake.definitions["DEBUG_OUTPUT"] = self.options.debug_output
        cmake.definitions["BUILD_AVX512"] = self.options.build_avx512
        cmake.definitions["FAT_RUNTIME"] = self.options.fat_runtime
        cmake.definitions["BUILD_CHIMERA"] = self.options.build_chimera
        cmake.definitions["DUMP_SUPPORT"] = self.options.dump_support
        cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return cmake

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libhs"
        self.cpp_info.libs = tools.collect_libs(self)
