from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class InjaConan(ConanFile):
    name = "inja"
    license = "MIT"
    homepage = "https://github.com/pantor/inja"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Inja is a template engine for modern C++, loosely inspired by jinja for python"
    topics = ("jinja2", "string templates", "templates engine")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11 if Version(self.version) < "3.4.0" else 17

    @property
    def _compilers_minimum_version(self):
        if self._min_cppstd == 11:
            return {}
        return {
            "Visual Studio": "15",
            "msvc": "191",
            "gcc": "7",
            "clang": "7",
            "apple-clang": "10",
        }

    def requirements(self):
        self.requires("nlohmann_json/3.11.2")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
        )

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "inja")
        self.cpp_info.set_property("cmake_target_name", "pantor::inja")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.filenames["cmake_find_package"] = "inja"
        self.cpp_info.filenames["cmake_find_package_multi"] = "inja"
        self.cpp_info.names["cmake_find_package"] = "pantor"
        self.cpp_info.names["cmake_find_package_multi"] = "pantor"
        self.cpp_info.components["libinja"].names["cmake_find_package"] = "inja"
        self.cpp_info.components["libinja"].names["cmake_find_package_multi"] = "inja"
        self.cpp_info.components["libinja"].set_property("cmake_target_name", "pantor::inja")
        self.cpp_info.components["libinja"].requires = ["nlohmann_json::nlohmann_json"]
        self.cpp_info.components["libinja"].bindirs = []
        self.cpp_info.components["libinja"].frameworkdirs = []
        self.cpp_info.components["libinja"].libdirs = []
        self.cpp_info.components["libinja"].resdirs = []
