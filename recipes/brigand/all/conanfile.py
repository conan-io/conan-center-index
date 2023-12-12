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
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "with_boost": [True, False],
    }
    default_options = {
        "with_boost": True,
    }

    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_boost:
            self.requires("boost/1.79.0")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        include_path = os.path.join("include", "brigand")
        copy(self, "*.hpp", src=os.path.join(self.source_folder, include_path), dst=os.path.join(self.package_folder, include_path))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libbrigand")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.options.with_boost:
            self.cpp_info.requires = ["boost::headers"]
        else:
            self.cpp_info.defines.append("BRIGAND_NO_BOOST_SUPPORT")
