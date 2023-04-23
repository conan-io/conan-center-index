from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import collect_libs, copy, get, replace_in_file
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class LibsrtpRecipe(ConanFile):
    name = "libsrtp"
    description = (
        "This package provides an implementation of the Secure Real-time Transport"
        "Protocol (SRTP), the Universal Security Transform (UST), and a supporting"
        "cryptographic kernel."
    )
    topics = ("srtp",)
    homepage = "https://github.com/cisco/libsrtp"
    url = "https://github.com/conan-io/conan-center-index"
    license = "BSD-3-Clause"
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
            self.requires("openssl/3.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_OPENSSL"] = self.options.with_openssl
        tc.variables["TEST_APPS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        replace_in_file(
            self, os.path.join(self.source_folder, "CMakeLists.txt"),
            "install(TARGETS srtp2 DESTINATION lib)",
            (
                "include(GNUInstallDirs)\n"
                "install(TARGETS srtp2\n"
                "RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}\n"
                "LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}\n"
                "ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR})"
            ),
        )
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", f"libsrtp{Version(self.version).major}")
        self.cpp_info.libs = collect_libs(self)
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
