from conan import ConanFile, tools
from conans import CMake
from conan.tools.microsoft import msvc_runtime_flag
import os

required_conan_version = ">=1.43.0"


class rpclibConan(ConanFile):
    name = "rpclib"
    description = "A modern C++ msgpack-RPC server and client library."
    license = "MIT"
    topics = ("rpc", "ipc", "rpc-server")
    homepage = "https://github.com/rpclib/rpclib/"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/*"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
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

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        if "MT" in str(msvc_runtime_flag(self)):
            self._cmake.definitions["RPCLIB_MSVC_STATIC_RUNTIME"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "rpclib")
        self.cpp_info.set_property("cmake_target_name", "rpclib::rpc")
        self.cpp_info.set_property("pkg_config_name", "rpclib")

        # Fix for installing dll to lib folder
        # - Default CMAKE installs the dll to the lib folder
        #   causing the test_package to fail
        if self.settings.os in ["Windows"]:
            if self.options.shared:
                self.cpp_info.components["_rpc"].bindirs.append(
                    os.path.join(self.package_folder, "lib"))

        # TODO: Remove after Conan 2.0
        self.cpp_info.components["_rpc"].names["cmake_find_package"] = "rpc"
        self.cpp_info.components["_rpc"].names["cmake_find_package_multi"] = "rpc"
        self.cpp_info.components["_rpc"].libs = ["rpc"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["_rpc"].system_libs = ["pthread"]
        self.cpp_info.names["pkg_config"] = "librpc"
