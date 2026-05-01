from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc, msvc_runtime_flag
from conan.tools.files import get, copy, rmdir, replace_in_file, export_conandata_patches, apply_conandata_patches
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os

required_conan_version = ">=2.0"

class TrantorConan(ConanFile):
    name = "trantor"
    description = "a non-blocking I/O tcp network lib based on c++14/17"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/an-tao/trantor"
    topics = ("tcp-server", "asynchronous-programming", "non-blocking-io")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "shared": [True, False],
        "with_c_ares": [True, False],
        "with_spdlog": [True, False],
    }
    default_options = {
        "fPIC": True,
        "shared": False,
        "with_c_ares": True,
        "with_spdlog": False,
        "spdlog/*:header_only": True,
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

    def requirements(self):
        self.requires("openssl/[>=1.1 <4]")
        if self.options.with_c_ares:
            self.requires("c-ares/[>=1.25 <2]")
        if self.options.get_safe("with_spdlog"):
            self.requires("spdlog/[>=1.13 <2]")

    def validate(self):
        check_min_cppstd(self, 14)

        # TODO: Compilation succeeds, but execution of test_package fails on Visual Studio with MDd
        if is_msvc(self) and self.options.shared and "MDd" in msvc_runtime_flag(self):
            raise ConanInvalidConfiguration(f"{self.ref} does not support the MDd runtime on Visual Studio.")

        if self.options.get_safe("with_spdlog") and not self.dependencies["spdlog"].options.header_only:
            raise ConanInvalidConfiguration(f"{self.ref} requires header_only spdlog.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        # fix c-ares imported target
        replace_in_file(self, cmakelists, "c-ares_lib", "c-ares::cares")
        # Cleanup rpath in shared lib
        replace_in_file(self, cmakelists, "set(CMAKE_INSTALL_RPATH \"${CMAKE_INSTALL_PREFIX}/${INSTALL_LIB_DIR}\")", "")

    def generate(self):
        tc = CMakeToolchain(self)
        # TODO: support other tls providers
        tc.cache_variables["TRANTOR_USE_TLS"] = "openssl"
        tc.cache_variables["BUILD_C-ARES"] = self.options.with_c_ares
        tc.cache_variables["USE_SPDLOG"] = self.options.get_safe("with_spdlog")
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
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Trantor")
        self.cpp_info.set_property("cmake_target_name", "Trantor::Trantor")
        self.cpp_info.libs = ["trantor"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
            self.cpp_info.system_libs.append("m")
