from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class LibDaemonConan(ConanFile):
    name = "libdaemon"
    description = "a lightweight C library that eases the writing of UNIX daemons"
    topics = ("daemon")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://0pointer.de/lennart/projects/libdaemon/"
    license = "LGPL-2.1-or-later"
    settings = "os", "arch", "compiler", "build_type"
    generators = "pkg_config"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _configure_args(self):
        yes_no = lambda v: "yes" if v else "no"
        return [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        self._autotools.configure(configure_dir=self._source_subfolder, args=self._configure_args)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        autotools = self._configure_autotools()
        autotools.install()
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "share"))
        
    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libdaemon"
        self.cpp_info.libs = ["daemon"]
