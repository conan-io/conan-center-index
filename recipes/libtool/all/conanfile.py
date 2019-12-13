import os
from conans import AutoToolsBuildEnvironment, ConanFile, tools


class LibtoolConan(ConanFile):
    name = "libtool"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gnu.org/software/libtool/"
    description = "GNU libtool is a generic library support script. "
    topics = ("conan", "libtool", "configure", "library", "shared", "static")
    exports_sources = ["patches/**"]
    license = ("GPL-2.0-or-later", "GPL-3.0-or-later")

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
        return os.path.join(self.source_folder, "source_subfolder")

    def config_options(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20190524")

    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--datarootdir={}".format(os.path.join(self.package_folder, "bin", "share").replace("\\", "/")),
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
            if self.settings.os != "Windows":
                conf_args.append("--enable-pic" if self.options.fPIC else "--disable-pic")
        autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING*", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libltdl.la"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "info"))
        tools.rmdir(os.path.join(self.package_folder, "bin", "share", "man"))

    def package_info(self):
        self.cpp_info.libs = ["ltdl"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        libtool = os.path.join(self.package_folder, "bin", "libtool")
        self.output.info("Setting LIBTOOL to {}".format(libtool))
        self.env_info.LIBTOOL = libtool

        libtoolize = os.path.join(self.package_folder, "bin", "libtoolize")
        self.output.info("Setting LIBTOOLIZE to {}".format(libtoolize))
        self.env_info.LIBTOOLIZE = libtoolize

        libtool_aclocal = os.path.join(self.package_folder, "bin", "share", "aclocal")
        self.output.info("Appending var to ACLOCAL_PATH: {}".format(libtool_aclocal))
        self.env_info.ACLOCAL_PATH.append(libtool_aclocal)
