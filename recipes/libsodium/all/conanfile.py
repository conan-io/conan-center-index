from conans import ConanFile, AutoToolsBuildEnvironment, tools, MSBuild
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class LibsodiumConan(ConanFile):
    name = "libsodium"
    description = "A modern and easy-to-use crypto library."
    license = "ISC"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://doc.libsodium.org/"
    topics = ("sodium", "libsodium", "encryption", "signature", "hashing")
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "use_soname": [True, False],
        "PIE": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "use_soname": True,
        "PIE": False,
    }

    generators = "cmake"
    exports_sources = "patches/*"
    short_paths = True

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if self._settings_build.os == "Windows" and self.settings.compiler != "Visual Studio" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")

    def validate(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared and "MT" in self.settings.compiler.runtime:
                raise ConanInvalidConfiguration("Cannot build shared libsodium libraries with MT(d) runtime")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _msvc_configuration(self):
        configuration = ""
        if self.options.shared:
            configuration += "Dyn"
        else:
            configuration += "Static"
        build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
        configuration += build_type
        return configuration

    @property
    def _msvc_sln_folder(self):
        folder = {
            "14": "vs2015",
            "15": "vs2017",
            "16": "vs2019",
        }.get(str(self.settings.compiler.version), None)
        if not folder:
            raise ConanInvalidConfiguration("Unsupported msvc version: {}".format(self.settings.compiler.version))
        return folder

    def _build_msvc(self):
        sln_path = os.path.join(self.build_folder, self._source_subfolder, "builds", "msvc", self._msvc_sln_folder, "libsodium.sln")

        msbuild = MSBuild(self)
        msbuild.build(sln_path, upgrade_project=False, platforms={"x86": "Win32"}, build_type=self._msvc_configuration)

    @property
    def _android_abi_str(self):
        return "androideabi" if str(self.settings.arch) in ["armv6", "armv7"] else "android"

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        if self.settings.os in ("FreeBSD", "Linux"):
            host = None
        elif self._is_mingw:
            host = "{}-w64-mingw32".format("i686" if self.settings.arch == "x86" else self.settings.arch)
        elif tools.is_apple_os(self.settings.os):
            host = "{}-apple-{}".format(self.settings.arch, "ios" if self.settings.os == "iOS" else "darwin")
        elif self.settings.os == "Android":
            host = "%s-linux-%s" % (tools.to_android_abi(self.settings.arch), self._android_abi_str)
        elif self.settings.os == "Neutrino":
            neutrino_archs = {"x86_64":"x86_64-pc", "x86":"i586-pc", "armv7":"arm-unknown", "armv8": "aarch64-unknown"}
            if self.settings.os.version == "7.0" and str(self.settings.arch) in neutrino_archs:
                host = "{}-nto-qnx7.0.0".format(neutrino_archs[str(self.settings.arch)])
                if self.settings.arch == "armv7":
                    host += "eabi"
            else:
                raise ConanInvalidConfiguration("Unsupported arch or Neutrino version for libsodium: {} {}".format(self.settings.os, self.settings.arch))
        elif self.settings.os == "Emscripten":
            host = None
            self.output.warn("os=Emscripten is not tested/supported by this recipe")
            # FIXME: ./dist-build/emscripten.sh does not respect options of this recipe
        else:
            raise ConanInvalidConfiguration("Unsupported os for libsodium: {}".format(self.settings.os))
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-soname-versions={}".format(yes_no(self.options.use_soname)),
            "--enable-pie={}".format(yes_no(self.options.PIE)),
        ]
        self._autotools.configure(args=args, configure_dir=self._source_subfolder, host=host)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"), r"-install_name \$rpath/", "-install_name ")
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            if self._is_mingw:
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), cwd=self._source_subfolder, win_bash=tools.os_info.is_windows)
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("*LICENSE", dst="licenses", keep_path=False)
        if self.settings.compiler == "Visual Studio":
            self.copy("*.lib", dst="lib", keep_path=False)
            self.copy("*.dll", dst="bin", keep_path=False)
            inc_src = os.path.join(self._source_subfolder, "src", self.name, "include")
            self.copy("*.h", src=inc_src, dst="include", keep_path=True, excludes=("*/private/*"))
        else:
            autotools = self._configure_autotools()
            autotools.install()

            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "libsodium"
        if self.settings.compiler == "Visual Studio":
            if not self.options.shared:
                self.cpp_info.defines = ["SODIUM_STATIC=1"]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs = ["pthread"]
