from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, copy
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.1"

class ZuluOpenJDK(ConanFile):
    name = "zulu-openjdk"
    description = "A OpenJDK distribution"
    license = "https://www.azul.com/products/zulu-and-zulu-enterprise/zulu-terms-of-use/" # pylint: disable=cci-invalid-recipe-license
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.azul.com"
    topics = ("java", "jdk", "openjdk")
    package_type = "application"
    settings = "os", "arch"
    upload_policy = "skip"
    build_policy = "missing"

    def layout(self):
        basic_layout(self, src_folder="src")

    def validate(self):
        supported_archs = ["x86_64", "armv8"]
        if self.settings.arch not in supported_archs:
            raise ConanInvalidConfiguration(f"Unsupported Architecture ({self.settings.arch}). "
                                            f"This version {self.version} currently only supports {supported_archs}.")
        supported_os = ["Windows", "Macos", "Linux"]
        if self.settings.os not in supported_os:
            raise ConanInvalidConfiguration(f"Unsupported os ({self.settings.os}). "
                                            f"This package currently only support {supported_os}.")

    def source(self):
        # we don't have sources, and we can't download binaries here because they depend on settings
        pass

    def build(self):
        get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)], strip_root=True)

    def package(self):
        # INFO: Azul is changing the directory layout inside macOS bundles so that only the Contents directory
        # https://foojay.io/today/azul-zulu-april-2026-quarterly-update-released/
        build_folder = self.build_folder
        if self.settings.os == "Macos":
            build_folder = os.path.join(build_folder, "Contents", "Home")

        copy(self, pattern="*", dst=os.path.join(self.package_folder, "bin"),
             src=os.path.join(build_folder, "bin"),
             excludes=("msvcp140.dll", "vcruntime140.dll", "vcruntime140_1.dll"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "include"),
             src=os.path.join(build_folder, "include"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "lib"),
             src=os.path.join(build_folder, "lib"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "res"),
             src=os.path.join(build_folder, "conf"))
        # conf folder is required for security settings, to avoid
        # java.lang.SecurityException: Can't read cryptographic policy directory: unlimited
        # https://github.com/conan-io/conan-center-index/pull/4491#issuecomment-774555069
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "conf"),
             src=os.path.join(build_folder, "conf"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "licenses"),
             src=os.path.join(build_folder, "legal"))
        copy(self, pattern="*", dst=os.path.join(self.package_folder, "lib", "jmods"),
             src=os.path.join(build_folder, "jmods"))

    def package_info(self):
        include_folder = {"Linux": "linux", "Macos": "darwin", "Windows": "win32"}.get(str(self.settings.os))
        self.cpp_info.includedirs.append(os.path.join("include", include_folder))
        self.cpp_info.libdirs = []

        java_home = self.package_folder
        self.buildenv_info.define_path("JAVA_HOME", java_home)
        self.runenv_info.define_path("JAVA_HOME", java_home)
