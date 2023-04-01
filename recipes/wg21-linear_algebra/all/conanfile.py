import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version

required_conan_version = ">=1.59.0"

class LAConan(ConanFile):
    name = "wg21-linear_algebra"
    homepage = "https://github.com/BobSteagall/wg21"
    description = "Production-quality reference implementation of P1385: A proposal to add linear algebra support to the C++ standard library"
    topics = ("linear-algebra", "multi-dimensional", "maths")
    license = "NCSA"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "header-library"
    no_copy_source = True

    def requirements(self):
        self.requires("mdspan/0.1.0")

    @property
    def _minimum_cpp_standard(self):
        return 20

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "8",
            "clang": "8",
            "apple-clang": "11"
        }
    
    @property
    def _full_compiler_version(self):
        compiler = self.settings.compiler
        if compiler == "msvc":
            if compiler.update:
                return int(f"{compiler.version}{compiler.update}")
            else:
                return int(f"{compiler.version}0")
        else:
            return compiler.version

    def configure(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(
            str(self.settings.compiler))
        if not min_version:
            self.output.warn(f"{self.name} recipe lacks information about the "
                             f"{self.settings.compiler} compiler support.")
        else:
            if Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration(
                    f"{self.name} requires C++{self._minimum_cpp_standard} support. "
                    f"The current compiler {self._full_compiler_version} does not support it.")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "wg21_linear_algebra")
        self.cpp_info.set_property("cmake_target_name", "wg21_linear_algebra::wg21_linear_algebra")
