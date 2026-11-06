from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=1.53.0"


class DBWallerConan(ConanFile):
    name = "dbwaller"
    description = "C++20 data-plane gateway with policy-aware caching and access controls"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ericel/DBWaller"
    topics = ("cache", "gateway", "security", "data-plane")
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
        return 20

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # spdlog is a private implementation detail; pin its option for a
        # deterministic package_id and to keep the static lib self-consistent.
        self.options["spdlog"].header_only = False

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # All three are implementation-only (not exposed in DBWaller's public
        # headers), so they are private requirements.
        self.requires("spdlog/1.15.3")
        self.requires("openssl/3.5.6")
        self.requires("nlohmann_json/3.12.0")

    def validate(self):
        check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["DBWALLER_BUILD_APPS"] = False
        tc.variables["DBWALLER_BUILD_TESTS"] = False
        tc.variables["DBWALLER_BUILD_BENCHMARKS"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # Conan generates its own CMake config/targets; drop the ones the
        # project installs plus its data dir so they don't shadow them.
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["dbwaller"]
        self.cpp_info.set_property("cmake_file_name", "DBWaller")
        self.cpp_info.set_property("cmake_target_name", "DBWaller::dbwaller")
        # Private deps must still propagate as transitive link requirements for
        # static consumers.
        self.cpp_info.requires = [
            "openssl::crypto",
            "spdlog::spdlog",
            "nlohmann_json::nlohmann_json",
        ]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread", "m", "dl"]
