from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
)
import os


required_conan_version = ">=2.0.9"


class LibGpuCountersConan(ConanFile):
    name = "libgpucounters"
    description = "A utility that allows applications to sample performance counters from Arm® Immortalis™ and Arm Mali™ GPUs."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/ARM-software/libGPUCounters"
    topics = ("gpu", "arm", "profiling")
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

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 14)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables.update(
            {
                "HWCPIPE_PIC": self.options.get_safe("fPIC", False),
                "HWCPIPE_FRONTEND_ENABLE_TESTS": False,
                "HWCPIPE_BUILD_EXAMPLES": False,
                "HWCPIPE_WERROR": False,  # true by default in the package but could be annoying for consumers
            }
        )
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE.md",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "*.a",
            self.build_folder,
            os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        dest_include_dir = os.path.join(self.package_folder, "include")
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "backend", "device", "include"),
            dest_include_dir,
        )
        copy(
            self,
            "*.hpp",
            os.path.join(self.source_folder, "hwcpipe", "include"),
            dest_include_dir,
        )

    def package_info(self):
        self.cpp_info.libs = ["hwcpipe", "device"]
        self.cpp_info.set_property("cmake_target_name", "hwcpipe")
