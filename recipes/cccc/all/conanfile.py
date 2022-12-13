import os
import shutil
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools import files, build, scm
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.51.3"

class CCCCConan(ConanFile):
    name = "cccc"
    license = "GPL-2.0-or-later"
    homepage = "https://sarnold.github.io/cccc/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "CCCC - Source code counter "\
                  "and metrics tool for C++, C, and Java"
    topics = ("metric", "static analyzer")

    settings = "os", "arch", "compiler", "build_type"

    @property
    def _bin_package_folder(self):
        return os.path.join(self.package_folder,"bin")

    @property
    def _license_folder(self):
        return os.path.join(self.package_folder,"licenses")

    @property
    def _msbuild_bat_file(self):
        return os.path.join(self.source_folder,"cccc","build_msvc.bat")

    @property
    def _cccc_binary_folder(self):
        return os.path.join(self.source_folder,"cccc")

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            files.copy(self,patch["patch_file"],self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
    
    def validate(self):
        if (not is_msvc(self) and (shutil.which("make") == None)):
            raise ConanInvalidConfiguration(f"{self.ref} requires msvc or"\
                                            "make executable")

    def source(self):
        files.get(self,**self.conan_data["sources"][self.version], strip_root=True,
                 destination=self.source_folder)

    def build(self):
        if is_msvc(self):
            self.run(f"{self._msbuild_bat_file} --clean")
        elif (shutil.which("make") != None):
            self.run("make cccc")

    def package(self):
        files.copy(self, "cccc", self._cccc_binary_folder, self._bin_package_folder)
        files.copy(self, "LICENSE", self.source_folder, self._license_folder)
        
    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        self.output.info("Append %s to environment variable PATH" % self._bin_package_folder)
        self.env_info.PATH.append(self._bin_package_folder)