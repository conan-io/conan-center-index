from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"


class BrigandConan(ConanFile):
    name = "brigand"
    url = "https://github.com/conan-io/conan-center-index"
    description = "A light-weight, fully functional, instant-compile time meta-programming library."
    topics = ("meta-programming", "boost", "runtime", "header-only")
    homepage = "https://github.com/edouarda/brigand"
    license = "BSL-1.0"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_sources = True

    def requirements(self):
        self.requires("boost/1.79.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        include_path = os.path.join("include", "brigand")
        copy(self, "*.hpp", src=os.path.join(self.source_folder, include_path), dst=os.path.join(self.package_folder, include_path))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libbrigand")
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.requires = ["boost::headers"]
