import os

from conan import ConanFile, conan_version
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"


class MPCGeneratorConan(ConanFile):
    name = "makefile-project-workspace-creator"
    description = "The Makefile, Project and Workspace Creator"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/objectcomputing/MPC"
    topics = ("objectcomputing", "installer")

    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def build_requirements(self):
        if self.settings.os == "Windows":
            kwargs = dict(visible=True) if conan_version.major >= 2 else {}
            self.tool_requires("strawberryperl/5.32.1.1", **kwargs)

    def package_id(self):
        self.info.clear()

    def build(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        copy(self, "*",
             src=self.build_folder,
             dst=os.path.join(self.package_folder, "bin"))
        copy(self, "LICENSE",
            src=os.path.join(self.build_folder, "docs"),
            dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        bin_path = os.path.join(self.package_folder, "bin")
        self.buildenv_info.define("MPC_ROOT", bin_path)

        self.env_info.PATH.append(bin_path)
        self.env_info.MPC_ROOT = bin_path
