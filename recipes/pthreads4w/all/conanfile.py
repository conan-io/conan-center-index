from conan import ConanFile
from conan.tools.files import chdir, collect_libs, copy, get, mkdir, replace_in_file
from conan.tools.gnu import AutotoolsToolchain, Autotools
from conan.tools.layout import basic_layout
from conan.tools.microsoft import is_msvc, NMakeToolchain
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.57.0"

class Pthreads4WConan(ConanFile):
    name = "pthreads4w"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceforge.net/projects/pthreads4w/"
    description = "POSIX Threads for Windows"
    license = "Apache-2.0"
    topics = ("pthreads", "windows", "posix")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "exception_scheme": ["CPP", "SEH", "default"],
    }
    default_options = {
        "shared": False,
        "exception_scheme": "default",
    }

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def configure(self):
        self.settings.rm_safe("compiler.libcxx")
        self.settings.rm_safe("compiler.cppstd")

    def build_requirements(self):
        if not is_msvc(self):
            self.build_requires("autoconf/2.71")
            if self._settings_build.os == "Windows":
                self.win_bash = True
                if not self.conf.get("tools.microsoft.bash:path", check_type=str):
                    self.tool_requires("msys2/cci.latest")

    def validate(self):
        if self.settings.os != "Windows":
            raise ConanInvalidConfiguration("pthreads4w can only target os=Windows")
        
    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        if is_msvc(self):
            tc = NMakeToolchain(self)
            tc.generate()
        else:
            tc = AutotoolsToolchain(self)
            tc.generate()

    def build(self):
        with chdir(self, self.source_folder):
            if is_msvc(self):
                makefile = os.path.join(self.source_folder, "Makefile")
                replace_in_file(self, makefile,
                    "	copy pthreadV*.lib $(LIBDEST)",
                    "	if exist pthreadV*.lib copy pthreadV*.lib $(LIBDEST)")
                replace_in_file(self, makefile,
                    "	copy libpthreadV*.lib $(LIBDEST)",
                    "	if exist libpthreadV*.lib copy libpthreadV*.lib $(LIBDEST)")
                replace_in_file(self, makefile, "XCFLAGS=\"/MD\"", "")
                replace_in_file(self, makefile, "XCFLAGS=\"/MDd\"", "")
                replace_in_file(self, makefile, "XCFLAGS=\"/MT\"", "")
                replace_in_file(self, makefile, "XCFLAGS=\"/MTd\"", "")
                target = {
                    "CPP": "VCE",
                    "SEH": "SSE",
                }.get(str(self.options.exception_scheme), "VC")
                if not self.options.shared:
                    target += "-static"
                if self.settings.build_type == "Debug":
                    target += "-debug"

                self.run(f"nmake {target}")
            else:
                autotools = Autotools(self)
                self.run("autoheader")
                autotools.autoreconf()
                autotools.configure()

                make_target = "GCE" if self.options.exception_scheme == "CPP" else "GC"
                if not self.options.shared:
                    make_target += "-static"
                if self.settings.build_type == "Debug":
                    make_target += "-debug"
                autotools.make(target=make_target, args=["-j1"])

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        with chdir(self, self.source_folder):
            if is_msvc(self):
                self.run("nmake install DESTROOT={}".format(self.package_folder), env="conanbuild")
            else:
                autotools = Autotools(self)
                mkdir(self, os.path.join(self.package_folder, "include"))
                mkdir(self, os.path.join(self.package_folder, "lib"))
                autotools.install(target="install-headers")
                if self.options.shared:
                    mkdir(self, os.path.join(self.package_folder, "bin"))
                    autotools.install(target="install-dlls")
                    autotools.install(target="install-implib-default")
                else:
                    autotools.install(target="install-lib-default")

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
        self.cpp_info.defines.append(self._exception_scheme_definition)
        if not self.options.shared:
            self.cpp_info.defines.append("__PTW32_STATIC_LIB")

    @property
    def _exception_scheme_definition(self):
        return {
            "CPP": "__PTW32_CLEANUP_CXX",
            "SEH": "__PTW32_CLEANUP_SEH",
            "default": "__PTW32_CLEANUP_C",
        }[str(self.options.exception_scheme)]
