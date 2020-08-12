import os

from conans import ConanFile, CMake, tools


class OneDplConan(ConanFile):
    name = "onedpl"
    description = ("OneDPL (Formerly Parallel STL) is an implementation of "
                   "the C++ standard library algorithms"
                   "with support for execution policies, as specified in "
                   "ISO/IEC 14882:2017 standard, commonly called C++17")
    license = ("Apache-2.0", "LLVM-exception")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneDPL"
    topics = ("stl", "parallelism")
    settings = "os", "arch", "build_type", "compiler"
    options = {"backend": ["tbb", "serial"]}
    default_options = {"backend": "tbb"}
    generators = ["cmake", "cmake_find_package"]
    exports = ["CMakeLists.txt"]
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return os.path.join(self.source_folder, "oneDPL-{}".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])

    def requirements(self):
        if self.options.backend == "tbb":
            self.requires("tbb/2020.1")

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PARALLELSTL_BACKEND"] = self.options.backend
        cmake.definitions["INTEL_PSTL_VERSION"] = self.version
        cmake.configure()
        return cmake

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*", src=os.path.join(self._source_subfolder, "stdlib"), dst=os.path.join("lib", "stdlib"))
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.includedirs = ["include", os.path.join("lib", "stdlib")]
        self.cpp_info.names["cmake_find_package"] = "ParallelSTL"
        self.cpp_info.names["cmake_find_package_multi"] = "ParallelSTL"

    def package_id(self):
        self.info.header_only()
