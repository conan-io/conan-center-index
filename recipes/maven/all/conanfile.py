from conan import ConanFile
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.47.0"

class MavenConan(ConanFile):
    name = "maven"
    description = "Apache Maven is a software project management and comprehension tool."
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://maven.apache.org/"
    topics = ("build", "project management")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def requirements(self):
        self.requires("zulu-openjdk/21.0.1")

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        for target in ("bin", "boot", "conf", "lib"):
            copy(self, pattern="*", dst=os.path.join(self.package_folder, target), src=os.path.join(self.source_folder, target))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []
