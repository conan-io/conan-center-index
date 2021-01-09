import os

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration

class LibnumaConan(ConanFile):
    name = "libnuma"
    description = "NUMA support for Linux."
    license = "GPL-2.0-or-later"
    topics = ("conan", "numa")
    homepage = "https://github.com/numactl/numactl"
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

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("{} is only supported on Linux".format(self.name))

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("numactl-" + self.version, self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self)

        args = []
        if self.options.shared:
            args.extend(["--disable-static", "--enable-shared"])
        else:
            args.extend(["--disable-shared", "--enable-static"])

        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("LICENSE.GPL2", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.components["numa"].libs = ["numa"]
        self.cpp_info.components["numa"].names["pkg_config"] = "numa"
        self.cpp_info.components["numa"].names["pkg_config"] = "numa"
        self.cpp_info.components["numa"].system_libs.extend(["dl", "pthread"])
