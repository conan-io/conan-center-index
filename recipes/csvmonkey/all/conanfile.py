from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc
import os

required_conan_version = ">=1.52.0"

class CSVMONEKYConan(ConanFile):
    name = "csvmonkey"
    description = "Header-only vectorized, lazy-decoding, zero-copy CSV file parser"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/dw/csvmonkey/"
    topics = ("csv-parser", "header-only", "vectorized")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_spirit": [True, False],
    }
    default_options = {
        "with_spirit": False,
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_spirit:
            self.requires("boost/1.81.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        if self.settings.arch not in ("x86", "x86_64",):
            raise ConanInvalidConfiguration(f"{self.ref} requires x86 architecture.")

        if is_msvc(self):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support Visual Studio C++.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "csvmonkey")
        self.cpp_info.set_property("cmake_target_name", "csvmonkey::csvmonkey")
        self.cpp_info.set_property("pkg_config_name", "csvmonkey")

        if self.options.with_spirit:
            self.cpp_info.defines.append("USE_SPIRIT")

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "csvmonkey"
        self.cpp_info.filenames["cmake_find_package_multi"] = "csvmonkey"
        self.cpp_info.names["cmake_find_package"] = "csvmonkey"
        self.cpp_info.names["cmake_find_package_multi"] = "csvmonkey"
