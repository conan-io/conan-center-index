from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"

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
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if Version(self.version) < "1.6.0":
            del self.options.max_expire_threads
        if Version(self.version) < "1.7.0":
            del self.options.max_poller_threads
        if Version(self.version) < "1.7.2":
            del self.options.compat
        if Version(self.version) < "1.7.3":
            del self.options.with_ipv6

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.tls:
            if Version(self.version) < "1.5.2":
                self.requires("mbedtls/2.25.0")
            else:
                self.requires("mbedtls/3.5.2")

    def validate(self):
        compiler_minimum_version = {
            "Visual Studio": "14",
            "msvc": "190",
        }
        minimum_version = compiler_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.settings.compiler} < {minimum_version} is not supported",
            )
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
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
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
            self.cpp_info.system_libs.extend(["pthread", "rt", "nsl"])

        if self.options.shared:
            self.cpp_info.defines.append("NNG_SHARED_LIB")
        else:
            self.cpp_info.defines.append("NNG_STATIC_LIB")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "nng"
        self.cpp_info.names["cmake_find_package_multi"] = "nng"
