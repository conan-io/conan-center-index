import os

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get

required_conan_version = ">=2.28"


class TgbotConan(ConanFile):
    name = "tgbot"
    description = "C++ library for the Telegram Bot API"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://reo7sp.github.io/tgbot-cpp"
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
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("boost/1.91.0", options={"header_only": True}, transitive_headers=True)
        self.requires("libcurl/[>=7.78 <9]", transitive_headers=True, transitive_libs=True)
        self.requires("nlohmann_json/3.12.0", transitive_headers=True)

    def validate(self):
        check_min_cppstd(self, 20)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        dependencies = CMakeDeps(self)
        dependencies.generate()

        toolchain = CMakeToolchain(self)
        toolchain.variables["ENABLE_TESTS"] = False
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.libs = ["TgBot"]
        self.cpp_info.set_property("cmake_file_name", "TgBot")
        self.cpp_info.set_property("cmake_target_name", "TgBot::TgBot")
        if self.options.shared:
            self.cpp_info.defines.append("TGBOT_DLL")
        if self.settings.os == "Windows":
            self.cpp_info.system_libs.append("ws2_32")
            self.cpp_info.defines.extend(["_WIN32_WINNT=0x0601", "WIN32_LEAN_AND_MEAN", "NOMINMAX"])
