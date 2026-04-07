from conan import ConanFile
from conan.tools.build import check_min_cstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rmdir
import os

required_conan_version = ">=2.4"

class ZxcConan(ConanFile):
    name = "zxc"
    description = "High-performance asymmetric lossless compression library"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/hellobertrand/zxc"
    topics = ("compression", "high-performance", "lossless")
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
    languages = "C"

    def requirements(self):
        self.requires("rapidhash/[>=3.0 <4]")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.21]")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["ZXC_NATIVE_ARCH"] = False
        tc.cache_variables["ZXC_BUILD_CLI"] = False
        tc.cache_variables["ZXC_BUILD_TESTS"] = False
        tc.cache_variables["ZXC_ENABLE_LTO"] = False
        tc.cache_variables["FIND_PACKAGE_DISABLE_Doxygen"] = True
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def validate(self):
        if self.settings.get_safe("compiler.cstd"):
            check_min_cstd(self, 17)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "zxc")
        self.cpp_info.set_property("cmake_target_name", "zxc::zxc_lib")
        self.cpp_info.set_property("pkg_config_name", "zxc")
        self.cpp_info.libs = ["zxc"]
        if not self.options.shared:
            self.cpp_info.defines.append("ZXC_STATIC_DEFINE")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])