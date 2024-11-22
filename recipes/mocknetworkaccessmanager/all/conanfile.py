from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
import os


required_conan_version = ">=1.52.0"


class MockNetworkAccessManagerConan(ConanFile):
    name = "mocknetworkaccessmanager"
    description = "Mocking network communication for Qt applications"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.com/julrich/MockNetworkAccessManager"
    topics = ("qt", "mock", "network", "QNetworkAccessManager", "unit test", "test")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "with_qt": [5, 6],
    }
    default_options = {
        "fPIC": True,
        "with_qt": 5,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_qt == 5:
            self.requires("qt/[~5.15]", transitive_headers=True)
        else:
            self.requires("qt/[>=6.6 <7]", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, "11")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.variables["FORCE_QT5"] = self.options.with_qt == 5
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["MockNetworkAccessManager"]
