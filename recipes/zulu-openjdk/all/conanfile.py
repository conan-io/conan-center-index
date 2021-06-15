from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob


class ZuluOpenJDK(ConanFile):
    name = "zulu-openjdk"
    url = "https://github.com/conan-io/conan-center-index/"
    description = "An OpenJDK distribution"
    homepage = "https://www.azul.com"
    license = "https://www.azul.com/products/zulu-and-zulu-enterprise/zulu-terms-of-use/"
    topics = ("java", "jdk", "openjdk")
    settings = "os", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _jni_folder(self):
        folder = {"Linux": "linux", "Macos": "darwin",
                  "Windows": "win32"}.get(str(self.settings.os))
        return os.path.join("include", folder)

    @property
    def _binary_key(self):
        return '{0}_{1}'.format(self.settings.os, self.settings.arch)

    def configure(self):
        data = self.conan_data["sources"][self.version].get(self._binary_key, None)
        if data is None:
            raise ConanInvalidConfiguration("Unsupported Architecture.  No data was found in {0} for OS "
                                            "{1} with arch {2}".format(self.version, self.settings.os,
                                                                       self.settings.arch))
        if self.settings.os not in ["Windows", "Macos", "Linux"]:
            raise ConanInvalidConfiguration("Unsupported os. This package currently only"
                                            " supports Linux/Macos/Windows")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version][self._binary_key],
                  destination=self._source_subfolder, strip_root=True, keep_permissions=True)

    def build(self):
        pass  # nothing to do, but this shall trigger no warnings ;-)

    def package(self):
        self.copy(pattern='*', dst='.', src=self._source_subfolder,
                  excludes=("msvcp140.dll", "vcruntime140.dll"))

    def package_info(self):
        self.cpp_info.includedirs.append(self._jni_folder)
        self.cpp_info.libdirs = []

        java_home = self.package_folder
        bin_path = os.path.join(java_home, "bin")

        self.output.info("Creating JAVA_HOME environment variable with : {0}".format(java_home))
        self.env_info.JAVA_HOME = java_home

        self.output.info("Appending PATH environment variable with : {0}".format(bin_path))
        self.env_info.PATH.append(bin_path)
