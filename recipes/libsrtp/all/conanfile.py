from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, save, rmdir
from conan.tools.scm import Version
from conan.tools.env import VirtualBuildEnv
import os

required_conan_version = ">=1.53.0"


class LibsrtpRecipe(ConanFile):
    name = "libsrtp"
    description = (
        "This package provides an implementation of the Secure Real-time Transport"
        "Protocol (SRTP), the Universal Security Transform (UST), and a supporting"
        "cryptographic kernel."
    )
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/cisco/libsrtp"
    topics = ("srtp",)
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openssl": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/[>=1.1 <4]")

    def build_requirements(self):
        if Version(self.version) >= "2.6.0":
            self.tool_requires("cmake/[>=3.21 <4]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_OPENSSL"] = self.options.with_openssl
        if  Version(self.version) < "2.6.0":
            tc.variables["TEST_APPS"] = False
        else:
            tc.variables["LIBSRTP_TEST_APPS"] = False
        if Version(self.version) < "2.4.0":
            # Relocatable shared libs on Macos
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        if  "2.5.0" <= Version(self.version) < "2.6.0":
            tc.cache_variables["BUILD_WITH_WARNINGS"] = False
        if  "2.6.0" <= Version(self.version):
            tc.cache_variables["ENABLE_WARNINGS"] = False
            tc.cache_variables["ENABLE_WARNINGS_AS_ERRORS"] = False
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()
        venv = VirtualBuildEnv(self)
        venv.generate(scope="build")

    def _patch_sources(self):
        save(self, os.path.join(self.source_folder, "CMakeLists.txt"),
             "\ninstall(TARGETS srtp2 RUNTIME DESTINATION bin LIBRARY DESTINATION lib ARCHIVE DESTINATION lib)\n",
             append=True)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", f"libsrtp{Version(self.version).major}")
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
