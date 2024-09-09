import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"


class SrtConan(ConanFile):
    name = "srt"
    description = (
        "Secure Reliable Transport (SRT) is an open source transport technology that optimizes streaming"
        " performance across unpredictable networks, such as the Internet."
    )
    license = "MPL-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Haivision/srt"
    topics = ("ip", "transport")

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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_APPS"] = False
        tc.variables["ENABLE_LOGGING"] = False
        tc.variables["ENABLE_SHARED"] = self.options.shared
        tc.variables["ENABLE_STATIC"] = not self.options.shared
        tc.variables["ENABLE_STDCXX_SYNC"] = True
        tc.variables["ENABLE_ENCRYPTION"] = True
        tc.variables["USE_OPENSSL_PC"] = False
        if is_msvc(self):
            # required to avoid warnings when srt shared, even if openssl shared,
            # otherwise upstream CMakeLists would add /DELAYLOAD:libeay32.dll to link flags
            tc.variables["OPENSSL_USE_STATIC_LIBS"] = True
        tc.generate()

        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        'set (CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/scripts")',
                        'list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/scripts")')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "srt")
        suffix = "_static" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.libs = ["srt" + suffix]
        if self.options.shared:
            self.cpp_info.defines = ["SRT_DYNAMIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = ["ws2_32"]
