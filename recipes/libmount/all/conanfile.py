from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os


class LibmountConan(ConanFile):
    name = "libmount"
    description = "The libmount library is used to parse /etc/fstab, /etc/mtab and /proc/self/mountinfo files, manage the mtab file, evaluate mount options, etc"
    topics = ("conan", "mount", "libmount", "linux", "util-linux")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://git.kernel.org/pub/scm/utils/util-linux/util-linux.git"
    license = "GPL-2.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _autotools = None

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("only Linux is supported")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "util-linux-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_autotools(self):
        if not self._autotools:
            args = ["--disable-all-programs", "--enable-libmount", "--enable-libblkid"]
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--enable-static"])
            self._autotools = AutoToolsBuildEnvironment(self)
            self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            env_build = self._configure_autotools()
            env_build.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            env_build = self._configure_autotools()
            env_build.install()
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "sbin"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        os.remove(os.path.join(self.package_folder, "lib", "libblkid.la"))
        os.remove(os.path.join(self.package_folder, "lib", "libmount.la"))

    def package_info(self):
        self.cpp_info.libs = ["mount", "blkid"]
        self.cpp_info.includedirs.append(os.path.join("include", "libmount"))
        self.cpp_info.set_property("pkg_config_name", "mount")
