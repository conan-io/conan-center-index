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
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"use_z3": [True, False]}
    default_options = {"use_z3": False}
    
    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"
            
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "cppcheck-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["USE_Z3"] = "ON" if self.options["USE_Z3"] else "OFF"
        cmake.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder)
        return cmake

    def build(self):
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
