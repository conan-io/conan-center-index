from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.35.0"

class LibfabricConan(ConanFile):
    name = "libfabric"
    description = "Open Fabric Interfaces"
    topics = ("conan", "fabric")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://libfabric.org"
    license = "BSD"
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

    def configure(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("The libfabric package cannot be built on Visual Studio.")
        for p in self._providers:
            if self.options.get_safe(p) not in ["auto", "yes", "no", "dl"] and not os.path.isdir(str(self.options.get_safe(p))):
                raise ConanInvalidConfiguration("Option {} can only be one of 'auto', 'yes', 'no', 'dl' or a directory path")
        if self.options.get_safe('with_libnl') and not os.path.isdir(str(self.options.with_libnl)):
            raise ConanInvalidConfiguration("Value of with_libnl must be an existing directory")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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
        self.copy(pattern="COPYING", dst="licenses", src=os.path.join(self._source_subfolder, "blob", "main"))
        autotools = self._configure_autotools()
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = self.collect_libs()
