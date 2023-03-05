import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import cmake_layout
from conan.tools.files import copy, get
from conan.tools.scm import Version

required_conan_version = ">=2.0.0"

class MDSpanConan(ConanFile):
    name = "mdspan"
    homepage = "https://github.com/kokkos/mdspan"
    description = "Production-quality reference implementation of mdspan"
    topics = ("multi-dimensional", "array", "span")
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    package_type = "header-library"
    no_copy_source = True
    generators = "CMakeToolchain", "CMakeDeps"


    @property
    def _minimum_cpp_standard(self):
        return 14

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "15",
            "gcc": "5",
            "clang": "3.4",
            "apple-clang": "5.1"
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

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "mdspan")
        self.cpp_info.set_property("cmake_target_name", "std::mdspan")