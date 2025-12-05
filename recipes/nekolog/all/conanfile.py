from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout
from conan.tools.files import copy, get
import os


class NekoLogConan(ConanFile):
    name = "nekolog"
    # version is managed by config.yml in ConanCenter
    license = "MIT OR Apache-2.0"
    author = "Hoshi <moehoshio>"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/moehoshio/NekoLog"
    description = "An easy-to-use, modern, lightweight, and efficient C++20 logging library"
    topics = ("logging", "cpp20", "header-only", "async")
    
    # Header-only library
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    
    options = {
        "build_tests": [True, False],
        "use_modules": [True, False],
    }
    default_options = {
        "build_tests": False,
        "use_modules": False,
    }
    
    # Header-only library
    package_type = "header-library"
    settings = "os", "compiler", "build_type", "arch"
    
    options = {
        "build_tests": [True, False],
        "use_modules": [True, False],
    }
    default_options = {
        "build_tests": False,
        "use_modules": False,
    }
    
    def export_sources(self):
        # ConanCenter will download from conandata.yml
        pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        # Header-only library - package_id is independent of settings
        self.info.clear()

    def source(self):
        # Download sources from GitHub using conandata.yml
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        # Note: ConanCenter CI uses Ninja, but for local testing on Windows
        # you can use Visual Studio if Ninja is not available
        # Uncomment the line below for local Windows testing:
        # tc.generator = "Visual Studio 17 2022"
        # For ConanCenter submission, keep Ninja (comment out the above line)
        tc.generator = "Ninja"
        tc.variables["NEKO_LOG_BUILD_TESTS"] = False  # Don't build tests in ConanCenter
        tc.variables["NEKO_LOG_USE_MODULES"] = False  # Disable modules for compatibility
        # Enable auto-fetch to get NekoSchema via FetchContent
        tc.variables["NEKO_LOG_AUTO_FETCH_DEPS"] = True
        # Tell NekoSchema not to build tests (prevents GoogleTest installation)
        tc.variables["NEKO_SCHEMA_BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        # Header-only library, but we still need to run CMake for installation
        cmake = CMake(self)
        cmake.configure()
        # No need to build for header-only, and we don't want to build fetched dependencies

    def package(self):
        copy(self, "LICENSE", 
             src=self.source_folder, 
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "NekoLog")
        self.cpp_info.set_property("cmake_target_name", "Neko::Log")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # NekoSchema dependency is handled via FetchContent in CMakeLists.txt
        # Once NekoSchema is published to Conan, uncomment:
        # self.cpp_info.requires = ["nekoschema::nekoschema"]
