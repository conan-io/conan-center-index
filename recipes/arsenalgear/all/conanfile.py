from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.files import get, copy, rmdir
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout

import os

required_conan_version = ">=1.53.0"

class ArsenalgearConan(ConanFile):
    name = "arsenalgear"
    description = "A library containing general purpose C++ utils."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/JustWhit3/arsenalgear-cpp"
    topics = ("constants", "math", "operators", "stream")
    package_type = "static-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
    }
    default_options = {
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "8",
            "clang": "7",
            "apple-clang": "12.0",
        }

    def export_sources(self):
        if Version(self.version) < "2.1.0":
            copy(self, "CMakeLists.txt", src=self.recipe_folder, dst=self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) < "2.0.0":
            self.requires("boost/1.81.0")
            if self.settings.os in ["Linux", "Macos"]:
                self.requires("exprtk/0.0.2")

    def validate(self):
        # arsenalgear doesn't support Visual Studio(yet).
        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Visual Studio(yet)")

        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if Version(self.version) < "2.1.0":
            tc.variables["ARSENALGEAR_VERSION"] = str(self.version)
            tc.variables["ARSENALGEAR_SRC_DIR"] = self.source_folder.replace("\\", "/")
        else:
            tc.variables["ARSENALGEAR_TESTS"] = False
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        if Version(self.version) < "2.1.0":
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
        self.cpp_info.libs = ["arsenalgear"]

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
