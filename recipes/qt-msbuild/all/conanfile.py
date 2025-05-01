import os

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout

required_conan_version = ">=1.53.0"

class QtMSBuildConan(ConanFile):
    name = "qt-msbuild"
    description = "Qt/MSBuild MSBuild rules and targets from Qt VS Tools"
    license = "LicenseRef-Qt-Commercial OR GPL-3.0-only WITH Qt-GPL-exception-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.qt.io"
    topics = ("qt", "msbuild")

    package_type = "build-scripts"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version])

    def package(self):
        copy(self, "*", src=self.source_folder, dst=os.path.join(self.package_folder, "res"))

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]

        self.buildenv_info.define_path("QtMsBuild", os.path.join(self.package_folder, "res"))
