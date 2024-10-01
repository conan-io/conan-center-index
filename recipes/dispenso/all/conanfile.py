from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, export_conandata_patches, apply_conandata_patches, rm, rmdir
from conan.tools.scm import Version
import os


required_conan_version = ">=1.53.0"


class DispensoPackage(ConanFile):
    name = "dispenso"
    description = "Dispenso is a library for working with sets of tasks in parallel"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebookincubator/dispenso"
    topics = ("tasks", "parallel", "threads")
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

    @property
    def _min_cppstd(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "apple-clang": "10",
            "clang": "7",
            "gcc": "7",
            "msvc": "191",
            "Visual Studio": "15",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Part of the public api in dispenso/thread_pool.h (and more), unvendorized
        self.requires("concurrentqueue/1.0.4", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["DISPENSO_SHARED_LIB"] = self.options.shared
        if self.settings.os == "Windows":
            tc.preprocessor_definitions["NOMINMAX"] = 1
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = 1
        if self.settings.get_safe("compiler.cppstd") is None:
            # TODO: Remove once Conan 1 is deprecated, this is needed so apple-clang
            # can compile, as it defaults to C++98
            tc.variables["CMAKE_CXX_STANDARD"] = self._min_cppstd
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

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.libs = ["dispenso"]

        self.cpp_info.set_property("cmake_file_name", "Dispenso")
        self.cpp_info.set_property("cmake_target_name", "Dispenso::dispenso")

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["pthread", "m"])

        if self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["synchronization", "winmm"])
            self.cpp_info.defines.append("NOMINMAX")
