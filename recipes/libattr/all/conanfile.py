from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
import os
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"

class LibAttrConan(ConanFile):
    name = "libattr"
    description = "Commands for Manipulating Filesystem Extended Attributes"
    topics = ("conan", "attr", "filesystem")
    license = "GPL-2.0-or-later"
    homepage = "https://savannah.nongnu.org/projects/attr/"
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
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _pkg_etc(self):
        return os.path.join(
            self.package_folder,
            "etc"
        )

    @property
    def _pkg_res(self):
        return os.path.join(
            self.package_folder,
            "res"
        )

    @property
    def _doc_folder(self):
        return os.path.join(
            self._source_subfolder,
            "doc"
        )

    def validate(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "libattr is just supported for Linux")

    def configure(self):
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True,
                  destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(
            self, win_bash=tools.os_info.is_windows)
        conf_args = [
            "--prefix={}".format(tools.microsoft.unix_path(self, self.package_folder)),
            "--bindir={}".format(tools.microsoft.unix_path(self, 
                os.path.join(self.package_folder, "bin"))),
            "--libdir={}".format(tools.microsoft.unix_path(self, 
                os.path.join(self.package_folder, "lib")))
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args)
        return self._autotools

    def build(self):
        with tools.files.chdir(self, self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.files.chdir(self, self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()
        tools.files.mkdir(self, self._pkg_res)
        tools.files.rename(self, 
            os.path.join(self._pkg_etc, "xattr.conf"),
            os.path.join(self._pkg_res, "xattr.conf")
        )
        self.copy("COPYING", dst="licenses", src=self._doc_folder)
        tools.files.rmdir(self, os.path.join(self.package_folder,"lib","pkgconfig"))
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "etc"))
        
    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libattr"
        self.cpp_info.names["cmake_find_package"] = "libattr"
        self.cpp_info.names["cmake_find_package_multi"] = "libattr"
        self.cpp_info.libs = ["attr"]
