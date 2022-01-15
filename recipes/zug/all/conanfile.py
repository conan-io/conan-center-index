import os
from pprint import pprint

from conans import ConanFile, tools


class ZugConan(ConanFile):
    name = "zug"
    version = "0.0.1"
    license = "Boost Software License 1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sinusoid.es/zug/"
    description = "Transducers for C++ — Clojure style higher order push/pull \
        sequence transformations"
    topics = ("zug",)
    settings = ("compiler",)
    no_copy_source = True

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self.source_folder
        )

    def build(self):
        pass  # header only

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_folder)
        self.copy(
            pattern="*", dst="include/zug", src=os.path.join(self.source_folder, "zug")
        )

    def package_info(self):
        if self.settings.compiler in ["Visual Studio", "msvc"]:
            self.cpp_info.cxxflags = ["/Zc:externConstexpr"]
