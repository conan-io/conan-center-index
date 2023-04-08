from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os


required_conan_version = ">=1.52.0"


class WilConan(ConanFile):
    name = "wil"
    description = (
        "The Windows Implementation Libraries (WIL) is a header-only C++ library"
        "created to make life easier for developers on Windows through readable"
        "type-safe C++ interfaces for common Windows coding patterns."
    )
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/microsoft/wil"
    topics = ("win", "wil", "header-only")
    package_type = "header-library"
    # only arch is aplicable, windows library
    settings = "os", "arch", "compiler", "build_type" 
    
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "15",
            "msvc": "14.1",
            "gcc": "5",
            "clang": "5",
            "apple-clang": "5.1",
        }

    # About compiler version: https://github.com/microsoft/wil/issues/207#issuecomment-991722592 
    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    # same package ID for any package
    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            # Validate the minimum cpp standard supported when installing the package. For C++ projects only
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration(f"{self.ref} can be used only on Windows.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.h",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        # Folders not used for header-only
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # https://github.com/microsoft/wil/blob/56e3e5aa79234f8de3ceeeaf05b715b823bc2cca/CMakeLists.txt#L53
        self.cpp_info.set_property("cmake_file_name", "WIL")
        self.cpp_info.set_property("cmake_target_name", "WIL::WIL")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "WIL"
        self.cpp_info.filenames["cmake_find_package_multi"] = "WIL"
        self.cpp_info.names["cmake_find_package"] = "WIL"
        self.cpp_info.names["cmake_find_package_multi"] = "WIL"
