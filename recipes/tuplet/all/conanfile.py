from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class TupletConan(ConanFile):
    name = "tuplet"
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/codeinred/tuplet"
    description = "A fast, simple tuple implementation that implements tuple as an aggregate"
    topics = ("tuple", "trivially-copyable", "modern-cpp")
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _min_cppstd(self):
        return "20"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "11",
            "Visual Studio": "17",
            "msvc": "19.22",
            "clang": "13",
            "apple-clang": "13"
        }

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        compiler = str(self.settings.compiler)
        version = str(self.settings.compiler.version)

        minimum_version = self._compilers_minimum_version.get(compiler, False)

        if not minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.name} requires C++20. Your compiler configuration ({compiler}-{version}) wasn't validated. \
                please report an issue if it does actually supports c++20.")
        elif lazy_lt_semver(version, minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.name} {self.version} requires C++20, which your compiler ({compiler}-{version}) does not support")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        include_folder = os.path.join(self.source_folder, "include")
        copy(self, "*.hpp", src=include_folder, dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "tuplet")
        self.cpp_info.set_property("cmake_target_name", "tuplet::tuplet")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
