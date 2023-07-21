import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, export_conandata_patches, get, rmdir, rename
from conan.tools.microsoft import msvc_runtime_flag
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class rpclibConan(ConanFile):
    name = "rpclib"
    description = "A modern C++ msgpack-RPC server and client library."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/rpclib/rpclib/"
    topics = ("rpc", "ipc", "rpc-server")

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

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "14.1",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if "MT" in str(msvc_runtime_flag(self)):
            tc.variables["RPCLIB_MSVC_STATIC_RUNTIME"] = True
        tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = self.options.shared
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        for dll in (self.package_path / "lib").glob("*.dll"):
            rename(self, dll, self.package_path / "bin" / dll.name)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "rpclib")
        self.cpp_info.set_property("cmake_target_name", "rpclib::rpc")
        self.cpp_info.set_property("pkg_config_name", "rpclib")

        # Fix for installing dll to lib folder
        # - Default CMAKE installs the dll to the lib folder
        #   causing the test_package to fail
        if self.settings.os in ["Windows"]:
            if self.options.shared:
                self.cpp_info.components["_rpc"].bindirs.append(os.path.join(self.package_folder, "lib"))

        # TODO: Remove after Conan 2.0
        self.cpp_info.components["_rpc"].names["cmake_find_package"] = "rpc"
        self.cpp_info.components["_rpc"].names["cmake_find_package_multi"] = "rpc"
        self.cpp_info.components["_rpc"].libs = ["rpc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_rpc"].system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            self.cpp_info.components["_rpc"].system_libs = ["ws2_32", "mswsock"]
