from conan import ConanFile
from conan.tools.files import copy, download, save
import os
import stat


required_conan_version = ">=1.47.0"


class Antlr4Conan(ConanFile):
    name = "antlr4"
    description = "powerful parser generator for reading, processing, executing, or translating structured text or binary files."
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/antlr/antlr4"
    topics = ("parser", "generator")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        pass

    def requirements(self):
        self.requires("openjdk/21.0.1")

    def package_id(self):
        del self.info.settings.arch
        del self.info.settings.compiler
        del self.info.settings.build_type

    def source(self):
        v = self.conan_data["sources"][self.version]
        download(
                self,
                url=v["jar"]["url"],
                filename=os.path.join(self.source_folder, "antlr-complete.jar"),
                sha256=v["jar"]["sha256"],
                )
        download(
                self,
                url=v["license"]["url"],
                filename=os.path.join(self.source_folder, "LICENSE.txt"),
                sha256=v["license"]["sha256"],
                )

    def package(self):
        copy(self, pattern="LICENSE.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="antlr-complete.jar", dst=os.path.join(self.package_folder, "res"), src=self.source_folder)
        if self.settings.os == "Windows":
            save(self,
                 path=os.path.join(self.package_folder, "bin", "antlr4.bat"),
                 content="""\
                         java -classpath %CLASSPATH% org.antlr.v4.Tool %*
                         """
                 )
        else:
            bin_path = os.path.join(self.package_folder, "bin", "antlr4")
            save(self,
                 path=bin_path,
                 content="""\
                         #!/bin/bash
                         java -classpath $CLASSPATH org.antlr.v4.Tool $@
                         """
                 )
            st = os.stat(bin_path)
            os.chmod(bin_path, st.st_mode | stat.S_IEXEC)

    def package_info(self):
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        jar = os.path.join(self.package_folder, "res", "antlr-complete.jar")
        self.runenv_info.prepend_path("CLASSPATH", jar)
