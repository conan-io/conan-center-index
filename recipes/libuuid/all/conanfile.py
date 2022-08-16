from conan import ConanFile
from conan.tools import files
from conan.errors import ConanInvalidConfiguration
from conans import AutoToolsBuildEnvironment, tools
import os

required_conan_version = ">=1.33.0"


class LibuuidConan(ConanFile):
    name = "libuuid"
    description = "Portable uuid C library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/libuuid/"
    license = "BSD-3-Clause"
    topics = ("conan", "libuuid", "uuid", "unique-id", "unique-identifier")
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/**"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("libuuid is not supported on Windows")

    def build_requirements(self):
        self.build_requires("libtool/2.4.7")

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        configure_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        if "x86" in self.settings.arch:
            self._autotools.flags.append('-mstackrealign')
        self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), run_environment=True)
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "uuid"
        self.cpp_info.libs = ["uuid"]
        self.cpp_info.includedirs.append(os.path.join("include", "uuid"))
