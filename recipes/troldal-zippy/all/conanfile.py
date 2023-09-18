import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class TroldalZippyConan(ConanFile):
    name = "troldal-zippy"
    description = 'A simple C++ wrapper around the "miniz" zip library '
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/troldal/Zippy"
    topics = ("wrapper", "compression", "zip", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("miniz/3.0.2")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._minimum_cpp_standard)
        if is_msvc(self):
            check_min_vs(self, "192")
        else:
            min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
            if not min_version:
                self.output.warning(f"{self.name} recipe lacks information about the {self.settings.compiler} compiler support.")
            else:
                if Version(self.settings.compiler.version) < min_version:
                    raise ConanInvalidConfiguration(
                        f"{self.name} requires C++{self._minimum_cpp_standard} support. The current compiler"
                        f" {self.settings.compiler} {self.settings.compiler.version} does not support it."
                    )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        apply_conandata_patches(self)
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*.hpp",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "library"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # To match the target created here
        # https://github.com/troldal/Zippy/blob/a838de8522f9051df0d1b202473bb69befe648702/library/CMakeLists.txt#L10
        self.cpp_info.set_property("cmake_file_name", "Zippy")
        self.cpp_info.set_property("cmake_target_name", "Zippy::Zippy")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Zippy"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Zippy"
        self.cpp_info.names["cmake_find_package"] = "Zippy"
        self.cpp_info.names["cmake_find_package_multi"] = "Zippy"
