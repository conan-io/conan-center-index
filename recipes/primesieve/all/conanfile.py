from conan import ConanFile
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.files import get, copy, rm, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
import os


required_conan_version = ">=1.53.0"

class PackageConan(ConanFile):
    name = "primesieve"
    description = "Fast prime number generator"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kimwalisch/primesieve"
    topics = ("math", "prime-numbers", "sieve-of-eratosthenes")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_multiarch": [True, False],
        "with_msvc_crt_static": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_multiarch": True,
        "with_msvc_crt_static": False,
    }

    @property
    def _min_cppstd(self):
        return 11

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_PRIMESIEVE"] = False
        tc.variables["BUILD_DOC"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["WITH_MULTIARCH"] = self.options.with_multiarch
        if is_msvc(self):
            tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0091"] = "NEW"
            tc.variables["WITH_MSVC_CRT_STATIC"] = self.options.with_msvc_crt_static
            tc.variables["USE_MSVC_RUNTIME_LIBRARY_DLL"] = not is_msvc_static_runtime(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["primesieve"]
        self.cpp_info.set_property("cmake_file_name", "primesieve")
        self.cpp_info.set_property("cmake_target_name", "primesieve::primesieve")
        self.cpp_info.filenames["cmake_find_package"] = "primesieve"
        self.cpp_info.filenames["cmake_find_package_multi"] = "primesieve"
        self.cpp_info.names["cmake_find_package"] = "primesieve"
        self.cpp_info.names["cmake_find_package_multi"] = "primesieve"
