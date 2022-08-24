from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibNlConan(ConanFile):
    name = "libnl"
    description = "A collection of libraries providing APIs to netlink protocol based Linux kernel interfaces."
    topics = ("netlink")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.infradead.org/~tgr/libnl/"
    license = "LGPL-2.1-only"
    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False], "shared": [True, False]}
    default_options = {"fPIC": True, "shared": False}
    build_requires = ( "flex/2.6.4", "bison/3.7.6" )

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Libnl is only supported on Linux")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        config_args = [
            "--prefix={}".format(tools.microsoft.unix_path(self, self.package_folder)),
        ]
        if self.options.shared:
            config_args.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            config_args.extend(["--enable-shared=no", "--enable-static=yes"])

        self._autotools.configure(configure_dir=self._source_subfolder, args=config_args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        autotools.install()
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "etc"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def package_info(self):
        self.cpp_info.components["nl"].libs = ["nl-3"]
        self.cpp_info.components["nl"].includedirs = [os.path.join('include', 'libnl3')]
        if self._settings_build.os != "Windows":
            self.cpp_info.components["nl"].system_libs = ["pthread", "m"]
        self.cpp_info.components["nl-route"].libs = ["nl-route-3"]
        self.cpp_info.components["nl-route"].requires = ["nl"]
        self.cpp_info.components["nl-genl"].libs = ["nl-genl-3"]
        self.cpp_info.components["nl-genl"].requires = ["nl"]
        self.cpp_info.components["nl-nf"].libs = ["nl-nf-3"]
        self.cpp_info.components["nl-nf"].requires = ["nl-route"]
        self.cpp_info.components["nl-cli"].libs = ["nl-cli-3"]
        self.cpp_info.components["nl-cli"].requires = ["nl-nf", "nl-genl"]
        self.cpp_info.components["nl-idiag"].libs = ["nl-idiag-3"]
        self.cpp_info.components["nl-idiag"].requires = ["nl"]
