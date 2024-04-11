from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get, copy, rename, rm, rmdir
from conan.tools.microsoft import is_msvc_static_runtime, is_msvc
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"

class PrimesieveConan(ConanFile):
    name = "primesieve"
    description = "Fast prime number generator"
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/kimwalisch/primesieve"
    topics = ("math", "prime-numbers", "sieve-of-eratosthenes")
    package_type = "library"
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
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        if self.settings.compiler == "gcc" and Version(self.settings.compiler.version) <= "5":
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support GCC<=5 currently. Contributions with fixes are welcome.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_PRIMESIEVE"] = False
        tc.variables["BUILD_DOC"] = False
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_TESTS"] = False
        tc.variables["WITH_MULTIARCH"] = self.options.with_multiarch
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
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
        if is_msvc(self) and self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "primesieve.dll.lib"), os.path.join(self.package_folder, "lib", "primesieve.lib"))

    def package_info(self):
        self.cpp_info.libs = ["primesieve"]
        self.cpp_info.set_property("cmake_file_name", "primesieve")
        self.cpp_info.set_property("cmake_target_name", "primesieve::primesieve")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
