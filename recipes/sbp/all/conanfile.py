import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy

required_conan_version = ">=1.53.0"


class SbpConan(ConanFile):
    name = "sbp"
    description = "Swift Binary Protocol client library"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/swift-nav/libsbp"
    topics = ("gnss",)
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
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def validate(self):
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                "Windows shared builds are not supported right now, "
                "see issue https://github.com/swift-nav/libsbp/issues/1062"
            )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        data = self.conan_data["sources"][self.version]
        get(self, **data["source"], strip_root=True)
        get(self, **data["cmake"], strip_root=True, destination=os.path.join("c", "cmake", "common"))

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["libsbp_ENABLE_TESTS"] = False
        tc.variables["libsbp_ENABLE_DOCS"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="c")
        cmake.build()

    def package(self):
        copy(
            self,
            pattern="LICENSE",
            dst=os.path.join(self.package_folder, "licenses"),
            src=self.source_folder,
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["sbp"]
