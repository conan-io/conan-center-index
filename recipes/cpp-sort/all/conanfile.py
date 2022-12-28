import os.path

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.50.0"


class CppSortConan(ConanFile):
    name = "cpp-sort"
    description = "Additional sorting algorithms & related tools"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Morwenn/cpp-sort"
    topics = "cpp-sort", "sorting", "algorithms"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "apple-clang": "9.4",
            "clang": "3.8",
            "gcc": "5.5"
        }

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)

        if is_msvc(self) and Version(self.version) < "1.10.0":
            raise ConanInvalidConfiguration(f"{self.ref} versions older than 1.10.0 do not support MSVC")

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)
        try:
            minimum_version = self._compilers_minimum_version[str(compiler)]
            if minimum_version and loose_lt_semver(version, minimum_version):
                msg = (
                    f"{self.ref} requires C++{self._minimum_cpp_standard} features "
                    f"which are not supported by compiler {compiler} {version}."
                )
                raise ConanInvalidConfiguration(msg)
        except KeyError:
            msg = (
                f"{self.ref} recipe lacks information about the {compiler} compiler, "
                f"support for the required C++{self._minimum_cpp_standard} features is assumed"
            )
            self.output.warn(msg)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = "OFF"
        tc.generate()

    def package(self):
        # Install with CMake
        cmake = CMake(self)
        cmake.configure()
        cmake.install()

        # Copy license files
        if Version(self.version) < "1.8.0":
            license_files = ["license.txt"]
        else:
            license_files = ["LICENSE.txt", "NOTICE.txt"]
        for license_file in license_files:
            copy(self, license_file, src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

        # Remove CMake config files (only files in lib)
        rmdir(self, os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "cpp-sort")
        self.cpp_info.set_property("cmake_target_name", "cpp-sort::cpp-sort")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if is_msvc(self):
            self.cpp_info.cxxflags = ["/permissive-"]
