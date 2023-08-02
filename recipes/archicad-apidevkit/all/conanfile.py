from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
from conan.tools.microsoft import check_min_vs, is_msvc
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.52.0"


class ArchicadApidevkitConan(ConanFile):
    name = "archicad-apidevkit"
    description = "The General API Development Kit enables software developers to extend the functionality of Archicad"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://archicadapi.graphisoft.com/"
    license = "LicenseRef-LICENSE"
    topics = ("api", "archicad", "development", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if self.settings.build_type == "Debug":
            raise ConanInvalidConfiguration("Debug configuration is not supported")
        if is_msvc(self):
            # Approximate requirement for toolset >= v142
            check_min_vs(self, "192")
        if not self.info.settings.os in ("Macos", "Windows"):
            raise ConanInvalidConfiguration(
                f"{self.ref} is not supported by the OS {self.info.settings.os}")
        if not str(self.settings.arch) in ("x86_64"):
            raise ConanInvalidConfiguration(
                f"{self.ref} is not supported yet.")

    def build(self):
        devkit, licenses = self.conan_data["sources"][self.version][str(self.settings.os)][str(self.settings.arch)]
        get(self, **devkit, destination=os.path.join(self.package_folder, "bin"), strip_root=True)
        get(self, **licenses, destination=os.path.join(self.package_folder, "licenses"), strip_root=True)

    def package(self):
        copy(self, "bin", src=self.build_folder, dst=self.package_folder)
        copy(self, "licenses", src=self.build_folder, dst=self.package_folder)

    def package_info(self):
        self.cpp_info.bindirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []

        # These are dependencies of third party vendored libraries
        self.cpp_info.system_libs = [
            "WinMM", "MSImg32", "WS2_32", "USP10", "DNSApi"]
        if self.settings.os == "Macos":
            self.cpp_info.frameworks = ["CoreText", "CoreFoundation", "CoreServices",
                                        "ApplicationServices", "Carbon", "CoreGraphics", "AppKit", "Foundation"]
        else:
            self.cpp_info.system_libs.extend(["gdiplus", "iphlpapi"])

        devkit_dir = os.path.join(self.package_folder, "bin")
        self.output.info(f"Setting AC_API_DEVKIT_DIR environment variable: {devkit_dir}")
        self.env_info.AC_API_DEVKIT_DIR = devkit_dir
        self.buildenv_info.define("AC_API_DEVKIT_DIR", devkit_dir)
