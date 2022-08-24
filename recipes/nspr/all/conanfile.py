from conan.tools.microsoft import msvc_runtime_flag
from conan.tools.files import rename
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conan.errors import ConanInvalidConfiguration
import contextlib
import functools
import os

required_conan_version = ">=1.36.0"


class NsprConan(ConanFile):
    name = "nspr"
    homepage = "https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSPR"
    description = "Netscape Portable Runtime (NSPR) provides a platform-neutral API for system level and libc-like functions."
    topics = ("nspr", "libc")
    url = "https://github.com/conan-io/conan-center-index"
    license = "MPL-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mozilla": [True, False],
        "win32_target": ["winnt", "win95"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_mozilla": True,
        "win32_target": "winnt",
    }

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.win32_target

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def validate(self):
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1658671
        if tools.Version(self.version) < "4.29":
            if self.settings.os == "Macos" and self.settings.arch == "armv8":
                raise ConanInvalidConfiguration("NSPR does not support mac M1 before 4.29")

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            self.build_requires("mozilla-build/3.3")
            if not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination="tmp", strip_root=True)
        rename(self, os.path.join("tmp", "nspr"), self._source_subfolder)
        tools.files.rmdir(self, "tmp")

    @contextlib.contextmanager
    def _build_context(self):
        if self._is_msvc:
            with tools.vcvars(self):
                with tools.environment_append({"CC": "cl", "CXX": "cl", "LD": "link"}):
                    yield
        else:
            yield

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        conf_args = [
            "--with-mozilla={}".format(yes_no(self.options.with_mozilla)),
            "--enable-64bit={}".format(yes_no(self.settings.arch in ("armv8", "x86_64", "mips64", "ppc64", "ppc64le"))),
            "--enable-strip={}".format(yes_no(self.settings.build_type not in ("Debug", "RelWithDebInfo"))),
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--datarootdir={}".format(tools.unix_path(os.path.join(self.package_folder, "res"))),
            "--disable-cplus",
        ]
        if self._is_msvc:
            conf_args.extend([
                "{}-pc-mingw32".format("x86_64" if self.settings.arch == "x86_64" else "x86"),
                "--enable-static-rtl={}".format(yes_no("MT" in msvc_runtime_flag(self))),
                "--enable-debug-rtl={}".format(yes_no("d" in msvc_runtime_flag(self))),
            ])
        elif self.settings.os == "Android":
            conf_args.extend([
                "--with-android-ndk={}".format(tools.get_env(["NDK_ROOT"])),
                "--with-android-version={}".format(self.settings.os.api_level),
                "--with-android-platform={}".format(tools.get_env("ANDROID_PLATFORM")),
                "--with-android-toolchain={}".format(tools.get_env("ANDROID_TOOLCHAIN")),
            ])
        elif self.settings.os == "Windows":
            conf_args.append("--enable-win32-target={}".format(self.options.win32_target))
        env = autotools.vars
        if self.settings.os == "Macos":
            if self.settings.arch == "armv8":
                # conan adds `-arch`, which conflicts with nspr's apple silicon support
                env["CFLAGS"] = env["CFLAGS"].replace("-arch arm64", "")
                env["CXXFLAGS"] = env["CXXFLAGS"].replace("-arch arm64", "")

        autotools.configure(args=conf_args, vars=env)
        return autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            # relocatable shared libs on macOS
            tools.files.replace_in_file(self, 
                "configure",
                "-install_name @executable_path/",
                "-install_name @rpath/"
            )
            with self._build_context():
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            with self._build_context():
                autotools = self._configure_autotools()
                autotools.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "bin"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows":
            if self.options.shared:
                os.mkdir(os.path.join(self.package_folder, "bin"))
            for lib in self._library_names:
                libsuffix = "lib" if self._is_msvc else "a"
                libprefix = "" if self._is_msvc else "lib"
                if self.options.shared:
                    os.unlink(os.path.join(self.package_folder, "lib", "{}{}_s.{}".format(libprefix, lib, libsuffix)))
                    rename(self, os.path.join(self.package_folder, "lib", "{}.dll".format(lib)),
                                 os.path.join(self.package_folder, "bin", "{}.dll".format(lib)))
                else:
                    os.unlink(os.path.join(self.package_folder, "lib", "{}{}.{}".format(libprefix, lib, libsuffix)))
                    os.unlink(os.path.join(self.package_folder, "lib", "{}.dll".format(lib)))
            if not self.options.shared:
                tools.files.replace_in_file(self, os.path.join(self.package_folder, "include", "nspr", "prtypes.h"),
                                      "#define NSPR_API(__type) PR_IMPORT(__type)",
                                      "#define NSPR_API(__type) extern __type")
                tools.files.replace_in_file(self, os.path.join(self.package_folder, "include", "nspr", "prtypes.h"),
                                      "#define NSPR_DATA_API(__type) PR_IMPORT_DATA(__type)",
                                      "#define NSPR_DATA_API(__type) extern __type")
        else:
            shared_ext = "dylib" if self.settings.os == "Macos" else "so"
            for lib in self._library_names:
                if self.options.shared:
                    os.unlink(os.path.join(self.package_folder, "lib", "lib{}.a".format(lib)))
                else:
                    os.unlink(os.path.join(self.package_folder, "lib", "lib{}.{}".format(lib, shared_ext)))

        if self._is_msvc:
            if self.settings.build_type == "Debug":
                for lib in self._library_names:
                    os.unlink(os.path.join(self.package_folder, "lib", "{}.pdb".format(lib)))

        if not self.options.shared or self.settings.os == "Windows":
            for f in os.listdir(os.path.join(self.package_folder, "lib")):
                os.chmod(os.path.join(self.package_folder, "lib", f), 0o644)

    @property
    def _library_names(self):
        return ["plds4", "plc4", "nspr4"]

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "nspr")
        libs = self._library_names
        if self.settings.os == "Windows" and not self.options.shared:
            libs = list("{}_s".format(l) for l in libs)
        self.cpp_info.libs = libs
        if self.settings.compiler == "gcc" and self.settings.os == "Windows":
            if self.settings.arch == "x86":
                self.cpp_info.defines.append("_M_IX86")
            elif self.settings.arch == "x86_64":
                self.cpp_info.defines.append("_M_X64")
        self.cpp_info.includedirs.append(os.path.join("include", "nspr"))
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winmm", "ws2_32"])

        aclocal = tools.unix_path(os.path.join(self.package_folder, "res", "aclocal"))
        self.output.info("Appending AUTOMAKE_CONAN_INCLUDES environment variable: {}".format(aclocal))
        self.env_info.AUTOMAKE_CONAN_INCLUDES.append(aclocal)

        self.cpp_info.resdirs = ["res"]
