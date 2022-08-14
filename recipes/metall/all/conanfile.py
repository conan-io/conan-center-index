from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.scm import Version
import os

required_conan_version = ">=1.50.0"


class MetallConan(ConanFile):
    name = "metall"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/LLNL/metall"
    description = "Meta allocator for persistent memory"
    license = "MIT", "Apache-2.0"
    topics = "cpp", "allocator", "memory-allocator", "persistent-memory", "ecp", "exascale-computing"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "8.3",
            "clang": "9",
        }

    def requirements(self):
        self.requires("boost/1.79.0")

    def package_id(self):
        self.info.header_only()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 17)

        if self.settings.os not in ["Linux", "Macos"]:
            raise ConanInvalidConfiguration(
                "Metall requires some POSIX functionalities like mmap.")

        def lazy_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(
            str(self.settings.compiler), False)
        if minimum_version and lazy_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                "{} {} requires C++17, which your compiler does not support.".format(self.name, self.version))

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE*", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "COPYRIGHT", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Metall")
        self.cpp_info.set_property("cmake_target_name", "Metall::Metall")

        self.cpp_info.names["cmake_find_package"] = "Metall"
        self.cpp_info.names["cmake_find_package_multi"] = "Metall"

        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("pthread")

        if self.settings.compiler == "gcc" or (self.settings.os == "Linux" and self.settings.compiler == "clang"):
            if Version(self.settings.compiler.version) < "9":
                self.cpp_info.system_libs += ["stdc++fs"]

        self.cpp_info.requires = ["boost::headers"]
