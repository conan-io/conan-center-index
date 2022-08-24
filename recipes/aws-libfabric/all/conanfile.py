from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conan.errors import ConanInvalidConfiguration
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
    _providers = ["gni", "psm", "psm2", "sockets", "rxm", "tcp", "udp", "usnic", "verbs", "bgq", "shm", "efa", "rxd", "mrail", "rstream", "perf", "hook_debug"]
    options = {
        **{ p: [True, False, "shared"] for p in _providers },
        **{
            "shared": [True, False],
            "fPIC": [True, False],
            "with_libnl": [True, False],
            "bgq_progress": ["auto", "manual"],
            "bgq_mr": ["basic", "scalable"]
        }
    }
    default_options = {
        **{ p: False for p in _providers },
        **{
            "shared": False,
            "fPIC": True,
            "tcp": True,
            "with_libnl": False,
            "bgq_progress": "manual",
            "bgq_mr": "basic"
        }
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    _autotools = None

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        elif self.settings.os == "Linux":
            self.options.efa = True

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        if self.options.with_libnl:
            self.requires("libnl/3.2.25")

    def validate(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("The libfabric package cannot be built on Windows.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)

        yes_no_dl = lambda v: {"True": "yes", "False": "no", "shared": "dl"}[str(v)]
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--with-bgq-progress={}".format(self.options.bgq_progress),
            "--with-bgq-mr={}".format(self.options.bgq_mr),
        ]
        for p in self._providers:
            args.append("--enable-{}={}".format(p, yes_no_dl(getattr(self.options, p))))
        if self.options.with_libnl:
            args.append("--with-libnl={}".format(tools.unix_path(self.deps_cpp_info["libnl"].rootpath))),
        else:
            args.append("--with-libnl=no")
        if self.settings.build_type == "Debug":
            args.append("--enable-debug")
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
            if not self.options.shared:
                self.cpp_info.system_libs.extend(["dl", "rt"])
