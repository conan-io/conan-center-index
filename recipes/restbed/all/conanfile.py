from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm
import os
import textwrap

required_conan_version = ">=1.52.0"


class RestbedConan(ConanFile):
    name = "restbed"
    homepage = "https://github.com/Corvusoft/restbed"
    description = "Corvusoft's Restbed framework brings asynchronous RESTful functionality to C++14 applications."
    topics = ("restbed", "restful", "server", "client", "json", "http", "ssl", "tls")
    url = "https://github.com/conan-io/conan-center-index"
    license = "AGPL-3.0-or-later", "CPL"  # Corvusoft Permissive License (CPL)

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "ssl": [True, False],
        "ipc": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "ssl": True,
        "ipc": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        if self.settings.os in ("Windows", ):
            del self.options.ipc

    def validate(self):
        if self.settings.os in ("Windows", ) and not self.options.shared:
            # The headers don't allow to avoid __declspec(dllimport)/__declsped(dllexport)
            raise ConanInvalidConfiguration("Static libraries for Windows are not supported")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("asio/1.24.0")
        if self.options.ssl:
            self.requires("openssl/3.0.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_SSL"] = self.options.ssl
        tc.variables["BUILD_IPC"] = self.options.get_safe("ipc", False)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    @property
    def _libzmq_target(self):
        return "libzmq" if self.options.shared else "libzmq-static"

    def package_info(self):
        libname = "restbed"
        if self.settings.os in ("Windows", ) and self.options.shared:
            libname += "-shared"
        self.cpp_info.libs = [libname]

        if self.settings.os in ("FreeBSD", "Linux", ):
            self.cpp_info.system_libs.append("dl")
