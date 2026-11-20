import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rm, rmdir

required_conan_version = ">=2.0.9"


class CountlySdkCppConan(ConanFile):
    name = "countly-sdk-cpp"
    description = "Countly analytics SDK for C++ applications"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Countly/countly-sdk-cpp"
    topics = ("analytics", "telemetry", "crash-reporting", "countly")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_sqlite": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_sqlite": False,
    }
    implements = ["auto_shared_fpic"]

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("nlohmann_json/3.12.0", transitive_headers=True)
        self.requires("openssl/[>=1.1 <4]")
        if self.settings.os != "Windows":
            self.requires("libcurl/[>=7.78 <9]")
        if self.options.with_sqlite:
            self.requires("sqlite3/3.54.0")

    def validate(self):
        check_min_cppstd(self, 14)
        if self.settings.os == "WindowsStore":
            raise ConanInvalidConfiguration(f"{self.ref} uses WinHTTP, which UWP apps cannot use")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["COUNTLY_USE_SYSTEM_JSON"] = True
        tc.cache_variables["COUNTLY_USE_SQLITE"] = bool(self.options.with_sqlite)
        tc.cache_variables["COUNTLY_USE_SYSTEM_SQLITE"] = bool(self.options.with_sqlite)
        tc.cache_variables["COUNTLY_BUILD_TESTS"] = False
        tc.cache_variables["COUNTLY_BUILD_SAMPLE"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["countly"]
        self.cpp_info.set_property("cmake_file_name", "countly")
        self.cpp_info.set_property("cmake_target_name", "countly::countly")
        if self.options.with_sqlite:
            self.cpp_info.defines.append("COUNTLY_USE_SQLITE")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.append("winhttp")
