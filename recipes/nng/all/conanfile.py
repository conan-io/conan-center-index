from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"

class NngConan(ConanFile):
    name = "nng"
    description = "nanomsg-next-generation: light-weight brokerless messaging"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/nanomsg/nng"
    license = "MIT"
    topics = ("nanomsg", "communication", "messaging", "protocols")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "nngcat": [True, False],
        "http": [True, False],
        "tls": [True, False],
        "max_taskq_threads": ["ANY"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "nngcat": False,
        "http": True,
        "tls": False,
        "max_taskq_threads": "16"
    }

    def export_sources(self):
        export_conandata_patches(self)

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
            if Version(self.version) < "1.5.2":
                self.requires("mbedtls/2.25.0")
            else:
                self.requires("mbedtls/3.0.0")

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["NNG_TESTS"] = False
        tc.variables["NNG_ENABLE_TLS"] = self.options.tls
        tc.variables["NNG_ENABLE_NNGCAT"] = self.options.nngcat
        tc.variables["NNG_ENABLE_HTTP"] = self.options.http
        tc.variables["NNG_MAX_TASKQ_THREADS"] = self.options.max_taskq_threads
        tc.generate()

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
            self.cpp_info.system_libs.extend(["pthread"])

        if self.options.shared:
            self.cpp_info.defines.append("NNG_SHARED_LIB")
        else:
            self.cpp_info.defines.append("NNG_STATIC_LIB")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "nng"
        self.cpp_info.names["cmake_find_package_multi"] = "nng"
