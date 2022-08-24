from conan.tools.microsoft import msvc_runtime_flag
from conan import ConanFile, tools
from conans import AutoToolsBuildEnvironment
import contextlib
import os
import shutil

required_conan_version = ">=1.36"


class LibffiConan(ConanFile):
    name = "libffi"
    description = "A portable, high level programming interface to various calling conventions"
    topics = ("libffi", "runtime", "foreign-function-interface", "runtime-library")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://sourceware.org/libffi/"
    license = "MIT"

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

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        self.build_requires("gnu-config/cci.20201022")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        # Generate rpath friendly shared lib on macOS
        configure_path = os.path.join(self._source_subfolder, "configure")
        tools.files.replace_in_file(self, configure_path, "-install_name \\$rpath/", "-install_name @rpath/")

        if tools.scm.Version(self.version) < "3.3":
            if self.settings.compiler == "clang" and tools.scm.Version(str(self.settings.compiler.version)) >= 7.0:
                # https://android.googlesource.com/platform/external/libffi/+/ca22c3cb49a8cca299828c5ffad6fcfa76fdfa77
                sysv_s_src = os.path.join(self._source_subfolder, "src", "arm", "sysv.S")
                tools.files.replace_in_file(self, sysv_s_src, "fldmiad", "vldmia")
                tools.files.replace_in_file(self, sysv_s_src, "fstmiad", "vstmia")
                tools.files.replace_in_file(self, sysv_s_src, "fstmfdd\tsp!,", "vpush")

                # https://android.googlesource.com/platform/external/libffi/+/7748bd0e4a8f7d7c67b2867a3afdd92420e95a9f
                tools.files.replace_in_file(self, sysv_s_src, "stmeqia", "stmiaeq")

    @contextlib.contextmanager
    def _build_context(self):
        extra_env_vars = {}
        if tools.os_info.is_windows and (self._is_msvc or self.settings.compiler == "clang") :
            msvcc = tools.microsoft.unix_path(self, os.path.join(self.source_folder, self._source_subfolder, "msvcc.sh"))
            msvcc_args = []
            if self._is_msvc:
                if self.settings.arch == "x86_64":
                    msvcc_args.append("-m64")
                elif self.settings.arch == "x86":
                    msvcc_args.append("-m32")
            elif self.settings.compiler == "clang":
                msvcc_args.append("-clang-cl")

            if msvcc_args:
                msvcc = "{} {}".format(msvcc, " ".join(msvcc_args))
            extra_env_vars.update(tools.vcvars_dict(self.settings))
            extra_env_vars.update({
                "INSTALL": tools.microsoft.unix_path(self, os.path.join(self.source_folder, self._source_subfolder, "install-sh")),
                "LIBTOOL": tools.microsoft.unix_path(self, os.path.join(self.source_folder, self._source_subfolder, "ltmain.sh")),
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
        yes_no = lambda v: "yes" if v else "no"
        config_args = [
            "--enable-debug={}".format(yes_no(self.settings.build_type == "Debug")),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.defines.append("FFI_BUILDING")
        if self.options.shared:
            self._autotools.defines.append("FFI_BUILDING_DLL")
        if self._is_msvc:
            if "MT" in msvc_runtime_flag(self):
                self._autotools.defines.append("USE_STATIC_RTL")
            if "d" in msvc_runtime_flag(self):
                self._autotools.defines.append("USE_DEBUG_RTL")
        build = None
        host = None
        if self._is_msvc:
            build = "{}-{}-{}".format(
                "x86_64" if self._settings_build.arch == "x86_64" else "i686",
                "pc" if self._settings_build.arch == "x86" else "w64",
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
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
        shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))

        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()
            if tools.get_env("CONAN_RUN_TESTS", False):
                autotools.make(target="check")

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        if self._is_msvc:
            if self.options.shared:
                self.copy("libffi.dll", src=".libs", dst="bin")
            self.copy("libffi.lib", src=".libs", dst="lib")
            self.copy("*.h", src="include", dst="include")
        else:
            with self._build_context():
                autotools = self._configure_autotools()
                autotools.install()

            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
            tools.files.rm(self, "*.la", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "libffi")
        self.cpp_info.libs = ["{}ffi".format("lib" if self._is_msvc else "")]
        if not self.options.shared:
            self.cpp_info.defines = ["FFI_BUILDING"]

