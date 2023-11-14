import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.files import chdir, copy, get, rmdir
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class XtrConan(ConanFile):
    name = "xtr"
    description = "C++ Logging Library for Low-latency or Real-time Environments"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/choll/xtr"
    topics = ("logging", "logger")

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_exceptions": [True, False],
        "enable_lto": [True, False],
        "enable_io_uring": ["auto", True, False],
        "enable_io_uring_sqpoll": [True, False],
        "sink_capacity_kb": [None, "ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_exceptions": True,
        "enable_lto": False,
        "enable_io_uring": "auto",
        "enable_io_uring_sqpoll": False,
        "sink_capacity_kb": None,
    }

    def config_options(self):
        if Version(self.version) < "1.0.1":
            self.options.rm_safe("sink_capacity_kb")
        if Version(self.version) < "2.0.0":
            self.options.rm_safe("enable_io_uring")
            self.options.rm_safe("enable_io_uring_sqpoll")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        # INFO: https://github.com/choll/xtr/blob/2.1.0/include/xtr/detail/buffer.hpp#L27
        self.requires("fmt/10.1.1", transitive_headers=True, transitive_libs=True)
        # Require liburing on any Linux system as a run-time check will be
        # done to detect if the host kernel supports io_uring.
        if (
            Version(self.version) >= "2.0.0"
            and self.settings.os in ["Linux", "FreeBSD"]
            and self.options.get_safe("enable_io_uring")
        ):
            self.requires("liburing/2.4")

    def validate(self):
        if self.settings.os not in ("FreeBSD", "Linux"):
            raise ConanInvalidConfiguration(f"Unsupported os={self.settings.os}")
        if self.settings.compiler not in ("gcc", "clang"):
            raise ConanInvalidConfiguration(f"Unsupported compiler={self.settings.compiler}")
        if self.settings.arch not in ("x86_64",):
            raise ConanInvalidConfiguration(f"Unsupported arch={self.settings.arch}")
        if (
            Version(self.version) < "2.0.0"
            and self.settings.compiler == "clang"
            and self.settings.compiler.libcxx == "libc++"
        ):
            raise ConanInvalidConfiguration(f"Use at least version 2.0.0 for libc++ compatibility")
        if self.options.get_safe("enable_io_uring_sqpoll") and not self.options.get_safe("enable_io_uring"):
            raise ConanInvalidConfiguration(f"io_uring must be enabled if io_uring_sqpoll is enabled")
        if (
            self.options.get_safe("sink_capacity_kb")
            and not str(self.options.get_safe("sink_capacity_kb")).isdigit()
        ):
            raise ConanInvalidConfiguration(f"The option 'sink_capacity_kb' must be an integer")

        minimal_cpp_standard = 20
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, minimal_cpp_standard)

        minimum_version = {"gcc": 10, "clang": 12}
        compiler = str(self.settings.compiler)
        version = Version(self.settings.compiler.version)

        if version < minimum_version[compiler]:
            raise ConanInvalidConfiguration(
                f"{self.name} requires {self.settings.compiler} version {minimum_version[compiler]} or later"
            )

        if Version(self.dependencies["fmt"].ref.version) < 6:
            raise ConanInvalidConfiguration("The version of fmt must be >= 6.0.0")
        if Version(self.dependencies["fmt"].ref.version) == "8.0.0" and self.settings.compiler == "clang":
            raise ConanInvalidConfiguration(
                "fmt/8.0.0 is known to not work with clang (https://github.com/fmtlib/fmt/issues/2377)"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _get_defines(self):
        defines = []
        enable_io_uring = self.options.get_safe("enable_io_uring")
        if enable_io_uring in (True, False):
            defines += [f"XTR_USE_IO_URING={int(bool(enable_io_uring))}"]
        if self.options.get_safe("enable_io_uring_sqpoll"):
            defines += ["XTR_IO_URING_POLL=1"]
        capacity = self.options.get_safe("sink_capacity_kb")
        if capacity:
            defines += [f"XTR_SINK_CAPACITY={int(capacity) * 1024}"]
        return defines

    def generate(self):
        deps = AutotoolsDeps(self)
        deps.generate()

        tc = AutotoolsToolchain(self)
        tc.make_args += [
            f"EXCEPTIONS={int(bool(self.options.enable_exceptions))}",
            f"LTO={int(bool(self.options.enable_lto))}",
            f"LDLIBS={deps.vars()['LIBS']}",
        ]
        tc.extra_defines = self._get_defines()
        tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            autotools = Autotools(self)
            autotools.make()
            # FIXME: xtrctl fails to compile with
            # undefined reference to 'xtr::detail::file_descriptor::~file_descriptor()'
            # autotools.make(target="xtrctl")

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*.hpp",
             src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "*/libxtr.a",
             src=os.path.join(self.source_folder, "build"),
             dst=os.path.join(self.package_folder, "lib"),
             keep_path=False)
        # copy(self, "*/xtrctl",
        #      src=os.path.join(self.source_folder, "build"),
        #      dst=os.path.join(self.package_folder, "bin"),
        #      keep_path=False)

        rmdir(self, os.path.join(self.package_folder, "man"))

    def package_info(self):
        self.cpp_info.libs = ["xtr"]
        self.cpp_info.system_libs = ["pthread"]
        self.cpp_info.defines = self._get_defines()

        # TODO: Legacy, to be removed on Conan 2.0
        bin_path = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bin_path)
