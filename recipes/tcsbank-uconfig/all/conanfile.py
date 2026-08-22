import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.52.0"


class TCSBankUconfigConan(ConanFile):
    name = "tcsbank-uconfig"
    description = "Lightweight, header-only, C++17 configuration library"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Tinkoff/uconfig"
    topics = ("configuration", "env", "json", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_rapidjson": [True, False],
    }
    default_options = {
        "with_rapidjson": True,
    }
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "Visual Studio": "16",
            "msvc": "192",
            "gcc": "7.3",
            "clang": "6.0",
            "apple-clang": "10.0"
        }

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_rapidjson:
            self.requires("rapidjson/cci.20220822")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler))
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder)
        copy(self, "*.h",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, "*.ipp",
             dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.set_property("cmake_file_name", "uconfig")
        self.cpp_info.set_property("cmake_target_name", "uconfig::uconfig")
        self.cpp_info.set_property("pkg_config_name", "uconfig")

        if self.options.with_rapidjson:
            self.cpp_info.defines = ["RAPIDJSON_HAS_STDSTRING=1"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "uconfig"
        self.cpp_info.names["cmake_find_package_multi"] = "uconfig"
