from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import apply_conandata_patches, copy, download, export_conandata_patches, get, save
from conan.tools.layout import basic_layout
import os
import stat
import textwrap

required_conan_version = ">=2.0"


class Antlr3Conan(ConanFile):
    name = "antlr3"
    description = "ANTLR v3 parser generator: the antlr3 tool and the header-only C++ runtime"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/antlr/antlr3"
    topics = ("antlr", "parser", "generator", "grammar", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # Only needed to run the tool, not by the C++ runtime headers
        self.requires("openjdk/21.0.2", run=True, headers=False, libs=False)

    def package_id(self):
        self.info.clear()

    def validate(self):
        check_min_cppstd(self, 11)

    @property
    def _jar_name(self):
        return f"antlr-complete-{self.version}.jar"

    def source(self):
        get(self, **self.conan_data["sources"][self.version]["source"], strip_root=True)
        apply_conandata_patches(self)
        download(self, filename=self._jar_name, **self.conan_data["sources"][self.version]["jar"])

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.txt", os.path.join(self.source_folder, "tool"), os.path.join(self.package_folder, "licenses"))
        copy(self, "*", os.path.join(self.source_folder, "runtime", "Cpp", "include"), os.path.join(self.package_folder, "include"))
        copy(self, self._jar_name, self.source_folder, os.path.join(self.package_folder, "res"))

        # The package is OS independent, so ship both launchers; each locates the jar relative to itself
        save(self, os.path.join(self.package_folder, "bin", "antlr3.bat"), textwrap.dedent(f"""\
            @echo off
            if defined JAVA_HOME (set "JAVA=%JAVA_HOME%\\bin\\java") else (set "JAVA=java")
            "%JAVA%" -cp "%~dp0..\\res\\{self._jar_name}" org.antlr.Tool %*
            """))
        launcher = os.path.join(self.package_folder, "bin", "antlr3")
        save(self, launcher, textwrap.dedent(f"""\
            #!/bin/sh
            here="$(cd "$(dirname "$0")" && pwd)"
            java="${{JAVA_HOME:+$JAVA_HOME/bin/}}java"
            exec "$java" -cp "$here/../res/{self._jar_name}" org.antlr.Tool "$@"
            """))
        os.chmod(launcher, os.stat(launcher).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ANTLR3")
        self.cpp_info.set_property("cmake_target_name", "ANTLR3::antlr3")
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = ["res"]

        jar = os.path.join(self.package_folder, "res", self._jar_name)
        self.buildenv_info.define_path("ANTLR3_JAR", jar)
        self.runenv_info.define_path("ANTLR3_JAR", jar)
