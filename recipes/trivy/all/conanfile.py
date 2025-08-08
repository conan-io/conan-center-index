import os

from conan import ConanFile
from conan.tools.files import get, copy, rmdir
from conan.tools.scm import Version
from conan import conan_version
from conan.errors import ConanInvalidConfiguration


required_conan_version = ">=1.51.0"

class TrivyConan(ConanFile):
    name = "trivy"
    package_type = "application"
    description = "Trivy Security Scanner."
    topics = ("build", "scanner")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aquasecurity/trivy/"
    license = "Apache-2.0"
    settings = "os", "arch"

    def build(self):
        arch = str(self.settings.arch) if self.settings.os != "Macos" else "universal"
        get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][arch],
            destination=self.source_folder)
        
    def package(self):
        copy(self, "*", src=self.build_folder, dst=self.package_folder)

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        bindir = os.path.join(self.package_folder)
        self.cpp_info.bindirs = [bindir]
        
        if conan_version.major < 2:
            # Needed for compatibility with v1.x - Remove when 2.0 becomes the default
            self.output.info(f"Appending PATH environment variable: {bindir}")
            self.env_info.PATH.append(bindir)

