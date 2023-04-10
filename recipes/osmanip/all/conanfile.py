from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.53.0"

class OsmanipConan(ConanFile):
    name = "osmanip"
    description = "Library with useful output stream tools like: color and style manipulators, progress bars and terminal graphics."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/JustWhit3/osmanip"
    topics = ("manipulator", "iostream", "output-stream", "iomanip")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    def export_sources(self):
        if Version(self.version) < "4.5.0":
            copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("boost/1.81.0")
        if Version(self.version) < "4.2.0":
            self.requires("arsenalgear/1.2.2", transitive_headers=True)
        else:
            self.requires("arsenalgear/2.0.1", transitive_headers=True)

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _compiler_required_cpp17(self):
        return {
            "Visual Studio": "16",
            "msvc": "191",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
        }

    def validate(self):
        if self.info.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        minimum_version = self._compiler_required_cpp17.get(str(self.info.settings.compiler), False)
        if minimum_version:
            if Version(self.info.settings.compiler.version) < minimum_version:
                raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._minimum_cpp_standard}, which your compiler does not support.")
        else:
            self.output.warn(f"{self.ref} requires C++{self._minimum_cpp_standard}. Your compiler is unknown. Assuming it supports C++{self._minimum_cpp_standard}")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "4.5.0":
            tc.variables["OSMANIP_VERSION"] = str(self.version)
            tc.variables["OSMANIP_SRC_DIR"] = self.source_folder.replace("\\", "/")
        else:
            tc.variables["OSMANIP_TESTS"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        if Version(self.version) < "4.5.0":
            cmake.configure(build_script_folder=os.path.join(self.source_folder, os.pardir))
        else:
            cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["osmanip"]
