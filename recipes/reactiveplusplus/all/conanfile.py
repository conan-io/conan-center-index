from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class ReactivePlusPlusConan(ConanFile):
    name = "reactiveplusplus"
    description = (
        "ReactivePlusPlus is library for building asynchronous event-driven "
        "streams of data with help of sequences of primitive operators in the "
        "declarative form."
    )
    license = "BSL-1.0"
    topics = ("reactivex", "asynchronous", "event", "observable", "values-distributed-in-time")
    homepage = "https://github.com/victimsnino/ReactivePlusPlus"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        if Version(self.version) >= "2.0.0":
            # For 'consteval' support
            return {
                "Visual Studio": "17",
                "msvc": "193",
                "gcc": "12",
                "clang": "14",
                "apple-clang": "14",
            }
        else:
            return {
                "Visual Studio": "16.10",
                "msvc": "192",
                "gcc": "10",
                "clang": "12",
                "apple-clang": "14",
            }

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            return all(int(p1) < int(p2) for p1, p2 in zip(str(v1).split("."), str(v2).split(".")))

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*",
                   src=os.path.join(self.source_folder, "src", "rpp", "rpp"),
                   dst=os.path.join(self.package_folder, "include", "rpp"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "RPP")
        self.cpp_info.set_property("cmake_target_name", "RPP::rpp")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        # TODO: to remove in conan v2 once legacy generators removed
        self.cpp_info.names["cmake_find_package"] = "RPP"
        self.cpp_info.names["cmake_find_package_multi"] = "RPP"
        self.cpp_info.components["_reactiveplusplus"].names["cmake_find_package"] = "rpp"
        self.cpp_info.components["_reactiveplusplus"].names["cmake_find_package_multi"] = "rpp"
        self.cpp_info.components["_reactiveplusplus"].set_property("cmake_target_name", "RPP::rpp")
        self.cpp_info.components["_reactiveplusplus"].bindirs = []
        self.cpp_info.components["_reactiveplusplus"].libdirs = []
