import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout, CMake

required_conan_version = ">=2.0"


class TgBotStaterConan(ConanFile):
    name = "tgbotstater"
    description = "A C++ library for constructing Telegram bots in compile-time!"
    license = "MIT"

    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Makcal/TgBotStater"
    topics = ("telegram", "telegram-bot", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "include/*", "CMakeLists.txt"
    no_copy_source = True
    generators = "CMakeToolchain", "CMakeDeps"

    def requirements(self):
        self.requires("tgbot/1.8")
        self.requires("brigand/cpp11-1.3.0", options={"with_boost": False})
        compiler = self.settings.compiler
        if compiler == "gcc" and float(compiler.version.value) >= 13 or \
            compiler == "clang" and float(compiler.version.value) >= 17 or \
            compiler == "apple-clang" and float(compiler.version.value) >= 193 or \
            compiler == "msvc" and float(compiler.version.value) >= 15:
            pass
        else:
            self.requires("fmt/11.1.4", options={"header_only": True})

    def validate(self):
        check_min_cppstd(self, 20)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self, src_folder='.')

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["TgBotStater"]
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

    def package_id(self):
        self.info.clear()
