from conan import ConanFile
from conan.tools.files import download, copy
import os
from conan.tools.layout import basic_layout


class GasPreprocessorConan(ConanFile):
    name = "gas-preprocessor"
    license = "GPL-2.0-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("ffmpeg", "preprocessor", "assembler", "arm64")
    homepage = "https://github.com/FFmpeg/gas-preprocessor"
    description = "Perl script that implements a subset of the GNU as preprocessor that Apple's as doesn't"
    package_type = "application"

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        download(self,
                 url=self.conan_data["sources"][self.version]['url'],
                 filename="gas-preprocessor.pl", sha256=self.conan_data["sources"][self.version]["sha256"])

    def export_sources(self):
        copy(self, "gpl-2.0.txt", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def package(self):
        copy(self, "gas-preprocessor.pl", self.source_folder, os.path.join(self.package_folder, "bin"))

        # https://github.com/FFmpeg/gas-preprocessor/blob/a120373ba30de06675d8c47617b315beef16c88e/gas-preprocessor.pl#L3
        # GPL-2.0 or later is mentioned in the file itself - we keep a copy of the license file in the recipe
        copy(self, "gpl-2.0.txt", self.source_folder, os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["bin"]
