import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class StructoptConan(ConanFile):
    name = "structopt"
    description = "Parse command line arguments by defining a struct+"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/p-ranav/structopt"
    topics = ("argument-parser", "cpp17", "header-only", "single-header-lib", "command-line",
              "arguments", "mit-license", "modern-cpp", "lightweight", "reflection",
              "cross-platform", "type-safety", "type-safe", "argparse", "clap")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "9",
            "Visual Studio": "15.0",
            "clang": "5",
            "apple-clang": "10",
            "msvc": "191",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("magic_enum/0.9.2")
        self.requires("visit_struct/1.1.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version:
            if Version(self.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(
                    f"structopt: Unsupported compiler: {self.settings.compiler}-{self.settings.compiler.version} "
                    f"(https://github.com/p-ranav/structopt#compiler-compatibility)."
                )
        else:
            self.output.warning("{} requires C++14. Your compiler is unknown. Assuming it supports C++14.".format(self.name))

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        rmdir(self, os.path.join(self.source_folder, "include", "structopt", "third_party"))

    def package(self):
        copy(self, pattern="LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.configure()
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
