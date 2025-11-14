import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir

required_conan_version = ">=2"


class TgbotConan(ConanFile):
    name = "tgbot"
    description = "C++ library for Telegram bot API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://reo7sp.github.io/tgbot-cpp"
    topics = ("telegram", "telegram-api", "telegram-bot", "bot")

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
        # tgbot/Api.h:#include <boost/property_tree/ptree.hpp>
        self.requires("boost/[>=1.83.0 <1.90.0]", transitive_headers=True)
        # tgbot/net/CurlHttpClient.h:#include <curl/curl.h>
        self.requires("libcurl/[>=7.78 <9]", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTS"] = False
        if not self.settings.compiler.cppstd:
            tc.cache_variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        # Don't force PIC
        replace_in_file(
            self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "set_property(TARGET ${PROJECT_NAME} PROPERTY POSITION_INDEPENDENT_CODE ON)",
            "",
        )
        # Don't force CMAKE_CXX_STANDARD
        replace_in_file(self,
            os.path.join(self.source_folder, "CMakeLists.txt"),
            "set(CMAKE_CXX_STANDARD",
            "#")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        fix_apple_shared_install_name(self)
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["TgBot"]
        self.cpp_info.defines = ["HAVE_CURL=1"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["ws2_32"])
