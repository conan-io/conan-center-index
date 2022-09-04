from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class BeautyConan(ConanFile):
    name = "beauty"
    homepage = "https://github.com/dfleury2/beauty"
    description = "HTTP Server above Boost.Beast"
    topics = ("http", "server", "boost.beast")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    generators = "CMakeDeps"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8",
            "clang": "11",
            "Visual Studio": "16",
            "msvc": "192",
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

    def requirements(self):
        self.requires("boost/1.79.0"),
        self.requires("openssl/1.1.1q")

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, "20")

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"Compiler {self.name} must be at least {minimum_version}")

        if self.settings.compiler == "clang" and self.settings.compiler.libcxx != "libc++":
            raise ConanInvalidConfiguration("Only libc++ is supported for clang")

        if self.settings.compiler == "apple-clang" and self.options.shared:
            raise ConanInvalidConfiguration("shared is not supported on apple-clang")

        if is_msvc(self) and self.options.shared:
            raise ConanInvalidConfiguration("shared is not supported on Visual Studio")

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
        cmake.build(target="beauty")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "beauty")
        self.cpp_info.set_property("cmake_target_name", "beauty::beauty")
        self.cpp_info.libs = ["beauty"]
        self.cpp_info.requires = ["boost::headers", "openssl::openssl"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
