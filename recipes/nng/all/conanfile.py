from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy, rmdir
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=2.0"

class NngConan(ConanFile):
    name = "nng"
    description = "nanomsg-next-generation: light-weight brokerless messaging"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nanomsg/nng"
    topics = ("nanomsg", "communication", "messaging", "protocols")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "nngcat": [True, False],
        "http": [True, False],
        "tls": [True, False],
        "max_taskq_threads": ["ANY"],
        "max_expire_threads": ["ANY"],
        "max_poller_threads": ["ANY"],
        "compat": [True, False],
        "with_ipv6": [True, False],
        "tls_engine": ["mbed", "wolf"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "nngcat": False,
        "http": True,
        "tls": False,
        "max_taskq_threads": "16",
        "max_expire_threads": "8",
        "max_poller_threads": "8",
        "compat": True,
        "with_ipv6": True,
        "tls_engine": "mbed",
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
        if self.options.tls:
            tls_engine = self.options.get_safe("tls_engine", "mbed")
            if tls_engine == "mbed":
                self.requires("mbedtls/[>=3.5.2 <4]")
            elif tls_engine == "wolf":
                self.requires("wolfssl/[>=5.7.2 <6]")

    def validate(self):
        if not self.options.max_taskq_threads.value.isdigit():
            raise ConanInvalidConfiguration("max_taskq_threads must be an integral number")
        if "max_expire_threads" in self.options and not self.options.max_expire_threads.value.isdigit():
            raise ConanInvalidConfiguration("max_expire_threads must be an integral number")
        if "max_poller_threads" in self.options and not self.options.max_poller_threads.value.isdigit():
            raise ConanInvalidConfiguration("max_poller_threads must be an integral number")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NNG_TESTS"] = False
        tc.variables["NNG_ENABLE_TLS"] = self.options.tls
        tc.variables["NNG_ENABLE_NNGCAT"] = self.options.nngcat
        tc.variables["NNG_ENABLE_HTTP"] = self.options.http
        tc.variables["NNG_MAX_TASKQ_THREADS"] = self.options.max_taskq_threads
        if "max_expire_threads" in self.options:
            tc.variables["NNG_MAX_EXPIRE_THREADS"] = self.options.max_expire_threads
        if "max_poller_threads" in self.options:
            tc.variables["NNG_MAX_POLLER_THREADS"] = self.options.max_poller_threads
        if "compat" in self.options:
            tc.variables["NNG_ENABLE_COMPAT"] = self.options.compat
        if "with_ipv6" in self.options:
            tc.variables["NNG_ENABLE_IPV6"] = self.options.with_ipv6
        tc.variables["NNG_TLS_ENGINE"] = self.options.get_safe("tls_engine", "mbed")

        # Prevent linking against unused found library
        #https://github.com/nanomsg/nng/blob/8396f1df0420bb0156655532b5e6244dc1b3b646/src/platform/posix/CMakeLists.txt#L50C9-L50C22
        tc.cache_variables["NNG_HAVE_LIBNSL"] = "0"

        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "nng")
        self.cpp_info.set_property("cmake_target_name", "nng::nng")

        self.cpp_info.libs = ["nng"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.system_libs.extend(["mswsock", "ws2_32"])
        elif self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "rt"])

        if self.options.shared:
            self.cpp_info.defines.append("NNG_SHARED_LIB")
        else:
            self.cpp_info.defines.append("NNG_STATIC_LIB")
