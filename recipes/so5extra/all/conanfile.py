from conan import ConanFile
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.layout import basic_layout
from conan.tools.files import get, copy
import os

required_conan_version = ">=1.53.0"


class So5extraConan(ConanFile):
    name = "so5extra"
    license = "BSD-3-Clause"
    homepage = "https://github.com/Stiffstream/so5extra"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A collection of various SObjectizer's extensions."
    topics = ("concurrency", "actor-framework", "actors", "agents", "sobjectizer")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def _compiler_support_lut(self):
        if self.version >= Version("1.6.0"):
            # Since v1.6.0 requirements to compilers were updated:
            return {
                "gcc": "10",
                "clang": "11",
                "apple-clang": "13",
                "Visual Studio": "17",
                "msvc": "192"
            }

        return {
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191"
        }

    def requirements(self):
        if self.version >= Version("1.6.0"):
            self.requires("sobjectizer/5.8.0")
        else:
            self.requires("sobjectizer/5.7.4")

    def validate(self):
        minimal_cpp_standard = "17"
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, minimal_cpp_standard)
        minimal_version = self._compiler_support_lut()

        compiler = str(self.settings.compiler)
        if compiler not in minimal_version:
            self.output.warning(
                "%s recipe lacks information about the %s compiler standard version support" % (self.name, compiler))
            self.output.warning(
                "%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))
            return

        version = Version(self.settings.compiler.version)
        if version < minimal_version[compiler]:
            raise ConanInvalidConfiguration("%s requires a compiler that supports at least C++%s" % (self.name, minimal_cpp_standard))

    def package_id(self):
        self.info.clear()

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*.hpp", src=os.path.join(self.source_folder, "dev", "so_5_extra"), dst=os.path.join(self.package_folder, "include", "so_5_extra"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "so5extra")
        self.cpp_info.set_property("cmake_target_name", "sobjectizer::so5extra")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "so5extra"
        self.cpp_info.filenames["cmake_find_package_multi"] = "so5extra"
        self.cpp_info.names["cmake_find_package"] = "sobjectizer"
        self.cpp_info.names["cmake_find_package_multi"] = "sobjectizer"
        self.cpp_info.components["so_5_extra"].names["cmake_find_package"] = "so5extra"
        self.cpp_info.components["so_5_extra"].names["cmake_find_package_multi"] = "so5extra"
        self.cpp_info.components["so_5_extra"].set_property("cmake_target_name", "sobjectizer::so5extra")
        self.cpp_info.components["so_5_extra"].requires = ["sobjectizer::sobjectizer"]
