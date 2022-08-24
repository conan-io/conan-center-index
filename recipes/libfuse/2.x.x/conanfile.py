from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"

class LibfuseConan(ConanFile):
    name = "libfuse"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libfuse/libfuse"
    license = "LGPL-2.1"
    description = "The reference implementation of the Linux FUSE interface"
    topics = ("fuse", "libfuse", "filesystem", "linux")
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

    def validate(self):
        if self.settings.os not in ("Linux", "FreeBSD"):
            raise ConanInvalidConfiguration("libfuse supports only Linux and FreeBSD")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-lib",
            "--disable-util",
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING*", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()
        tools.files.rm(self, self.package_folder, "*.la")
        # remove ulockmgr stuff lib and header file
        tools.files.rm(self, self.package_folder, "*ulockmgr*")
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))


    def package_info(self):
        self.cpp_info.libs = ["fuse"]
        self.cpp_info.includedirs = [os.path.join("include", "fuse")]
        self.cpp_info.names["pkg_config"] = "fuse"
        self.cpp_info.system_libs = ["pthread"]
        # libfuse requires this define to compile successfully
        self.cpp_info.defines = ["_FILE_OFFSET_BITS=64"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("dl")

