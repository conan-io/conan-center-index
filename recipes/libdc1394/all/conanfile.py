from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os


class Libdc1394Conan(ConanFile):
    name = "libdc1394"
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = 'https://damien.douxchamps.net/ieee1394/libdc1394/'
    description = "libdc1394 provides a complete high level API to control IEEE 1394 based cameras"
    topics = ("conan", "ieee1394", "camera", "iidc", "dcam")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _env_build = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def _configure_autotools(self):
        if not self._env_build:
            self._env_build = AutoToolsBuildEnvironment(self)
            if self.options.shared:
                args = ["--disable-static", "--enable-shared"]
            else:
                args = ["--disable-shared", "--enable-static"]
            args.extend(["--disable-examples"])
            self._env_build.configure(args=args)
        return self._env_build

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows is not supported")
        if self.settings.compiler == "clang":
            raise ConanInvalidConfiguration("Clang doesn't support VLA")
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("libdc1394-%s" % self.version, self._source_subfolder)

    def build(self):
        with tools.chdir(self._source_subfolder):
            env_build = self._configure_autotools()
            env_build.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            env_build = self._configure_autotools()
            env_build.install()

        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libdc1394-{}".format(tools.Version(self.version).major)
        self.cpp_info.libs = ["dc1394"]
        if tools.is_apple_os(self.settings.os):
            self.cpp_info.frameworks.extend(["CoreFoundation", "CoreServices", "IOKit"])
