from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class BonjourSystemConan(ConanFile):
    name = "bonjour"
    version = "system"
    description = "Conan package for Apple's Bonjour"
    topics = ("Bonjour", "DNS-SD", "mDNS")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://developer.apple.com/bonjour/"
    license = "Apache-2.0", "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os != "Windows" or tools.cross_building(self):
            raise ConanInvalidConfiguration("Only Windows is supported for this package.")

    def system_requirements(self):
        # extract and install Bonjour64.msi from downloaded BonjourPSSetup.exe
        # see https://community.chocolatey.org/packages/bonjour#files
        package_tool = tools.SystemPackageTool(tool=tools.ChocolateyTool())
        package_tool.install(packages=["bonjour"])

    def package_info(self):
        self.cpp_info.system_libs = ["dns_sd"]
