from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.35.0"

class LibfabricConan(ConanFile):
    name = "libfabric"
    description = "Open Fabric Interfaces"
    topics = ("fabric", "communication", "framework", "service")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libfabric.org"
    license = "BSD-2-Clause", "GPL-2.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    _providers = ['gni', 'psm', 'psm2', 'psm3', 'rxm', 'sockets', 'tcp', 'udp', 'usnic', 'verbs', 'bgq']
    options = {
        **{ p: "ANY" for p in _providers },
        **{
            "shared": [True, False],
            "fPIC": [True, False],
            "with_libnl": "ANY",
            "with_bgq_progress": [None, "auto", "manual"],
            "with_bgq_mr": [None, "basic", "scalable"]
        }
    }
    default_options = {
        **{ p: "auto" for p in _providers },
        **{
            "shared": False,
            "fPIC": True,
            "with_libnl": None,
            "with_bgq_progress": None,
            "with_bgq_mr": None
        }
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _autotools = None

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.os not in ["Linux", "FreeBSD", "Macos"]:
            raise ConanInvalidConfiguration("libfabric only builds on Linux, Macos, and FreeBSD.")
        for p in self._providers:
            if self.options.get_safe(p) not in ["auto", "yes", "no", "dl"] and not os.path.isdir(str(self.options.get_safe(p))):
                raise ConanInvalidConfiguration("Option {} can only be one of 'auto', 'yes', 'no', 'dl' or a directory path")
        if self.options.get_safe('with_libnl') and not os.path.isdir(str(self.options.with_libnl)):
            raise ConanInvalidConfiguration("Value of with_libnl must be an existing directory")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        args = []
        for p in self._providers:
            args.append('--enable-{}={}'.format(p, self.options.get_safe(p)))
        if self.options.with_libnl:
            args.append('--with-libnl={}'.format(self.options.with_libnl))
        if self.options.with_bgq_progress:
            args.append('--with-bgq-progress={}'.format(self.options.with_bgq_progress))
        if self.options.with_bgq_mr:
            args.append('--with-bgq-mr={}'.format(self.options.with_bgq_mr))
        self._autotools.configure(args=args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        autotools = self._configure_autotools()
        autotools.install()

        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rm(self, os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libfabric"
        self.cpp_info.libs = self.collect_libs()
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
