from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMake, cmake_layout, CMakeDeps
from conan.tools.files import copy, get
from conan.tools.scm import Version
from conan.tools.build import check_min_cppstd
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.0"


class HakkaJsonConan(ConanFile):
    name = "hakka_json"
    license = "BSL-1.0 OR BSD-3-Clause"
    homepage = "https://github.com/cycraft-corp/hakka_json"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Memory-efficient JSON library with C++23 core and C API - Optimized for minimal runtime footprint"
    topics = ("json", "parser", "cpp23", "memory-efficiency", "embedded", "low-memory")

    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
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

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "23")

        minimum_versions = {
            "gcc": "11",
            "clang": "15",
            "apple-clang": "14",
            "msvc": "193"
        }

        minimum_version = minimum_versions.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++23, which your {self.settings.compiler} {self.settings.compiler.version} does not support"
            )

    def requirements(self):
        self.requires("nlohmann_json/3.12.0", transitive_headers=True)
        self.requires("tl-expected/1.1.0", transitive_headers=True)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HAKKA_JSON_BUILD_TESTS"] = False
        tc.variables["HAKKA_JSON_ENABLE_TBB"] = False
        tc.variables["HAKKA_JSON_USE_SYSTEM_DEPS"] = True
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["ICU_VERSION"] = "77.1"  # Specify ICU version to avoid GitHub API rate limits
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        cmake = CMake(self)
        cmake.install()

        icu_lib_dir = os.path.join(self.build_folder, "icu-install", "lib")
        if os.path.exists(icu_lib_dir):
            copy(self, "*.a", src=icu_lib_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)
            copy(self, "*.lib", src=icu_lib_dir, dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "HakkaJson")
        self.cpp_info.set_property("cmake_target_name", "HakkaJson::core")

        # CRITICAL: Main library needs ICU libraries statically linked
        if self.settings.os == "Windows":
            self.cpp_info.libs = ["hakka_json_core", "icutu", "icuin", "icuio", "icuuc", "icudt"]
        else:
            self.cpp_info.libs = ["hakka_json_core", "icutu", "icui18n", "icuio", "icuuc", "icudata"]

        self.cpp_info.requires = ["nlohmann_json::nlohmann_json", "tl-expected::tl-expected"]

        if self.settings.compiler in ["gcc", "clang", "apple-clang"] and self.settings.arch in ["x86", "armv7", "armv7hf"]:
            self.cpp_info.system_libs.append("atomic")

