from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
import os

required_conan_version = ">=1.53.0"

class AdoptiumOpenJDK(ConanFile):
    name = "adopt-openjdk"
    description = "A OpenJDK distribution"
    license = "https://www.eclipse.org/legal/epl-2.0/"
    url = "https://github.com/conan-io/conan-center-index/"
    homepage = "https://www.adoptium.net"
    topics = ("java", "jdk", "openjdk")
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _jni_folder(self):
        folder = {"Linux": "linux", "Macos": "darwin", "Windows": "win32", "AIX": "aix"}.get(str(self._settings_build.os))
        return os.path.join("include", folder)

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        supported_archs = ["x86_64", "armv8", "x86", "ppc64"]
        if self._settings_build.arch not in supported_archs:
            raise ConanInvalidConfiguration(f"Unsupported Architecture ({self._settings_build.arch}). "
                                            f"This version {self.version} currently only supports {supported_archs}.")
        supported_os = ["Windows", "Macos", "Linux", "AIX"]
        if self._settings_build.os not in supported_os:
            raise ConanInvalidConfiguration(f"Unsupported os ({self._settings_build.os}). "
                                            f"This package currently only support {supported_os}.")

    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self._settings_build.os)][str(self._settings_build.arch)], strip_root=True)

    def package(self):
        copy(self, pattern='*', dst=self.package_folder, src=self.source_folder)

    def package_info(self):
        java_home = self.package_folder
        if str(self._settings_build.os) == 'Macos':
            java_home = os.path.join(java_home, 'Contents', 'Home')
       
        bin_path = os.path.join(java_home, "bin")
        self.cpp_info.includedirs = [os.path.join(java_home, 'include'),

                                     os.path.join(java_home, self._jni_folder)]
        self.cpp_info.libdirs = []

        self.output.info(f"Creating JAVA_HOME environment variable with : {java_home}")
        self.env_info.JAVA_HOME = java_home
        self.buildenv_info.define_path("JAVA_HOME", java_home)
        self.runenv_info.define_path("JAVA_HOME", java_home)

        self.output.info(f"Appending PATH environment variable with : {bin_path}")
        self.env_info.PATH.append(bin_path)
