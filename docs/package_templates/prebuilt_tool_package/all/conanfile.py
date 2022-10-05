from conan import ConanFile
from conan.tools.files import get, copy
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.47.0"


class PackageConan(ConanFile):
    name = "package"
    description = "short description"
    license = "" # Use short name only, conform to SPDX License List: https://spdx.org/licenses/
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/project/package"
    topics = ("topic1", "topic2", "topic3", "pre-built") # no "conan"  and project name in topics. Use "pre-built" for tooling packages
    settings = "os", "arch", "compiler", "build_type" # even for pre-built executables

    # not needed but supress warning message from conan commands
    def layout(self):
        pass

    # specific compiler and build type, usually are not distributed by vendors
    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    # in case some configuration is not supported
    def validate(self):
        if self.info.settings.os == "Macos" and Version(self.info.settings.os.version) < 11:
            raise ConanInvalidConfiguration(f"{self.ref} requires OSX >=11.")

    # do not cache as source, instead, use build folder
    def source(self):
        pass

    # download the source here, than copy to package folder
    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)],
            destination=self.source_folder, strip_root=True)

    # copy all needed files to the package folder
    def package(self):
        # a license file is always mandatory
        copy(self, pattern="LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        copy(self, pattern="*.exe", dst=os.path.join(self.package_folder, "bin"), src=self.source_folder)
        copy(self, pattern="foo", dst=os.path.join(self.package_folder, "bin"), src=self.source_folder)

    def package_info(self):
        # folders not used for pre-built binaries
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []
        self.cpp_info.includedirs = []

        bin_folder = os.path.join(self.package_folder, "bin")
        # In case need to find packaged tools when building a package
        self.buildenv_info.append("PATH", bin_folder)
        # In case need to find packaged tools at runtime
        self.runenv_info.append("PATH", bin_folder)
        # TODO: Legacy, to be removed on Conan 2.0
        self.env_info.PATH.append(bin_folder)
