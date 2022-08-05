from conan.tools.cmake import CMake, CMakeToolchain
from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import re

required_conan_version = ">=1.43.0"


class OneTBBConan(ConanFile):
    name = "onetbb"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/oneapi-src/oneTBB"
    description = (
        "oneAPI Threading Building Blocks (oneTBB) lets you easily write parallel C++"
        " programs that take full advantage of multicore performance, that are portable, composable"
        " and have future-proof scalability.")
    topics = ("tbb", "threading", "parallelism", "tbbmalloc")

    settings = "os", "arch", "compiler", "build_type"
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

    def validate(self):
        if (self.settings.os == "Macos"
                and self.settings.compiler == "apple-clang"
                and tools.Version(self.settings.compiler.version) < "11.0"):
            raise ConanInvalidConfiguration(
                "{} {} couldn't be built by apple-clang < 11.0".format(
                    self.name,
                    self.version,
                ))
        if not self.options.get_safe("shared", True):
            self.output.warn(
                "oneTBB strongly discourages usage of static linkage")
        if (self.options.tbbproxy
                and not (self.options.tbbmalloc
                         and self.options.get_safe("shared", True))):
            raise ConanInvalidConfiguration(
                "tbbproxy needs tbbmalloc and shared options")

    def package_id(self):
        del self.info.options.tbbmalloc
        del self.info.options.tbbproxy

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination="src",
        )

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["TBB_TEST"] = False
        toolchain.variables["TBB_STRICT"] = False
        toolchain.variables["CMAKE_INSTALL_BINDIR"] = "bin"
        toolchain.variables["CMAKE_INSTALL_SBINDIR"] = "bin"
        toolchain.variables["CMAKE_INSTALL_LIBEXECDIR"] = "bin"
        toolchain.variables["CMAKE_INSTALL_LIBDIR"] = "lib"
        toolchain.variables["CMAKE_INSTALL_INCLUDEDIR"] = "include"
        toolchain.variables["CMAKE_INSTALL_OLDINCLUDEDIR"] = "include"
        toolchain.variables["CMAKE_INSTALL_DATAROOTDIR"] = "share"
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="src")
        cmake.build()

    def package(self):
        CMake(self).install()
        self.copy(os.path.join("src", "LICENSE.txt"), dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "TBB")
        self.cpp_info.set_property("pkg_config_name", "tbb")

        def lib_name(name):
            if self.settings.build_type == "Debug":
                return name + "_debug"
            return name

        # tbb
        tbb = self.cpp_info.components["libtbb"]

        tbb.set_property("cmake_target_name", "TBB::tbb")
        tbb.libs = [lib_name("tbb")]
        if self.settings.os == "Windows":
            version_info = tools.load(
                os.path.join(self.package_folder, "include", "oneapi", "tbb",
                             "version.h"))
            binary_version = re.sub(
                r".*" + re.escape("#define __TBB_BINARY_VERSION ") +
                r"(\d+).*",
                r"\1",
                version_info,
                flags=re.MULTILINE | re.DOTALL,
            )
            tbb.libs.append(lib_name("tbb{}".format(binary_version)))
        if self.settings.os in ["Linux", "FreeBSD"]:
            tbb.system_libs = ["dl", "rt", "pthread"]

        # tbbmalloc
        if self.options.tbbmalloc:
            tbbmalloc = self.cpp_info.components["tbbmalloc"]

            tbbmalloc.set_property("cmake_target_name", "TBB::tbbmalloc")
            tbbmalloc.libs = [lib_name("tbbmalloc")]
            if self.settings.os in ["Linux", "FreeBSD"]:
                tbbmalloc.system_libs = ["m", "dl", "pthread"]

            # tbbmalloc_proxy
            if self.options.tbbproxy:
                tbbproxy = self.cpp_info.components["tbbmalloc_proxy"]

                tbbproxy.set_property("cmake_target_name", "TBB::tbbmalloc_proxy")
                tbbproxy.libs = [lib_name("tbbmalloc_proxy")]
                tbbproxy.requires = ["tbbmalloc"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "TBB"
        self.cpp_info.names["cmake_find_package_multi"] = "TBB"
        self.cpp_info.names["pkg_config"] = "tbb"
        tbb.names["cmake_find_package"] = "tbb"
        tbb.names["cmake_find_package_multi"] = "tbb"
