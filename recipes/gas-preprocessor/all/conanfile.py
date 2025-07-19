from conan import ConanFile
from conan.tools.files import download, copy, get
import os
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc

class GasPreprocessorConan(ConanFile):
    name = "gas-preprocessor"
    license = "GPL-2.0-or-later"
    url = "https://github.com/FFmpeg/gas-preprocessor"
    description = "Perl script that implements a subset of the GNU as preprocessor that Apple's as doesn't"
    package_type = "application"
    no_copy_source = True

    def build_requirements(self):
        if is_msvc(self):
            self.tool_requires("strawberryperl/5.32.1.1")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        download(self,
                  url=self.conan_data["sources"][self.version]['url'],
                  filename="gas-preprocessor.pl"
                )
        download(self,
                 url="https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt",
                 filename="LICENSE.txt"
                 )

    def package(self):
        copy(self, "gas-preprocessor.pl", self.source_folder, os.path.join(self.package_folder, "bin"))
        copy(self, "LICENSE.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["bin"]
