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
        self.requires("mdspan/0.5.0")

    @property
    def _minimum_cpp_standard(self):
        return 20

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "10",
            "clang": "12", # Should be 11 but https://github.com/conan-io/conan-docker-tools/issues/251
            "apple-clang": "11"
        }

    def validate(self):
        compiler = self.settings.compiler
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(compiler))
        if min_version and Version(self.settings.compiler.version) < min_version:
            raise ConanInvalidConfiguration(f"{self.ref} requires at least {compiler} {min_version}")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "include"), os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "wg21_linear_algebra")
        self.cpp_info.set_property("cmake_target_name", "wg21_linear_algebra::wg21_linear_algebra")

        self.cpp_info.names["cmake_find_package"] = "wg21_linear_algebra"
        self.cpp_info.names["cmake_find_package_multi"] = "wg21_linear_algebra"
