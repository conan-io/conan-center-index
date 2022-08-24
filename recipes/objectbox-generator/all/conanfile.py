from conans import CMake, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class PackageConan(ConanFile):
    name = "objectbox-generator"
    description = "ObjectBox Generator based on FlatBuffers schema files (fbs) for C and C++"
    license = "GPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/objectbox/objectbox-generator"
    topics = ("database", "code-generator", "objectbox")
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def validate(self):
        if self.settings.os not in ["Linux", "Windows", "Macos"] or self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("{} doesn't support current environment".format(self.name))

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version][str(self.settings.os)],
                  destination=self.source_folder)
        tools.files.download(self, **self.conan_data["sources"][self.version]["License"], filename="LICENSE.txt")

    def package(self):
        if self.settings.os != "Windows":
            bin_path = os.path.join(self.source_folder, "objectbox-generator")
            os.chmod(bin_path, os.stat(bin_path).st_mode | 0o111)
        self.copy("objectbox-generator*", src=self.source_folder, dst="bin", keep_path=False)
        self.copy("LICENSE.txt", dst="licenses", src=self.source_folder)

    def package_info(self):
        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var: {}".format(binpath))
        self.env_info.PATH.append(binpath)

        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
