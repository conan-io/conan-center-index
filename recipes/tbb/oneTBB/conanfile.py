from conan.tools.cmake import CMake, CMakeToolchain
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import re

required_conan_version = ">=1.37.0"

class ConanFile(ConanFile):
    name = "tbb"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneTBB"
    description = (
        "oneAPI Threading Building Blocks (oneTBB) lets you easily write parallel C++"
        " programs that take full advantage of multicore performance, that are portable, composable"
        " and have future-proof scalability."
    )
    topics = ("tbb", "threading", "parallelism", "tbbmalloc")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tbbmalloc": [True, False],
        "tbbproxy": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "tbbmalloc": False,
        "tbbproxy": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if tools.Version(self.version) < "2021.2.0":
            del self.options.shared
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("shared", True):
            del self.options.fPIC
        if (self.settings.os == "Macos" and
           self.settings.compiler == "apple-clang" and
           tools.Version(self.settings.compiler.version) < "8.0"):
            raise ConanInvalidConfiguration("%s %s couldn't be built by apple-clang < 8.0" % (self.name, self.version))
        if not self.options.get_safe("shared", True):
            self.output.warn("oneTBB strongly discourages usage of static linkage")
        if self.options.tbbproxy and not (self.options.tbbmalloc and self.options.get_safe("shared", True)):
            raise ConanInvalidConfiguration("tbbproxy needs tbbmalloc and shared options")

    def package_id(self):
        del self.info.options.tbbmalloc
        del self.info.options.tbbproxy

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination="src")

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["TBB_TEST"] = False
        toolchain.variables["CMAKE_INSTALL_LIBDIR"] = "lib"
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="src")
        cmake.build()

    def package(self):
        CMake(self).install()
        self.copy(os.path.join("src", "LICENSE.txt"), dst="licenses")

        # Remove cmake targets
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

        # Remove documentation
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "TBB"
        self.cpp_info.names["cmake_find_package_multi"] = "TBB"
        # tbb
        self.cpp_info.components["libtbb"].names["cmake_find_package"] = "tbb"
        self.cpp_info.components["libtbb"].names["cmake_find_package_multi"] = "tbb"
        self.cpp_info.components["libtbb"].libs = [self._lib_name("tbb")]
        if self.settings.os == "Windows":
            version_info = tools.load(os.path.join(self.package_folder, "include", "oneapi", "tbb", "version.h"))
            binary_version = re.sub(
                r".*" + re.escape("#define __TBB_BINARY_VERSION ") + r"(\d+).*",
                r"\1",
                version_info,
                flags=re.MULTILINE | re.DOTALL
            )
            self.cpp_info.components["libtbb"].libs.append(self._lib_name("tbb{}".format(binary_version)))
        if self.settings.os == "Linux":
            self.cpp_info.components["libtbb"].system_libs = ["dl", "rt", "pthread"]
        # tbbmalloc
        if self.options.tbbmalloc:
            self.cpp_info.components["tbbmalloc"].names["cmake_find_package"] = "tbbmalloc"
            self.cpp_info.components["tbbmalloc"].names["cmake_find_package_multi"] = "tbbmalloc"
            self.cpp_info.components["tbbmalloc"].libs = [self._lib_name("tbbmalloc")]
            if self.settings.os == "Linux":
                self.cpp_info.components["tbbmalloc"].system_libs = ["dl", "pthread"]
            # tbbmalloc_proxy
            if self.options.tbbproxy:
                self.cpp_info.components["tbbmalloc_proxy"].names["cmake_find_package"] = "tbbmalloc_proxy"
                self.cpp_info.components["tbbmalloc_proxy"].names["cmake_find_package_multi"] = "tbbmalloc_proxy"
                self.cpp_info.components["tbbmalloc_proxy"].libs = [self._lib_name("tbbmalloc_proxy")]
                self.cpp_info.components["tbbmalloc_proxy"].requires = ["tbbmalloc"]

    def _lib_name(self, name):
        if self.settings.build_type == "Debug":
            return name + "_debug"
        return name
