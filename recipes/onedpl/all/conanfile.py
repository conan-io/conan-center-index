import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
from conan.tools import files

required_conan_version = ">=1.43.0"

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
    options = {
        "backend": ["tbb", "serial"]
    }
    default_options = {
        "backend": "tbb"
    }
    generators = ["cmake", "cmake_find_package"]
    exports = ["CMakeLists.txt"]
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.options.backend == "tbb" and not self.options["tbb"].tbbmalloc:
            raise ConanInvalidConfiguration(f"recipe {self.name}/{self.version} with backend=tbb requires tbb:malloc")

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.options.backend == "tbb":
            # Listed as an OPTIONAL_COMPONENT but optional components not supported by conan
            self.options["tbb"].tbbmalloc = True

    def requirements(self):
        if self.options.backend == "tbb":
            self.requires("tbb/2020.2")

    def package_id(self):
        self.info.header_only()

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["PARALLELSTL_BACKEND"] = self.options.backend
        cmake.configure()
        return cmake

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("*", src=os.path.join(self._source_subfolder, "stdlib"), dst=os.path.join("lib", "stdlib"))
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        target_name = "ParallelSTL"
        namespace = "pstl"
        self.cpp_info.filenames["cmake_find_package"] = target_name
        self.cpp_info.filenames["cmake_find_package_multi"] = target_name
        self.cpp_info.names["cmake_find_package"] = namespace
        self.cpp_info.names["cmake_find_package_multi"] = namespace
        self.cpp_info.set_property("cmake_file_name", target_name)
        self.cpp_info.set_property("cmake_target_name", f"{namespace}::{target_name}")
        self.cpp_info.components["_onedpl"].names["cmake_find_package"] = target_name
        self.cpp_info.components["_onedpl"].names["cmake_find_package_multi"] = target_name
        self.cpp_info.components["_onedpl"].includedirs = ["include", os.path.join("lib", "stdlib")]
        if self.options.backend == "tbb":
            self.cpp_info.components["_onedpl"].requires = ["tbb::libtbb", "tbb::tbbmalloc"]
