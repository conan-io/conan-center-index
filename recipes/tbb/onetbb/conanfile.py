import os

from conans import ConanFile, CMake, tools
from conans.tools import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class TBBConan(ConanFile):
    name = "tbb"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneTBB"
    description = """Intel Threading Building Blocks (Intel TBB) lets you easily write parallel C++
    programs that take full advantage of multicore performance, that are portable and composable, and
    that have future-proof scalability"""
    topics = ("conan", "tbb", "threading", "parallelism", "tbbmalloc")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tbbmalloc": [True, False],
        "tbbproxy": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "tbbmalloc": False,
        "tbbproxy": False
    }
    exports_sources = ["CMakeLists.txt"]
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self.settings.os == "Macos" and \
            self.settings.compiler == "apple-clang" and \
            tools.Version(self.settings.compiler.version) < "8.0":
            raise ConanInvalidConfiguration(f"{self.name}/{self.version} couldn not be built by apple-clang < 8.0")
        if not self.options.shared:
            self.output.warn("Intel-TBB strongly discourages usage of static linkage")
        if self.options.tbbproxy and (not self.options.shared or not self.options.tbbmalloc):
            raise ConanInvalidConfiguration(f"{self.name}/{self.version} with tbbproxy needs tbbmalloc and shared options")

    def package_id(self):
        del self.info.options.tbbmalloc
        del self.info.options.tbbproxy

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions.update({
            "TBB_TEST": False,
            "TBB_DISABLE_HWLOC_AUTOMATIC_SEARCH": True
        })
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(self.package_folder, "*.pc")
        tools.remove_files_by_mask(self.package_folder, "*.cmake")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "TBB"
        self.cpp_info.names["cmake_find_package_multi"] = "TBB"
        self.cpp_info.components["libtbb"].names["cmake_find_package"] = "tbb"
        self.cpp_info.components["libtbb"].names["cmake_find_package_multi"] = "tbb"
        self.cpp_info.components["libtbb"].libs = [self._lib_name("tbb")]
        if self.settings.os == "Linux":
            self.cpp_info.components["libtbb"].system_libs = ["dl", "rt", "pthread"]
        if self.options.tbbmalloc:
            self.cpp_info.components["tbbmalloc"].names["cmake_find_package"] = "tbbmalloc"
            self.cpp_info.components["tbbmalloc"].names["cmake_find_package_multi"] = "tbbmalloc"
            self.cpp_info.components["tbbmalloc"].libs = [self._lib_name("tbbmalloc")]
            if self.settings.os == "Linux":
                self.cpp_info.components["tbbmalloc"].system_libs = ["dl", "pthread"]
            if self.options.tbbproxy:
                self.cpp_info.components["tbbmalloc_proxy"].names["cmake_find_package"] = "tbbmalloc_proxy"
                self.cpp_info.components["tbbmalloc_proxy"].names["cmake_find_package_multi"] = "tbbmalloc_proxy"
                self.cpp_info.components["tbbmalloc_proxy"].libs = [self._lib_name("tbbmalloc_proxy")]
                self.cpp_info.components["tbbmalloc_proxy"].requires = ["tbbmalloc"]

    def _lib_name(self, name):
        if self.settings.build_type == "Debug":
            return name + "_debug"
        return name
