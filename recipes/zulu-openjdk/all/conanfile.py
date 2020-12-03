from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os, glob


class ZuluOpenJDK(ConanFile):
    name = "zulu-openjdk"
    url = "https://github.com/conan-io/conan-center-index/"
    description = "A OpenJDK distribution"
    homepage = "https://www.azul.com"
    license = "https://www.azul.com/products/zulu-and-zulu-enterprise/zulu-terms-of-use/"
    topics = ("java", "jdk", "openjdk")
    settings = "os", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _jni_folder(self):
        folder = {"Linux": "linux", "Macos": "darwin", "Windows": "win32"}.get(str(self.settings.os))
        return os.path.join("include", folder)

    def configure(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Unsupported Architecture.  This package currently only supports x86_64.")
        if self.settings.os not in ["Windows", "Macos", "Linux"]:
            raise ConanInvalidConfiguration("Unsupported os. This package currently only support Linux/Macos/Windows")

    def source(self):
        url = self.conan_data["sources"][self.version]["url"][str(self.settings.os)]
        checksum = self.conan_data["sources"][self.version]["sha256"][str(self.settings.os)]
        tools.get(url, sha256=checksum)
        os.rename(glob.glob("zulu*")[0], self._source_subfolder)

    def build(self):
        pass # nothing to do, but this shall trigger no warnings ;-)

    def package(self):
        self.copy(pattern="*", dst="bin", src=os.path.join(self._source_subfolder, "bin"), excludes=("msvcp140.dll", "vcruntime140.dll"))
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "include"))
        self.copy(pattern="*", dst="lib", src=os.path.join(self._source_subfolder, "lib"))
        self.copy(pattern="*", dst="res", src=os.path.join(self._source_subfolder, "conf"))
        self.copy(pattern="*", dst="licenses", src=os.path.join(self._source_subfolder, "legal"))
        self.copy(pattern="*", dst=os.path.join("lib", "jmods"), src=os.path.join(self._source_subfolder, "jmods"))

    def package_info(self):
        self.cpp_info.includedirs.append(self._jni_folder)
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.libs = tools.collect_libs(self)

        java_home = self.package_folder
        bin_path = os.path.join(java_home, "bin")

        self.output.info("Creating JAVA_HOME environment variable with : {0}".format(java_home))
        self.env_info.JAVA_HOME = java_home

        self.output.info("Appending PATH environment variable with : {0}".format(bin_path))
        self.env_info.PATH.append(bin_path)
