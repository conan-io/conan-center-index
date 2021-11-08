from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import conan.tools.files
from contextlib import contextmanager
import os

required_conan_version = ">=1.33"

class NsprConan(ConanFile):
    name = "nspr"
    homepage = "https://developer.mozilla.org/en-US/docs/Mozilla/Projects/NSPR"
    description = "Netscape Portable Runtime (NSPR) provides a platform-neutral API for system level and libc-like functions."
    topics = ("conan", "nspr", "libc")
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "compiler", "arch", "build_type"
    license = "MPL-2.0"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_mozilla": [True, False],
        "win32_target": ["winnt", "win95"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_mozilla": True,
        "win32_target": "winnt",
    }
    generators = "cmake"

    _autotools = None

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx
        if self.options.shared:
            del self.options.fPIC
    
    def validate(self):
        # https://bugzilla.mozilla.org/show_bug.cgi?id=1658671
        if tools.Version(self.version) < "4.29":
            if self.settings.os == "Macos" and self.settings.arch == "armv8":
                raise ConanInvalidConfiguration("NSPR does not support mac M1 before 4.29")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  strip_root=True)
        conan.tools.files.rename(self, "nspr", self._source_subfolder)

    def build_requirements(self):
        if self._settings_build.os == "Windows" :
            self.build_requires("mozilla-build/3.3")
            if not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                with tools.environment_append({"CC": "cl", "CXX": "cl", "LD": "link"}):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        conf_args = [
            "--with-mozilla" if self.options.with_mozilla else "--without-mozilla",
            "--disable-cplus",
            "--enable-64bit" if self.settings.arch in ("armv8", "x86_64") else "--disable-64bit",
            "--disable-strip" if self.settings.build_type == "RelWithDebInfo" else "--enable-strip",
            "--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug",
        ]
        if self.settings.compiler == "Visual Studio":
            conf_args.extend([
                "{}-pc-mingw32".format("x86_64" if self.settings.arch == "x86_64" else "x86"),
                "--enable-static-rtl" if "MT" in str(self.settings.compiler.runtime) else "--disable-static-rtl",
                "--enable-debug-rtl" if "d" in str(self.settings.compiler.runtime) else "--disable-debug-rtl",
            ])
        elif self.settings.os == "Android":
            conf_args.extend([
                "--with-android-ndk={}".format(os.environ["NDK_ROOT"]),
                "--with-android-version={}".format(self.settings.os.api_level),
                "--with-android-platform={}".format(os.environ["ANDROID_PLATFORM"]),
                "--with-android-toolchain={}".format(os.environ["ANDROID_TOOLCHAIN"]),
            ])
        elif self.settings.os == "Windows":
            conf_args.append("--enable-win32-target={}".format(self.options.win32_target))
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        env = self._autotools.vars
        if self.settings.os == "Macos":
            if self.settings.arch == "armv8":
                # conan adds `-arch`, which conflicts with nspr's apple silicon support
                env["CFLAGS"] = env["CFLAGS"].replace("-arch arm64", "")
                env["CXXFLAGS"] = env["CXXFLAGS"].replace("-arch arm64", "")

        self._autotools.configure(args=conf_args, vars=env)
        return self._autotools

    def build(self):
        with tools.chdir(self._source_subfolder):
            with self._build_context():
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        with tools.chdir(self._source_subfolder):
            with self._build_context():
                autotools = self._configure_autotools()
                autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "bin"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        if self.settings.os == "Windows":
            if self.options.shared:
                os.mkdir(os.path.join(self.package_folder, "bin"))
            for lib in self._library_names:
                libsuffix = "lib" if self.settings.compiler == "Visual Studio" else "a"
                libprefix = "" if self.settings.compiler == "Visual Studio" else "lib"
                if self.options.shared:
                    os.unlink(os.path.join(self.package_folder, "lib", "{}{}_s.{}".format(libprefix, lib, libsuffix)))
                    os.rename(os.path.join(self.package_folder, "lib", "{}.dll".format(lib)),
                              os.path.join(self.package_folder, "bin", "{}.dll".format(lib)))
                else:
                    os.unlink(os.path.join(self.package_folder, "lib", "{}{}.{}".format(libprefix, lib, libsuffix)))
                    os.unlink(os.path.join(self.package_folder, "lib", "{}.dll".format(lib)))
            if not self.options.shared:
                tools.replace_in_file(os.path.join(self.package_folder, "include", "nspr", "prtypes.h"),
                                      "#define NSPR_API(__type) PR_IMPORT(__type)",
                                      "#define NSPR_API(__type) extern __type")
                tools.replace_in_file(os.path.join(self.package_folder, "include", "nspr", "prtypes.h"),
                                      "#define NSPR_DATA_API(__type) PR_IMPORT_DATA(__type)",
                                      "#define NSPR_DATA_API(__type) extern __type")
        else:
            shared_ext = "dylib" if self.settings.os == "Macos" else "so"
            for lib in self._library_names:
                if self.options.shared:
                    os.unlink(os.path.join(self.package_folder, "lib", "lib{}.a".format(lib)))
                else:
                    os.unlink(os.path.join(self.package_folder, "lib", "lib{}.{}".format(lib, shared_ext)))

        if self.settings.compiler == "Visual Studio":
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
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.extend(["dl", "pthread"])
        elif self.settings.os == "Windows":
            self.cpp_info.system_libs.extend(["winmm", "ws2_32"])
