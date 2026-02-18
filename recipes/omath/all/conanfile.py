from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=2.1"


class OmathConan(ConanFile):
    name = "omath"
    description = "Cross-platform modern general purpose math library written in C++23"
    license = "Zlib"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/orange-cpp/omath"
    topics = ("math", "linear-algebra", "vector", "matrix")

    package_type = "library"
    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    implements = ["auto_shared_fpic"]


    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 23)
        if is_msvc(self) and self.options.shared:
            # https://github.com/orange-cpp/omath/pull/17
            raise ConanInvalidConfiguration("Windows shared is not supported for now.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.cache_variables["OMATH_USE_UNITY_BUILD"] = False
        tc.cache_variables["OMATH_BUILD_TESTS"] = False
        tc.cache_variables["OMATH_THREAT_WARNING_AS_ERROR"] = False
        tc.cache_variables["OMATH_BUILD_BENCHMARK"] = False
        tc.cache_variables["OMATH_BUILD_EXAMPLES"] = False
        tc.cache_variables["OMATH_BUILD_AS_SHARED_LIBRARY"] = self.options.shared
        tc.cache_variables["OMATH_BUILD_VIA_VCPKG"] = False
        tc.generate()
        
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=f"{self.package_folder}/licenses")
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "omath")
        self.cpp_info.set_property("cmake_target_name", "omath::omath")
        self.cpp_info.defines.extend(["OMATH_SUPRESS_SAFETY_CHECKS", "OMATH_ENABLE_FORCE_INLINE", "OMATH_ENABLE_LEGACY"])
        self.cpp_info.libs = ["omath"]
