from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os, platform, glob


class ZuluOpenJDK(ConanFile):
    name = "zulu-openjdk"
    url = "https://github.com/conan-io/conan-center-index/"
    description = "A OpenJDK distribution"
    homepage = "https://www.azul.com"
    license = "https://www.azul.com/products/zulu-and-zulu-enterprise/zulu-terms-of-use/"
    topics = ("java", "jdk")
    settings = "os", "arch"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _jni_folder(self):
        folder = {"Linux": "linux", "Darwin": "darwin", "Windows": "win32"}.get(platform.system())
        return os.path.join("include", folder)

    def configure(self):
        # Checking against self.settings.* would prevent cross-building profiles from working
        # TODO, I think for the new, 2 profile builds, this can be done ...
        if tools.detected_architecture() != "x86_64":
            raise ConanInvalidConfiguration("Unsupported Architecture.  This package currently only supports x86_64.")
        if platform.system() not in ["Windows", "Darwin", "Linux"]:
            raise ConanInvalidConfiguration("Unsupported System. This package currently only support Linux/Darwin/Windows")

    def source(self):
        url = self.conan_data["sources"][self.version]["url"][str(self.settings.os)]
        checksum = self.conan_data["sources"][self.version]["sha256"][str(self.settings.os)]
        tools.get(url, sha256=checksum)
        os.rename(glob.glob("zulu*")[0], self._source_subfolder)

    def build(self):
        pass # nothing to do, but this shall trigger no warnings ;-)

    def package(self):
        self.copy(pattern="*", dst=".", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.includedirs.append(self._jni_folder)
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.libs = tools.collect_libs(self)

        java_home = os.path.join(self.package_folder)
        bin_path = os.path.join(java_home, "bin")

        self.output.info("Creating JAVA_HOME environment variable with : {0}".format(java_home))
        self.env_info.JAVA_HOME = java_home

        self.output.info("Appending PATH environment variable with : {0}".format(bin_path))
        self.env_info.path.append(bin_path)
