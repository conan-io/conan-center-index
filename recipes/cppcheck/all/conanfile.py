from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir
import os

required_conan_version = ">=1.46.0"


class CppcheckConan(ConanFile):
    name = "cppcheck"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/danmar/cppcheck"
    topics = ("cpp check", "static analyzer")
    description = "Cppcheck is an analysis tool for C/C++ code."
    license = "GPL-3.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"with_z3": [True, False, "deprecated"], "have_rules": [True, False]}
    default_options = {"with_z3": "deprecated", "have_rules": True}

    def layout(self):
        cmake_layout(self)

    def configure(self):
        if self.options.with_z3 != "deprecated":
            self.output.warn("with_z3 option is deprecated, do not use anymore.")

    def package_id(self):
        del self.info.options.with_z3

    def requirements(self):
        if self.options.have_rules:
            self.requires("pcre/8.45")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["HAVE_RULES"] = self.options.have_rules
        tc.variables["USE_MATCHCOMPILER"] = "Auto"
        tc.variables["ENABLE_OSS_FUZZ"] = False
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        replace_in_file(self, os.path.join(self.source_folder, "tools", "CMakeLists.txt"), "CMAKE_SOURCE_DIR", "PROJECT_SOURCE_DIR")
        replace_in_file(self, os.path.join(self.source_folder, "cmake", "findDependencies.cmake"), "PCRE_LIBRARY pcre", "PCRE_LIBRARY NAMES pcre pcred")
        replace_in_file(self, os.path.join(self.source_folder, "htmlreport", "cppcheck-htmlreport"), "#!/usr/bin/env python", "#!/usr/bin/env python3")
        replace_in_file(self, os.path.join(self.source_folder, "cli", "CMakeLists.txt"),
                              "RUNTIME DESTINATION ${CMAKE_INSTALL_FULL_BINDIR}",
                              "DESTINATION ${CMAKE_INSTALL_FULL_BINDIR}")
        replace_in_file(self, os.path.join(self.source_folder, "cli", "CMakeLists.txt"), "add_dependencies(cppcheck run-dmake)", "")

        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=os.path.join(self.source_folder))
        copy(self, "*", dst=os.path.join(self.package_folder, "bin", "cfg"), src=os.path.join(self.source_folder, "cfg"))
        copy(self, "cppcheck-htmlreport", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.source_folder, "htmlreport"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bin_folder = os.path.join(self.package_folder, "bin")
        self.output.info("Append %s to environment variable PATH" % bin_folder)
        self.env_info.PATH.append(bin_folder)
        self.env_info.CPPCHECK_HTMLREPORT = os.path.join(bin_folder, "cppcheck-htmlreport")
