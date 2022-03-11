from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.36.0"


class HiredisConan(ConanFile):
    name = "hiredis"
    description = "Hiredis is a minimalistic C client library for the Redis database."
    license = "BSD-3-Clause"
    topics = ("hiredis", "redis", "client", "database")
    homepage = "https://github.com/redis/hiredis"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("hiredis {} is not supported on Windows.".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # Do not force PIC if static
        if not self.options.shared:
            makefile = os.path.join(self._source_subfolder, "Makefile")
            tools.replace_in_file(makefile, "-fPIC ", "")

    def build(self):
        self._patch_sources()
        with tools.chdir(self._source_subfolder):
            autoTools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            autoTools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            autoTools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            autoTools.install(vars={
                "DESTDIR": tools.unix_path(self.package_folder),
                "PREFIX": "",
            })
        tools.remove_files_by_mask(
            os.path.join(self.package_folder, "lib"),
            "*.a" if self.options.shared else "*.[so|dylib]*",
        )
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "hiredis")
        self.cpp_info.libs = ["hiredis"]
