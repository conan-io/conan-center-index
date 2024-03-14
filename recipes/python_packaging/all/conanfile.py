from conan import ConanFile
from conan.tools.files import copy, get
import os


required_conan_version = ">=1.47.0"


class PackageConan(ConanFile):
    name = "python_packaging"
    description = "Core utilities for Python packages"
    license = "BSD-2-Clause"  # or Apache-2.0
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pypa/packaging/"
    topics = ("python")
    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"

    def package_id(self):
        del self.info.settings.os
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "src"), os.path.join(self.package_folder, "lib", "python3", "dist-packages"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        opengv_dist_packages = os.path.join(self.package_folder, "lib", "python3", "dist-packages")
        self.runenv_info.prepend_path("PYTHONPATH", opengv_dist_packages)
        self.env_info.PYTHONPATH.append(opengv_dist_packages) # remove in conan v2?
