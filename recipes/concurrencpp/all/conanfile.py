from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.53.0"


class ConcurrencppConan(ConanFile):
    name = "concurrencpp"
    description = "Modern concurrency for C++. Tasks, executors, timers and C++20 coroutines to rule them all."
    homepage = "https://github.com/David-Haim/concurrencpp"
    topics = ("scheduler", "coroutines", "concurrency", "tasks", "executors", "timers", "await", "multithreading")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
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
        return "20"

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "clang": "11",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        if Version(self.version) <= "0.1.5" and self.options.shared and is_msvc(self):
            # see https://github.com/David-Haim/concurrencpp/issues/75
            raise ConanInvalidConfiguration(f"{self.ref} does not support shared builds with Visual Studio")
        if self.settings.compiler == "gcc":
            raise ConanInvalidConfiguration("gcc is not supported by concurrencpp")
        if Version(self.version) >= "0.1.5" and self.settings.compiler == "apple-clang":
            # apple-clang does not seem to support the C++20 synchronization library which concurrencpp 0.1.5 depends on
            raise ConanInvalidConfiguration("apple-clang is not supported by concurrencpp 0.1.5 and higher")

        minimum_version = self._minimum_compilers_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )
        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration("libc++ required")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
