import os, glob
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration

class LibmnlConan(ConanFile):
    name = "libmnl"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://netfilter.org/projects/libmnl/index.html"
    description = "Minimalistic Netlink communication library"
    topics = ("libmnl", "netlink")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def configure(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libmnl is only supported on Linux")
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        config_args = [
            "--prefix={}".format(tools.unix_path(self.package_folder)),
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
        la_pattern = os.path.join(self.package_folder, "lib", "**", "*.la")
        la_files = glob.glob(la_pattern, recursive=True)
        for next_file in la_files:
            os.remove(next_file)
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "etc"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.libs = ["mnl"]
