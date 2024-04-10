import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, save, replace_in_file
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class EnjinCppSdk(ConanFile):
    name = "enjincppsdk"
    description = "A C++ SDK for development on the Enjin blockchain platform."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/enjin/enjin-cpp-sdk"
    topics = ("enjin", "sdk", "blockchain")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_default_http_client": [True, False],
        "with_default_ws_client": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_default_http_client": False,
        "with_default_ws_client": False,
    }

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "9",
            "clang": "10",
            "apple-clang": "12",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

        if self.options.with_default_http_client:
            self.options["cpp-httplib"].with_openssl = True

        self.options["spdlog"].header_only = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_default_http_client:
            self.requires("cpp-httplib/0.14.1")

        if self.options.with_default_ws_client:
            self.requires("ixwebsocket/11.4.3")

        self.requires("rapidjson/cci.20220822")
        self.requires("spdlog/1.12.0")

    def validate(self):
        # Validations for OS
        if is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.settings.os} is not supported at this time. Contributions are welcomed.")

        # Validations for minimum required C++ standard
        compiler = self.settings.compiler
        if compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)
        minimum_version = self._minimum_compilers_version.get(str(compiler), False)
        if not minimum_version:
            self.output.warning("C++17 support is required. Your compiler is unknown. Assuming it supports C++17.")
        elif Version(compiler.version) < minimum_version:
            raise ConanInvalidConfiguration("C++17 support is required, which your compiler does not support.")

        if compiler == "clang" and compiler.libcxx != "libstdc++11":
            raise ConanInvalidConfiguration("libstdc++11 is required for clang.")

        # Validations for dependencies
        if not self.dependencies["spdlog"].options.header_only:
            raise ConanInvalidConfiguration(f"{self.name} requires spdlog:header_only=True to be enabled.")

        if self.options.with_default_http_client and not self.dependencies["cpp-httplib"].options.with_openssl:
            raise ConanInvalidConfiguration(
                f"{self.name} requires cpp-httplib:with_openssl=True when using with_default_http_client=True."
            )

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["ENJINSDK_BUILD_SHARED"] = self.options.shared
        tc.variables["ENJINSDK_BUILD_TESTS"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def _patch_sources(self):
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"), "RAPIDJSON", "RapidJSON")
        # Remove version check for RapidJSON
        save(self, os.path.join(self.source_folder, "cmake", "enjinsdk_find_rapidjson.cmake"),
             "find_package(RapidJSON REQUIRED CONFIG)")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "enjinsdk"))

    def package_info(self):
        self.cpp_info.libs = ["enjinsdk"]
        self.cpp_info.set_property("cmake_file_name", "enjinsdk")
        self.cpp_info.set_property("cmake_target_name", "enjinsdk::enjinsdk")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "enjinsdk"
        self.cpp_info.names["cmake_find_package_multi"] = "enjinsdk"
