from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os
import platform
import shutil
from contextlib import contextmanager


class LibffiConan(ConanFile):
    name = "libffi"
    description = "A portable, high level programming interface to various calling conventions"
    topics = ("conan", "libffi", "runtime", "foreign-function-interface", "runtime-library")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceware.org/libffi/"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = "patches/**"
    _autotools = None
    _source_subfolder = "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "{}-{}".format(self.name, self.version)
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        configure_path = os.path.join(self._source_subfolder, "configure")
        if self.settings.os == "Macos":
            tools.replace_in_file(configure_path, r"-install_name \$rpath/", "-install_name ")

        if self.settings.compiler == "clang" and float(str(self.settings.compiler.version)) >= 7.0:
            # https://android.googlesource.com/platform/external/libffi/+/ca22c3cb49a8cca299828c5ffad6fcfa76fdfa77
            sysv_s_src = os.path.join(self._source_subfolder, "src", "arm", "sysv.S")
            tools.replace_in_file(sysv_s_src, "fldmiad", "vldmia")
            tools.replace_in_file(sysv_s_src, "fstmiad", "vstmia")
            tools.replace_in_file(sysv_s_src, "fstmfdd\tsp!,", "vpush")

            # https://android.googlesource.com/platform/external/libffi/+/7748bd0e4a8f7d7c67b2867a3afdd92420e95a9f
            tools.replace_in_file(sysv_s_src, "stmeqia", "stmiaeq")
                
    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            if self.options.shared:
                del self.options.fPIC

    def configure(self):
        if self.settings.compiler != "Visual Studio":
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ:
            self.build_requires("msys2/20190524")

    @contextmanager
    def _build_context(self):
        extra_env_vars = {}
        if self.settings.compiler == "Visual Studio":
            self.package_folder = tools.unix_path(self.package_folder)
            msvcc = tools.unix_path(os.path.join(self.source_folder, self._source_subfolder, "msvcc.sh"))
            msvcc_args = []
            if self.settings.arch == "x86_64":
                msvcc_args.append("-m64")
            elif self.settings.arch == "x86":
                msvcc_args.append("-m32")
            if msvcc_args:
                msvcc = "{} {}".format(msvcc, " ".join(msvcc_args))
            extra_env_vars.update(tools.vcvars_dict(self.settings))
            extra_env_vars.update({
                "INSTALL": tools.unix_path(os.path.join(self.source_folder, self._source_subfolder, "install-sh")),
                "LIBTOOL": tools.unix_path(os.path.join(self.source_folder, self._source_subfolder, "ltmain.sh")),
                "CC": msvcc,
                "CXX": msvcc,
                "LD": "link",
                "CPP": "cl -nologo -EP",
                "CXXCPP": "cl -nologo -EP",
            })
        with tools.environment_append(extra_env_vars):
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        config_args = [
            "--enable-debug" if self.settings.build_type == "Debug" else "--disable-debug",
        ]
        if self.options.shared:
            config_args.extend(["--enable-shared", "--disable-static"])
        else:
            config_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.defines.append("FFI_BUILDING")
        if not self.options.shared:
            self._autotools.defines.append("FFI_STATIC")
        if self.settings.compiler == "Visual Studio":
            if "MT" in self.settings.compiler.runtime:
                self._autotools.defines.append("USE_STATIC_RTL")
            if "d" in self.settings.compiler.runtime:
                self._autotools.defines.append("USE_DEBUG_RTL")
        build = None
        host = None
        if self.settings.compiler == "Visual Studio":
            build = "{}-{}-{}".format(
                "x86_64" if "64" in platform.machine() else "i686",
                "pc" if self.settings.arch == "x86" else "w64",
                "cygwin")
            host = "{}-{}-{}".format(
                "x86_64" if self.settings.arch == "x86_64" else "i686",
                "pc" if self.settings.arch == "x86" else "w64",
                "cygwin")
        else:
            if self._autotools.host and "x86-" in self._autotools.host:
                self._autotools.host = self._autotools.host.replace("x86", "i686")
        self._autotools.configure(args=config_args, configure_dir=self._source_subfolder, build=build, host=host)
        return self._autotools

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()
            if tools.get_env("CONAN_RUN_TESTS", False):
                autotools.make(target="check")

    def package(self):
        self.copy("LICENSE", src=os.path.join(self.source_folder, self._source_subfolder), dst="licenses")
        if self.settings.os == "Windows":
            self.copy("*.h", src="{}/include".format(self.build_folder), dst="include")
        if self.settings.compiler == "Visual Studio":
            self.copy("*.lib", src="{}/.libs".format(self.build_folder), dst="lib")
            self.copy("*.dll", src="{}/.libs".format(self.build_folder), dst="bin")
        else:
            with self._build_context():
                autotools = self._configure_autotools()
                with tools.chdir(self.build_folder):
                    autotools.install()
            os.rename(os.path.join(self.package_folder, "lib", "libffi-{}".format(self.version), "include"),
                      os.path.join(self.package_folder, "include"))
            tools.rmdir(os.path.join(self.package_folder, "lib", "libffi-{}".format(self.version)))
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.rmdir(os.path.join(self.package_folder, "share"))

            os.unlink(os.path.join(self.package_folder, "lib", "libffi.la"))

    def package_info(self):
        if not self.options.shared:
            self.cpp_info.defines += ["FFI_STATIC"]
        self.cpp_info.libs = tools.collect_libs(self)
