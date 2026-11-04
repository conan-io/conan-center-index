import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get

required_conan_version = ">=1.59.0"


class NodejsConan(ConanFile):
    name = "nodejs"
    description = "Node.js is an open-source, cross-platform JavaScript runtime environment."
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nodejs.org"
    topics = ("node", "javascript", "runtime", "pre-built")

    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def layout(self):
        pass

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    @property
    def _nodejs_arch(self):
        if str(self.settings.os) in ["Linux", "FreeBSD"]:
            if str(self.settings.arch).startswith("armv7"):
                return "armv7"
            if str(self.settings.arch).startswith("armv8") and "32" not in str(self.settings.arch):
                return "armv8"
        return str(self.settings.arch)

    @property
    def _dl_info(self):
        return self.conan_data["sources"].get(self.version, {}).get(str(self.settings.os), {}).get(self._nodejs_arch)

    def validate(self):
        if not self._dl_info:
            raise ConanInvalidConfiguration("Binaries for this combination of architecture/version/os not available")

    def build(self):
        get(self, **self._dl_info, strip_root=True)

    def package(self):
        copy(self, "LICENSE", dst=os.path.join(self.package_folder, "licenses"), src=self.build_folder)
        copy(self, "*", dst=os.path.join(self.package_folder, "bin"), src=os.path.join(self.build_folder, "bin"))
        copy(self, "*", dst=os.path.join(self.package_folder, "lib"), src=os.path.join(self.build_folder, "lib"))
        copy(self, "node.exe", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder)
        copy(self, "npm", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder)
        copy(self, "npx", dst=os.path.join(self.package_folder, "bin"), src=self.build_folder)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.frameworkdirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.resdirs = []

        # TODO: Legacy, to be removed on Conan 2.0
        bin_dir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_dir)
