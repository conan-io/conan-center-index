from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.52.0"

class ValijsonConan(ConanFile):
    name = "valijson"
    description = "Valijson is a header-only JSON Schema Validation library for C++11."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/tristanpenman/valijson"
    topics = ("json", "validator", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(
            self,
            pattern="*.hpp",
            dst=os.path.join(self.package_folder, "include"),
            src=os.path.join(self.source_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_target_name", "ValiJSON::valijson")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        # self.cpp_info.filenames["cmake_find_package"] = "valijson" # TBA: There's no installed config file
        # self.cpp_info.filenames["cmake_find_package_multi"] = "valijson" # TBA: There's no installed config file
        self.cpp_info.names["cmake_find_package"] = "ValiJSON"
        self.cpp_info.names["cmake_find_package_multi"] = "ValiJSON"
        self.cpp_info.components["libvalijson"].names["cmake_find_package"] = "valijson"
        self.cpp_info.components["libvalijson"].names["cmake_find_package_multi"] = "valijson"
        self.cpp_info.components["libvalijson"].set_property("cmake_target_name", "ValiJSON::valijson")
        self.cpp_info.components["libvalijson"].bindirs = []
        self.cpp_info.components["libvalijson"].libdirs = []
