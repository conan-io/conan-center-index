import os

from conan import ConanFile
from conan.tools.files import copy, download
from conan.tools.layout import basic_layout

required_conan_version = ">=1.47.0"


class Djinni(ConanFile):
    name = "djinni-generator"
    description = "Djinni is a tool for generating cross-language type declarations and interface bindings."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://djinni.xlcpp.dev"
    topics = ("java", "Objective-C", "ios", "Android")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        filename = os.path.basename(self.conan_data["sources"][self.version]["url"])
        download(self, filename=filename, **self.conan_data["sources"][self.version])
        download(self, filename="LICENSE", url="https://raw.githubusercontent.com/cross-language-cpp/djinni-generator/main/LICENSE")

    def build(self):
        pass # avoid warning for missing build steps

    def package(self):
        copy(self, "LICENSE",
             dst=os.path.join(self.package_folder, "licenses"),
             src=self.source_folder,
             keep_path=False)
        copy(self, "djinni",
             dst=os.path.join(self.package_folder, "bin"),
             src=self.source_folder,
             keep_path=False)
        if self.settings.os == "Windows":
            os.rename(os.path.join(self.package_folder, "bin", "djinni"),
                      os.path.join(self.package_folder, "bin", "djinni.bat"))
        else:
            executable = os.path.join(self.package_folder, "bin", "djinni")
            os.chmod(executable, os.stat(executable).st_mode | 0o111)

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
