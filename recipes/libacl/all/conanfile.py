from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class LibAclConan(ConanFile):
    name = "libacl"
    description = "Commands for Manipulating POSIX Access Control Lists"
    topics = ("conan", "acl", "POSIX")
    license = "GPL-2.0-or-later"
    homepage = "https://savannah.nongnu.org/projects/acl/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }
    requires = ["libattr/2.5.1"]
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _doc_folder(self):
        return os.path.join(
            self._source_subfolder,
            "doc"
        )

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libacl is just supported for Linux")

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--prefix={}".format(tools.unix_path(self.package_folder)),
            "--bindir={}".format(tools.unix_path(
                os.path.join(self.package_folder, "bin"))),
            "--libdir={}".format(tools.unix_path(
                os.path.join(self.package_folder, "lib")))
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        self.copy("COPYING", dst="licenses", src=self._doc_folder)
        tools.rmdir(os.path.join(self.package_folder,"lib","pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
        tools.rmdir(os.path.join(self.package_folder, "share"))
        
    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libacl"
        self.cpp_info.libs = ["acl"]
