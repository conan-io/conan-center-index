import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
from conan.tools.scm import Version

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

    @property
    def _min_cppstd(self):
        # tgbot requiroes C++17 since 1.7.3
        return "14" if Version(self.version) < "1.7.3" else "17"

    @property
    def _compilers_minimum_version(self):
        return {
            "17": {
                # tgbot/>= 1.7.3 require C++17 filesystem
                "gcc": "9",
                "clang": "9",
                "apple-clang": "13",
                "Visual Studio": "16",
                "msvc": "192",
            },
            "14": {
                "gcc": "5",
                "clang": "3",
                "apple-clang": "10",
                "Visual Studio": "15",
                "msvc": "191",
            }
        }.get(self._min_cppstd, {})


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
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

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
