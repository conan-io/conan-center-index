from conans import ConanFile, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.29.1"


class Argon2Conan(ConanFile):
    name = "argon2"
    license = "Apache 2.0", "CC0-1.0"
    homepage = "https://github.com/P-H-C/phc-winner-argon2"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Argon2 password hashing library"
    topics = ("argon2", "crypto", "password hashing")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = "patches/**"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("argon2 recipe currently does not offer Windows support")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("phc-winner-argon2-{0}".format(self.version), self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("make libs")

    def package(self):
        self.copy("*LICENSE", src=self._source_subfolder, dst="licenses", keep_path=False)
        with tools.chdir(self._source_subfolder):
            self.run("make DESTDIR={} PREFIX= LIBRARY_REL=lib install".format(self.package_folder))
        # drop unneeded dirs
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "bin"))
        # drop unneeded libs
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a*")
        else:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.so*")
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.dylib")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libargon2"
        self.cpp_info.libs = ["argon2"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["pthread"]
