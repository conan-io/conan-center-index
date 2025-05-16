from os.path import join

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy
from conan.tools.files import get

required_conan_version = ">=2"


class ReductCppConan(ConanFile):
    name = "reduct-cpp"
    description = "Reduct Storage Client SDK for C++"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.reduct.store/docs/getting-started/with-cpp"
    topics = ("reduct-storage", "http-client", "http-api")
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_chrono": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_chrono": False,
        "cpp-httplib/*:with_openssl": True,
        "cpp-httplib/*:with_zlib": True,
        "date/*:header_only": True,
    }

    def config_options(self):
        if self.settings.get_safe("os") == "Windows":
            self.options.rm_safe("fPIC")
            self.options.with_chrono = True
        elif (
                self.settings.get_safe("compiler") == "gcc"
                and self.settings.get_safe("compiler.version") >= "14"
        ):
            self.options.with_chrono = True

    def requirements(self):
        self.requires("fmt/11.0.2")
        self.requires("cpp-httplib/0.16.0")
        self.requires("nlohmann_json/3.11.3")
        self.requires("openssl/3.2.2")
        self.requires("concurrentqueue/1.0.4")
        if not self.options.with_chrono:
            self.requires("date/3.0.1")

    def validate(self):
        check_min_cppstd(self, 20)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.with_chrono:
            tc.variables["REDUCT_CPP_USE_STD_CHRONO"] = "ON"
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["reductcpp"]
