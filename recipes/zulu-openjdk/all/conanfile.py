from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
import os
import stat

required_conan_version = ">=1.53.0"


class ZuluOpenJDK(ConanFile):
    name = "zulu-openjdk"
    description = "A OpenJDK distribution"
    license = "https://www.azul.com/products/zulu-and-zulu-enterprise/zulu-terms-of-use/"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://www.azul.com"
    topics = ("java", "jdk", "openjdk")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_host(self):
        return getattr(self, "settings_host", self.settings)

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _jni_folder(self):
        folder = {"Linux": "linux", "Macos": "darwin",
                  "Windows": "win32", "SunOS": "solaris"}.get(str(self._settings_host.os))
        return os.path.join("include", folder)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        srcs = self.conan_data["sources"].get(self.version, {}).get(str(self._settings_host.os))
        if srcs is None:
            raise ConanInvalidConfiguration(f"Unsupported os ({self._settings_host.os}). "
                                            f"This version {self.version} currently does not support"
                                            f" {self._settings_host.arch} on {self._settings_host.os})")
        if srcs.get(str(self._settings_host.arch)) is None:
            raise ConanInvalidConfiguration(f"Unsupported Architecture ({self._settings_host.arch}). "
                                            f"This version {self.version} currently does not support"
                                            f" {self._settings_host.arch} on {self._settings_host.os})")

    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self._settings_host.os)]
            [str(self._settings_host.arch)], strip_root=True)

    def package(self):
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "bin"),
             src=os.path.join(self.source_folder, "bin"),
             excludes=("msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(self.source_folder, "include"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "lib"),
             src=os.path.join(self.source_folder, "lib"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "res"),
             src=os.path.join(self.source_folder, "conf"))
        # conf folder is required for security settings, to avoid
        # java.lang.SecurityException: Can't read cryptographic policy directory: unlimited
        # https://github.com/conan-io/conan-center-index/pull/4491#issuecomment-774555069
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "conf"),
             src=os.path.join(self.source_folder, "conf"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(self.source_folder, "legal"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "lib", "jmods"),
             src=os.path.join(self.source_folder, "jmods"))

    def package_info(self):
        self.cpp_info.includedirs.append(self._jni_folder)
        self.cpp_info.libdirs = []

        java_home = self.package_folder
        bin_path = os.path.join(java_home, "bin")

        self.output.info(f"Creating JAVA_HOME environment variable with : {java_home}")
        self.env_info.JAVA_HOME = java_home
        self.buildenv_info.define_path("JAVA_HOME", java_home)
        self.runenv_info.define_path("JAVA_HOME", java_home)

        self.output.info(f"Appending PATH environment variable with : {bin_path}")
        self.env_info.PATH.append(bin_path)
