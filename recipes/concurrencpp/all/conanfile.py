from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class ConcurrencppConan(ConanFile):
    name = "concurrencpp"
    description = "Modern concurrency for C++. Tasks, executors, timers and C++20 coroutines to rule them all."
    homepage = "https://github.com/David-Haim/concurrencpp"
    topics = ("scheduler", "coroutines", "concurrency", "tasks", "executors", "timers", "await", "multithreading")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "clang": "11",
        }

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "20")
        if self.info.options.shared and is_msvc(self):
            # see https://github.com/David-Haim/concurrencpp/issues/75
            raise ConanInvalidConfiguration("concurrencpp does not support shared builds with Visual Studio")
        if self.info.settings.compiler == "gcc":
            raise ConanInvalidConfiguration("gcc is not supported by concurrencpp")

        minimum_version = self._minimum_compilers_version.get(
            str(self.info.settings.compiler), False
        )
        if not minimum_version:
            self.output.warn(
                "concurrencpp requires C++20. Your compiler is unknown. Assuming it supports C++20."
            )
        elif Version(self.info.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                "concurrencpp requires clang >= 11 or Visual Studio >= 16.8.2 as a compiler!"
            )
        if self.info.settings.compiler == "clang" and self.info.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration("libc++ required")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "concurrencpp")
        self.cpp_info.set_property("cmake_target_name", "concurrencpp::concurrencpp")
        self.cpp_info.libs = ["concurrencpp"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m", "pthread", "rt"]
