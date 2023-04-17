from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy
from conan.tools.build import check_min_cppstd
import os


required_conan_version = ">=1.50.0"


class Rangev3Conan(ConanFile):
    name = "range-v3"
    license = "BSL-1.0"
    homepage = "https://github.com/ericniebler/range-v3"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Experimental range library for C++11/14/17"
    topics = ("range", "range-library", "proposal", "iterator", "header-only")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5" if Version(self.version) < "0.10.0" else "6.5",
            "msvc": "192",
            "Visual Studio": "16", # TODO: remove when only Conan2 is supported
            "clang": "3.6" if Version(self.version) < "0.10.0" else "3.9"
        }

    @property
    def _min_cppstd(self):
        if is_msvc(self):
            return "17"
        else:
            return "14"
    
    def layout(self):
        basic_layout(self)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if not minimum_version:
            self.output.warning(
                f"{self.settings.compiler} {self.settings.compiler.version} support for range-v3 is unknown, assuming it is supported.")
        elif Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"range-v3 {self.version} requires C++{self._min_cppstd} with {self.settings.compiler}, which is not supported by {self.settings.compiler} {self.settings.compiler.version}")


    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def package(self):
        copy(self, "*", dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, "LICENSE.txt", dst=os.path.join(
            self.package_folder, "licenses"), src=self.source_folder)

    def package_info(self):
        self.cpp_info.components["range-v3-meta"].names["cmake_find_package"] = "meta"
        self.cpp_info.components["range-v3-meta"].names["cmake_find_package_multi"] = "meta"
        if is_msvc(self):
            self.cpp_info.components["range-v3-meta"].cxxflags = ["/permissive-"]

            if "0.9.0" <= Version(self.version) < "0.11.0":
                self.cpp_info.components["range-v3-meta"].cxxflags.append(
                    "/experimental:preprocessor")
        self.cpp_info.components["range-v3-concepts"].names["cmake_find_package"] = "concepts"
        self.cpp_info.components["range-v3-concepts"].names["cmake_find_package_multi"] = "concepts"
        self.cpp_info.components["range-v3-concepts"].requires = ["range-v3-meta"]
