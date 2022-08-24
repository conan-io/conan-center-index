from conans import ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class OpenJDK(ConanFile):
    name = "openjdk"
    url = "https://github.com/conan-io/conan-center-index/"
    description = "Java Development Kit builds, from Oracle"
    homepage = "https://jdk.java.net"
    license = "GPL-2.0-with-classpath-exception"
    topics = ("java", "jdk", "openjdk")
    settings = "os", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.settings.arch != "x86_64":
            raise ConanInvalidConfiguration("Unsupported Architecture.  This package currently only supports x86_64.")
        if self.settings.os not in ["Windows", "Macos", "Linux"]:
            raise ConanInvalidConfiguration("Unsupported os. This package currently only support Linux/Macos/Windows")

    def build(self):
        tools.get(**self.conan_data["sources"][self.version][str(self.settings.os)],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        if self.settings.os == "Macos":
            _source_subfolder = os.path.join(self._source_subfolder, "jdk-{}.jdk".format(self.version), "Contents", "Home")
        else:
            _source_subfolder = self._source_subfolder
        self.copy(pattern="*", dst="bin", src=os.path.join(_source_subfolder, "bin"),
                  excludes=("msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll"))
        self.copy(pattern="*", dst="include", src=os.path.join(_source_subfolder, "include"))
        self.copy(pattern="*", dst="lib", src=os.path.join(_source_subfolder, "lib"))
        self.copy(pattern="*", dst=os.path.join("lib", "jmods"), src=os.path.join(_source_subfolder, "jmods"))
        self.copy(pattern="*", dst="licenses", src=os.path.join(_source_subfolder, "legal"))
        # conf folder is required for security settings, to avoid
        # java.lang.SecurityException: Can't read cryptographic policy directory: unlimited
        # https://github.com/conan-io/conan-center-index/pull/4491#issuecomment-774555069
        self.copy(pattern="*", dst="conf", src=os.path.join(_source_subfolder, "conf"))

    def package_info(self):
        self.output.info("Creating JAVA_HOME environment variable with : {0}".format(self.package_folder))
        self.env_info.JAVA_HOME = self.package_folder

        self.output.info("Appending PATH environment variable with : {0}".format(os.path.join(self.package_folder, "bin")))
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
