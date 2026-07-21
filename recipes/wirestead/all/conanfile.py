from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.scm import Version
import os

required_conan_version = ">=2.9"


class WiresteadConan(ConanFile):
    name = "wirestead"
    description = "Unified, cross-platform async C++ library for Serial, TCP, UDP, and UDS communication"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/wirestead/wirestead"
    topics = ("async", "communication", "tcp", "udp", "serial", "uds", "networking", "cpp20")
    settings = "os", "arch", "compiler", "build_type"
    package_type = "library"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_config": [True, False],
        "enable_memory_tracking": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_config": True,
        "enable_memory_tracking": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def requirements(self):
        self.requires("boost/[>=1.83.0]", transitive_headers=True, transitive_libs=True)
        self.requires("spdlog/[>=1.9 <2]", transitive_headers=True, transitive_libs=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["WIRESTEAD_BUILD_SHARED"] = self.options.shared
        tc.cache_variables["WIRESTEAD_BUILD_STATIC"] = not self.options.shared
        tc.cache_variables["WIRESTEAD_ENABLE_INSTALL"] = True
        tc.cache_variables["WIRESTEAD_BUILD_TESTS"] = False
        tc.cache_variables["WIRESTEAD_BUILD_DOCS"] = False
        tc.cache_variables["WIRESTEAD_ENABLE_PKGCONFIG"] = False
        tc.cache_variables["WIRESTEAD_ENABLE_CONFIG"] = self.options.enable_config
        tc.cache_variables["WIRESTEAD_ENABLE_MEMORY_TRACKING"] = self.options.enable_memory_tracking
        tc.generate()

        deps = CMakeDeps(self)
        if Version(self.dependencies["boost"].ref.version) >= "1.89.0":
            deps.set_property("boost::headers", "cmake_target_aliases", ["Boost::system"])
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        copy(
            self,
            "LICENSE*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "NOTICE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "wirestead::wirestead")
        self.cpp_info.set_property("cmake_file_name", "wirestead")
        self.cpp_info.set_property("pkg_config_name", "wirestead")
        self.cpp_info.libs = ["wirestead"]

        if self.options.enable_config:
            self.cpp_info.defines.append("WIRESTEAD_ENABLE_CONFIG=1")
        if self.options.enable_memory_tracking:
            self.cpp_info.defines.append("WIRESTEAD_ENABLE_MEMORY_TRACKING=1")

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32", "mswsock", "iphlpapi"])
            self.cpp_info.defines.extend(["WIN32_LEAN_AND_MEAN", "NOMINMAX"])
        else:
            self.cpp_info.system_libs.append("pthread")
            if self.settings.os == "Macos":
                self.cpp_info.defines.append("_DARWIN_C_SOURCE")
            else:
                self.cpp_info.defines.append("_POSIX_C_SOURCE=200809L")

        requires = ["boost::headers", "spdlog::spdlog"]
        if Version(self.dependencies["boost"].ref.version) < "1.89.0":
            # boost::system is a separate component pre-1.89; from 1.89 it no
            # longer exists and boost::headers (aliased in generate()) covers it.
            requires.append("boost::system")
        self.cpp_info.requires = requires
