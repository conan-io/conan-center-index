from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import get, copy, rmdir
import os

class CorogramConan(ConanFile):
    name = "corogram"
    description = "A C++20 coroutine-based Telegram Bot framework built on top of Drogon"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/corogram/corogram"
    topics = ("telegram", "bot", "coroutine", "drogon", "cpp20")
    package_type = "header-library"
    no_copy_source = True  # header-only için şart
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "with_redis": [True, False],
        "with_ed25519": [True, False],
    }
    default_options = {
        "with_redis": False,
        "with_ed25519": False,
    }

    def requirements(self):
        self.requires("drogon/1.9.1")
        self.requires("nlohmann_json/3.11.3")
        self.requires("openssl/3.2.1")
        if self.options.with_redis:
            self.requires("hiredis/1.2.0")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        tc = CMakeToolchain(self)
        tc.variables["COROGRAM_BUILD_EXAMPLES"] = False
        tc.variables["COROGRAM_HAS_HIREDIS"] = self.options.with_redis
        tc.variables["COROGRAM_ED25519"] = self.options.with_ed25519
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             self.source_folder,
             os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp",
             os.path.join(self.source_folder, "include"),
             os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.clear()  # header-only: settings farketmez

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.set_property("cmake_file_name", "corogram")
        self.cpp_info.set_property("cmake_target_name", "corogram::corogram")
        if self.settings.os == "Windows":
            self.cpp_info.defines = ["NOMINMAX", "WIN32_LEAN_AND_MEAN"]