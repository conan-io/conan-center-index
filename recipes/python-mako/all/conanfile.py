import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


required_conan_version = ">=1.47.0"


class PackageConan(ConanFile):
    name = "python-mako"
    description = "A template library written in Python"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.makotemplates.org/"
    topics = ("python", "template")
    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "mako"), os.path.join(self.package_folder, "lib", "python3", "dist-packages", "mako"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        dist_packages = os.path.join(self.package_folder, "lib", "python3", "dist-packages")
        self.runenv_info.prepend_path("PYTHONPATH", dist_packages)
        self.env_info.PYTHONPATH.append(dist_packages) # remove in conan v2?
