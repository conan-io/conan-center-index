from conans import ConanFile, tools, AutoToolsBuildEnvironment
import os
from conans.errors import ConanInvalidConfiguration


class LibACLConan(ConanFile):
    name = "libacl"
    description = "Commands for Manipulating POSIX Access Control Lists"
    topics = ("conan", "acl", "POSIX", "access controll")
    license = "MIT"
    homepage = "https://savannah.nongnu.org/projects/acl"
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
    requires = ["libattr/2.4.48"]
    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_folder(self):
        return "build"

    def config_options(self):
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration(
                "libacl is just supported for Linux")

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

        self._autotools.configure(
            args=conf_args, use_default_install_dirs=False)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        with tools.chdir(self._source_subfolder):
            autotools = self._configure_autotools()
            autotools.install()            
        #tools.rename(
        #    os.path.join(self._pkg_etc, "xattr.conf"),
        #    os.path.join(self._pkg_lib, "xattr.conf")
        #)
        #tools.rmdir(os.path.join(self.package_folder, "share"))
        #tools.rmdir(os.path.join(self.package_folder, "etc"))      

    def package_id(self):
        pass 
        #self.cpp_info.names["cmake_find_package"] = "LibACL"
        #self.cpp_info.names["cmake_find_package_multi"] = "LibACL"
        #self.cpp_info.libs = tools.collect_libs(self)
