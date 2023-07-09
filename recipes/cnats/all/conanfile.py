from conan import ConanFile
from conan.tools.files import get, copy, rename, mkdir, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"


class PackageConan(ConanFile):
    name = "cnats"
    description = "A C client for NATS"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nats.io/"
    topics = ("messaging", "message-bus", "message-queue", "messaging-library", "nats-client")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_tls": [True, False],
        "with_sodium": [True, False],
        "enable_streaming": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_tls": False,
        "with_sodium": False,
        "enable_streaming": True
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_tls:
            self.requires("openssl/[>=1.1 <4]")
        if self.options.with_sodium:
            self.requires("libsodium/cci.20220430")
        if self.options.enable_streaming:
            self.requires("protobuf-c/1.4.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NATS_BUILD_WITH_TLS"] = self.options.with_tls
        tc.variables["NATS_BUILD_USE_SODIUM"] = self.options.with_sodium
        tc.variables["NATS_BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["NATS_BUILD_LIB_STATIC"] = not self.options.shared
        tc.variables["NATS_BUILD_LIB_SHARED"] = self.options.shared
        if self.options.with_tls:
            tc.variables["NATS_BUILD_TLS_USE_OPENSSL_1_1_API"] = self.dependencies["openssl"].ref.version.major > 1
        tc.variables["NATS_BUILD_STREAMING"] = self.options.enable_streaming
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        if self.settings.os == "Windows" and self.options.shared:
            mkdir(self, os.path.join(self.package_folder, "bin"))
            rename(self, os.path.join(self.package_folder, "lib", f"{self._nats_library_name}.dll"), os.path.join(self.package_folder, "bin", f"{self._nats_library_name}.dll"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    @property
    def _nats_library_name(self):
        suffix = "" if self.options.shared else "_static"
        debug = "d" if self.settings.build_type == "Debug" else ""
        return f"nats{suffix}{debug}"

    def package_info(self):
        self.cpp_info.libs = [self._nats_library_name]
        self.cpp_info.set_property("cmake_file_name", "cnats")
        self.cpp_info.set_property("cmake_target_name", f"cnats::{self._nats_library_name}")
        self.cpp_info.set_property("pkg_config_name", "libnats")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "rt"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "cnats"
        self.cpp_info.filenames["cmake_find_package_multi"] = "cnats"
        self.cpp_info.names["cmake_find_package"] = self._nats_library_name
        self.cpp_info.names["cmake_find_package_multi"] = self._nats_library_name
