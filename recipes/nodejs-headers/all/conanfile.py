import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, download, collect_libs

required_conan_version = ">=1.59.0"


class NodeJSHeadersConan(ConanFile):
    name = "nodejs-headers"
    description = "Resources for building/linking Node.js native addons"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://nodejs.org"
    topics = ("node", "napi", "headers", "header-only")

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True
    short_paths = True

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    @property
    def _dl_info_headers(self):
        return self.conan_data["sources"].get(self.version, {}).get("Headers")

    @property
    def _dl_info_import_libs(self):
        return self.conan_data["sources"].get(self.version, {}).get(str(self.settings.os), {}).get("import_libs", {}).get(str(self.settings.arch), {})

    @property
    def _dl_info_pdbs(self):
        return self.conan_data["sources"].get(self.version, {}).get(str(self.settings.os), {}).get("pdbs", {}).get(str(self.settings.arch), {})

    def validate(self):
        if not self._dl_info_headers or (self.settings.os == "Windows" and 
                                         (not self._dl_info_import_libs or not self._dl_info_pdbs)):
            raise ConanInvalidConfiguration("Resources for this combination of architecture/version/os not available")

    def build(self):
        get(self, **self._dl_info_headers, strip_root=True)
        if self.settings.os == "Windows":
            download(self, **self._dl_info_import_libs, filename="node.lib")
            if self.settings.build_type == "Debug":
                get(self, **self._dl_info_pdbs)

    def package(self):
        copy(self, "*", dst=os.path.join(self.package_folder, "include"), src=os.path.join(self.build_folder, "include"))
        if self.settings.os == "Windows":
            copy(self, "node.lib", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder)
            if self.settings.build_type == "Debug":
                copy(self, "node.pdb", dst=os.path.join(self.package_folder, "lib"), src=self.build_folder)

    def package_info(self):
        if self.settings.os == "Windows":
            self.cpp_info.libs = collect_libs(self)

