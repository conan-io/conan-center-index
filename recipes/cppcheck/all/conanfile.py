"""Conan recipe package for cppcheck
"""
import os
from conans import ConanFile, CMake, tools


class CppcheckConan(ConanFile):
    name = "cppcheck"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/danmar/cppcheck"
    topics = ("Cpp Check", "static analyzer")
    description = "Cppcheck is an analysis tool for C/C++ code."
    license = "GPL-3.0-or-later"
    generators = "cmake_find_package"
    settings = "os", "arch", "compiler", "build_type"
    options = {"with_z3": [True, False], "have_rules": [True, False]}
    default_options = {"with_z3": True, "have_rules": True}
    exports_sources = ["patches/**"]
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"
        
    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def requirements(self):
        if self.options.with_z3:
            self.requires("z3/4.8.8")
        if self.options.have_rules:
            self.requires("pcre/8.44")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "cppcheck-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_Z3"] = "ON" if self.options.with_z3 else "OFF"
        cmake.definitions["HAVE_RULES"] = "ON" if self.options.have_rules else "OFF"
        cmake.definitions["Z3_LIBRARIES"] = "z3::z3"
        cmake.definitions["Z3_CXX_INCLUDE_DIRS"] = "${z3_INCLUDE_DIRS}"
        cmake.definitions["USE_MATCHCOMPILER"] = "ON" if self.settings.build_type == "Release" else "OFF"
        cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("*", dst=os.path.join("bin","cfg"), src=os.path.join(self._source_subfolder,"cfg"))
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        
    def package_info(self):
        bin_folder = os.path.join(self.package_folder, "bin")
        self.output.info("Append %s to environment variable PATH" % bin_folder)
        self.env_info.PATH.append(bin_folder)
