from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.50.0"

class FancyArgumentParserConan(ConanFile):
    name = "fancyargumentparser"
    description = "A fancy and easy-to-use command-line argument parser for C++."
    license = "MIT"
    url = "https://github.com"
    homepage = "https://github.com/simfeo/FancyArgumentParser"
    topics = ("command-line", "parser", "arguments", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "argparse.h", src=self.source_folder, dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        # Сообщаем системе сборки, как называется компонент
        self.cpp_info.components["fancyargumentparser_lib"].libs = []
