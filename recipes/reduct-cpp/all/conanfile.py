import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    copy,
    get,
    rmdir,
)

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
    }

    implements = ["auto_shared_fpic"]

    def requirements(self):
        self.requires("fmt/[>=11.0.2 <12]")
        self.requires("cpp-httplib/[>=0.16.0 <1]")
        self.requires("nlohmann_json/[>=3.11.3 <4]")
        self.requires("openssl/[>=3.0.13 <4]")
        self.requires("concurrentqueue/[>=1.0.4 <4]")
        if not self.options.with_chrono:
            self.requires("date/[>=3.0.1 <4]")

        def build_requirements(self):
            self.tool_requires("cmake/[>=3.23]")

    def validate(self):
        check_min_cppstd(self, 20)

        httplib = self.dependencies["cpp-httplib"]

        if not httplib.options.with_openssl:
            raise ConanInvalidConfiguration("cpp-httplib must be built with OpenSSL")

        if not httplib.options.with_zlib:
            raise ConanInvalidConfiguration("cpp-httplib must be built with zlib")

        if not self.options.with_chrono:
            date = self.dependencies["date"]
            if not date.options.header_only:
                raise ConanInvalidConfiguration("date must be built as header-only")

        if (
            self.settings.os != "Windows"
            and self.settings.get_safe("compiler") == "gcc"
        ):
            if self.settings.get_safe("compiler.version") < "14" and self.options.with_chrono:
                raise ConanInvalidConfiguration(
                    "ReductCpp with chrono requires GCC 14 or higher. "
                )
            elif (
                self.settings.get_safe("compiler.version") >= "14"
                and not self.options.with_chrono
            ):
                raise ConanInvalidConfiguration(
                    "ReductCpp requires chrono with GCC 14 or higher. "
                )

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.with_chrono:
            tc.cache_variables["REDUCT_CPP_USE_STD_CHRONO"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = ["reductcpp"]
        self.cpp_info.set_property("cmake_file_name", "ReductCpp")
        self.cpp_info.set_property("cmake_target_name", "reductcpp")
