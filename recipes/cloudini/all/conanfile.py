import os

from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0.9"


class CloudiniConan(ConanFile):
    name = "cloudini"
    description = "Point cloud compression library for ROS, MCAP and Foxglove"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facontidavide/cloudini"
    topics = ("point-cloud", "compression", "ros", "ros2", "mcap", "lidar")
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
    implements = ["auto_shared_fpic"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.shared
            self.package_type = "static-library"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("lz4/[>=1.9.4 <2]")
        self.requires("zstd/[>=1.5 <1.6]")

    def validate(self):
        check_min_cppstd(self, 20)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.16]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["CLOUDINI_FORCE_VENDORED_DEPS"] = False
        tc.cache_variables["CLOUDINI_BUILD_TOOLS"] = False
        tc.cache_variables["CLOUDINI_BUILD_BENCHMARKS"] = False
        tc.cache_variables["BUILD_TESTING"] = False
        tc.generate()
        deps = CMakeDeps(self)
        # Upstream's CMakeLists references LZ4::lz4_static and zstd::libzstd_static
        # explicitly. CCI's lz4/zstd recipes export these names when their `shared`
        # option is False (matching our default). The set_property overrides keep
        # this working even if a consumer forces lz4/zstd to shared via `-o *:shared=True`.
        deps.set_property("lz4", "cmake_target_name", "LZ4::lz4_static")
        deps.set_property("zstd", "cmake_target_name", "zstd::libzstd_static")
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "cloudini_lib"))
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        CMake(self).install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cloudini")
        self.cpp_info.set_property("cmake_target_name", "cloudini::cloudini")
        self.cpp_info.libs = ["cloudini_lib"]
        self.cpp_info.includedirs = ["include"]
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["m", "pthread"])
