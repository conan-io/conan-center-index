from conan import ConanFile
from conan.tools.files import download, copy
import os
from conan.tools.layout import basic_layout

class GasPreprocessorConan(ConanFile):
    name = "gas-preprocessor"
    license = "NO LICENSE"
    url = "https://github.com/FFmpeg/gas-preprocessor"
    description = "Perl script that implements a subset of the GNU as preprocessor that Apple's as doesn't"
    requires = "strawberryperl/[*]"
    package_type = "application"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        download(self,
                 url="https://raw.githubusercontent.com/FFmpeg/gas-preprocessor/a120373ba30de06675d8c47617b315beef16c88e/gas-preprocessor.pl",
                 filename="gas-preprocessor.pl"
                 )

    def package(self):
        copy(self, "gas-preprocessor.pl", self.source_folder, os.path.join(self.package_folder, "bin"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["bin"]
