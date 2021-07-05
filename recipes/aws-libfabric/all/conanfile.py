from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.35.0"

class LibfabricConan(ConanFile):
    name = "aws-libfabric"
    description = "AWS Libfabric"
    topics = ("fabric", "communication", "framework", "service")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/aws/libfabric"
    license = "BSD-2-Clause", "GPL-2.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    _providers = ['gni', 'psm', 'psm2', 'sockets', 'rxm', 'tcp', 'udp', 'usnic', 'verbs', 'bgq', 'shm', 'efa', 'rxd', 'mrail', 'rstream', 'perf', 'hook_debug']
    options = {
        **{ p: "ANY" for p in _providers },
        **{
            "shared": [True, False],
            "fPIC": [True, False],
            "with_libnl": [True, False],
            "with_bgq_progress": [None, "auto", "manual"],
            "with_bgq_mr": [None, "basic", "scalable"]
        }
    }
    default_options = {
        **{ p: "auto" for p in _providers if p not in ('efa', 'verbs', 'rxd') },
        **{
            "shared": False,
            "fPIC": True,
            "efa": "yes",
            "verbs": "no",
            "rxd": "no",
            "with_libnl": False,
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

    def requirements(self):
        if self.options.get_safe('with_libnl'):
            self.requires('libnl/3.2.25')

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            raise ConanInvalidConfiguration("The libfabric package cannot be built on Visual Studio.")
        for p in self._providers:
            if self.options.get_safe(p) not in ["auto", "yes", "no", "dl"] and not os.path.isdir(str(self.options.get_safe(p))):
                raise ConanInvalidConfiguration("Option {} can only be one of 'auto', 'yes', 'no', 'dl' or a directory path")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        with tools.chdir(self._source_subfolder):
            self.run("./autogen.sh", win_bash=tools.os_info.is_windows)
        args = []
        for p in self._providers:
            args.append('--enable-{}={}'.format(p, self.options.get_safe(p)))
        if self.options.with_libnl:
            args.append('--with-libnl={}'.format(self.deps_cpp_info["libnl"].rootpath))
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

        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libfabric"
        self.cpp_info.libs = self.collect_libs()
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread", "m"]
