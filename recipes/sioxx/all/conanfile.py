import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir


required_conan_version = ">=2.28"


class SioxxConan(ConanFile):
    name = "sioxx"
    description = "A modern C++17 Socket.IO client built on Boost.Beast"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/jfayot/sioxx"
    topics = ("socket.io", "websocket", "boost-beast", "networking")
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "boost/*:header_only": True,
    }

    implements = ["auto_shared_fpic"]

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost/1.90.0", visible=False)
        self.requires("nlohmann_json/3.12.0", transitive_headers=True)
        self.requires(
            "openssl/3.6.3",
            transitive_headers=False,
            transitive_libs=not self.options.shared,
            visible=not self.options.shared,
        )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.28]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.cache_variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.cache_variables["SIOXX_BUILD_DOCS"] = False
        tc.cache_variables["SIOXX_BUILD_EXAMPLES"] = False
        tc.cache_variables["SIOXX_BUILD_TESTS"] = False
        tc.cache_variables["SIOXX_INSTALL"] = True
        tc.cache_variables["SIOXX_USE_SYSTEM_BOOST"] = True
        tc.cache_variables["SIOXX_USE_SYSTEM_JSON"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["sioxx"]
        self.cpp_info.set_property("cmake_file_name", "sioxx")
        self.cpp_info.set_property("cmake_target_name", "sioxx::sioxx")
        self.cpp_info.set_property("pkg_config_name", "sioxx")
        self.cpp_info.requires = ["nlohmann_json::nlohmann_json"]

        if not self.options.shared:
            self.cpp_info.requires.extend(["openssl::ssl", "openssl::crypto"])
            if self.settings.os == "Windows":
                self.cpp_info.system_libs.extend(["ws2_32", "mswsock"])
            elif self.settings.os in ("Linux", "FreeBSD"):
                self.cpp_info.system_libs.append("pthread")
