import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file

required_conan_version = ">=1.53.0"


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
        self.requires("boost/1.83.0", transitive_headers=True, transitive_libs=True)
        # tgbot/net/CurlHttpClient.h:#include <curl/curl.h>
        self.requires("libcurl/[>=7.78 <9]", transitive_headers=True, transitive_libs=True)
        self.requires("openssl/[>=1.1 <4]")

    @property
    def _required_boost_components(self):
        return ["system"]

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, 11)
        miss_boost_required_comp = any(
            self.dependencies["boost"].options.get_safe(f"without_{boost_comp}", True)
            for boost_comp in self._required_boost_components
        )
        if self.dependencies["boost"].options.header_only or miss_boost_required_comp:
            raise ConanInvalidConfiguration(
                f"{self.name} requires non header-only boost with these components: "
                + ", ".join(self._required_boost_components)
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENABLE_TESTS"] = False
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

    def package_info(self):
        self.cpp_info.libs = ["TgBot"]
        self.cpp_info.defines = ["HAVE_CURL=1"]
