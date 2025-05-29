from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=2.0"


class ReactivePlusPlusConan(ConanFile):
    name = "reactiveplusplus"
    description = (
        "ReactivePlusPlus is library for building asynchronous event-driven "
        "streams of data with help of sequences of primitive operators in the "
        "declarative form."
    )
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/victimsnino/ReactivePlusPlus"
    topics = ("reactivex", "asynchronous", "event", "observable", "values-distributed-in-time")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

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
        required_cppstd = "20"
        check_min_cppstd(self, required_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++{required_cppstd}, which your compiler does not support.",
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
        # Copy extensions (available since v2.2.0)
        for extension in ["rppasio", "rppgrpc", "rppqt"]:
            copy(self, "*",
                       src=os.path.join(self.source_folder, "src", "extensions", extension, extension),
                       dst=os.path.join(self.package_folder, "include", extension))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "RPP")
        self.cpp_info.set_property("cmake_target_name", "RPP::rpp")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []

        self.cpp_info.components["_reactiveplusplus"].set_property("cmake_target_name", "RPP::rpp")
        self.cpp_info.components["_reactiveplusplus"].bindirs = []
        self.cpp_info.components["_reactiveplusplus"].libdirs = []
