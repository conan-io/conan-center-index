from conan.tools.files import rename
from conans import ConanFile, tools, AutoToolsBuildEnvironment
import contextlib
import os

required_conan_version = ">=1.38.0"


class LibX264Conan(ConanFile):
    name = "libx264"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.videolan.org/developers/x264.html"
    description = "x264 is a free software library and application for encoding video streams into the " \
                  "H.264/MPEG-4 AVC compression format"
    topics = ("libx264", "video", "encoding")
    license = "GPL-2.0"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "bit_depth": [8, 10, "all"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "bit_depth": "all",
    }

    _autotools = None
    _override_env = {}

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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @property
    def _with_nasm(self):
        return self.settings.arch in ("x86", "x86_64")

    def build_requirements(self):
        if self._with_nasm:
            self.build_requires("nasm/2.15.05")
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @contextlib.contextmanager
    def _build_context(self):
        with tools.vcvars(self) if self._is_msvc else tools.no_op():
            yield

    @property
    def env(self):
        ret = super(LibX264Conan, self).env
        ret.update(self._override_env)
        return ret

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []
        extra_asflags = []
        extra_cflags = []
        extra_ldflags = []
        args = [
            "--bit-depth=%s" % str(self.options.bit_depth),
            "--disable-cli",
            "--prefix={}".format(tools.unix_path(self.package_folder)),
        ]
        if self.options.shared:
            args.append("--enable-shared")
        else:
            args.append("--enable-static")
        if self.options.get_safe("fPIC", self.settings.os != "Windows"):
            args.append("--enable-pic")
        if self.settings.build_type == "Debug":
            args.append("--enable-debug")
        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # bitstream-a.S:29:18: error: unknown token in expression
            extra_asflags.append("-arch arm64")
            extra_ldflags.append("-arch arm64")
            args.append("--host=aarch64-apple-darwin")

        if self._with_nasm:
            # FIXME: get using user_build_info
            self._override_env["AS"] = os.path.join(self.dependencies.build["nasm"].package_folder, "bin", "nasm{}".format(".exe" if tools.os_info.is_windows else "")).replace("\\", "/")
        if tools.cross_building(self):
            if self.settings.os == "Android":
                # the as of ndk does not work well for building libx264
                self._override_env["AS"] = os.environ["CC"]
                ndk_root = tools.unix_path(os.environ["NDK_ROOT"])
                arch = {
                    "armv7": "arm",
                    "armv8": "aarch64",
                    "x86": "i686",
                    "x86_64": "x86_64",
                }.get(str(self.settings.arch))
                abi = "androideabi" if self.settings.arch == "armv7" else "android"
                args.append("--cross-prefix={}".format("{}/bin/{}-linux-{}-".format(ndk_root, arch, abi)))
        if self._is_msvc:
            self._override_env["CC"] = "cl -nologo"
            extra_cflags.extend(self._autotools.flags)
            if not (self.settings.compiler == "Visual Studio" and tools.Version(self.settings.compiler.version) < "12"):
                extra_cflags.append("-FS")
        build_canonical_name = None
        host_canonical_name = None
        if self._is_msvc:
            # autotools does not know about the msvc canonical name(s)
            build_canonical_name = False
            host_canonical_name = False
        if extra_asflags:
            args.append("--extra-asflags={}".format(" ".join(extra_asflags)))
        if extra_cflags:
            args.append("--extra-cflags={}".format(" ".join(extra_cflags)))
        if extra_ldflags:
            args.append("--extra-ldflags={}".format(" ".join(extra_ldflags)))
        self._autotools.configure(args=args, vars=self._override_env, configure_dir=self._source_subfolder, build=build_canonical_name, host=host_canonical_name)
        return self._autotools

    def build(self):
        with self._build_context():
            # relocatable shared lib on macOS
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                  "-install_name \\$(DESTDIR)\\$(libdir)/",
                                  "-install_name @rpath/")
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self._is_msvc:
            ext = ".dll.lib" if self.options.shared else ".lib"
            rename(self, os.path.join(self.package_folder, "lib", "libx264{}".format(ext)),
                         os.path.join(self.package_folder, "lib", "x264.lib"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "x264")
        self.cpp_info.libs = ["x264"]
        if self._is_msvc and self.options.shared:
            self.cpp_info.defines.append("X264_API_IMPORTS")
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.extend(["dl", "pthread", "m"])
        elif self.settings.os == "Android":
            self.cpp_info.system_libs.extend(["dl", "m"])

        # TODO: to remove in conan v2 once pkg_config generator removed
        self.cpp_info.names["pkg_config"] = "x264"
