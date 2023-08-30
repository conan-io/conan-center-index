import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import cmake_layout
from conan.tools.files import copy, get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.53.0"

class TreConan(ConanFile):
    name = "tre"
    description = "TRE is a lightweight, robust, and efficient POSIX-compliant regexp matching library with some exciting features such as approximate (fuzzy) matching."
    license = ""
    homepage = "https://github.com/laurikari/tre"
    url = "https://github.com/conan-io/conan-center-index"
    topics = "regex", "fuzzy matching"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")


    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows builds are not yet supported")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)


    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.generate()

    def _patch_sources(self):
        if self.settings.os == "Windows" and not is_msvc(self):
            replace_in_file(self, os.path.join(self.source_folder, "win32", "tre.def"), "tre.dll", "libtre.dll")

    def build(self):
        self._patch_sources()
        autotools = Autotools(self)
        autotools.autoreconf()
        autotools.configure()
        autotools.make()

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ["tre"]

