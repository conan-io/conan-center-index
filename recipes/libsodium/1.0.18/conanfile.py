from conans import ConanFile, AutoToolsBuildEnvironment, tools, MSBuild
from conans.errors import ConanInvalidConfiguration
import os


class LibsodiumConan(ConanFile):
    name        = "libsodium"
    description = "A modern and easy-to-use crypto library."
    license     = "ISC"
    url         = "https://github.com/conan-io/conan-center-index"
    homepage    = "https://download.libsodium.org/doc/"
    exports_sources = ["patches/**"]
    settings    = "os", "compiler", "arch", "build_type"
    topics = ("sodium", "libsodium", "encryption", "signature", "hashing")
    generators  = "cmake"
    _source_subfolder = "source_subfolder"
    short_paths = True

    options = {
        "shared" : [True, False],
        "fPIC": [True, False],
        "use_soname" : [True, False],
        "PIE"    : [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "use_soname": True,
        "PIE": False,
    }

    @property
    def _android_id_str(self):
        return "androideabi" if str(self.settings.arch) in ["armv6", "armv7"] else "android"

    @property
    def _is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    @property
    def _vs_configuration(self):
        configuration = ""
        if self.options.shared:
            configuration += "Dyn"
        else:
            configuration += "Static"
        build_type = "Debug" if self.settings.build_type == "Debug" else "Release"
        configuration += build_type
        return configuration

    @property
    def _vs_sln_folder(self):
        folder = {"14": "vs2015",
                  "15": "vs2017",
                  "16": "vs2019"}.get(str(self.settings.compiler.version), None)
        if not folder:
            raise ConanInvalidConfiguration("Unsupported msvc version: {}".format(self.settings.compiler.version))
        return folder

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        # There are several unix tools used (bash scripts for Emscripten, autoreconf on MinGW, etc...)
        if self.settings.compiler != "Visual Studio" and tools.os_info.is_windows and \
                not "CONAN_BASH_PATH" in os.environ and tools.os_info.detect_windows_subsystem() != "Windows":
            self.build_requires("msys2/20190524")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _build_visual(self):
        sln_path = os.path.join(self.build_folder, self._source_subfolder, "builds", "msvc", self._vs_sln_folder, "libsodium.sln")

        msbuild = MSBuild(self)
        msbuild.build(sln_path, upgrade_project=False, platforms={"x86": "Win32"}, build_type=self._vs_configuration)

    def _build_autotools_impl(self, configure_args, host_arch=None):
        win_bash = False
        if self._is_mingw:
            win_bash = True

        autotools = AutoToolsBuildEnvironment(self, win_bash=win_bash)
        if self._is_mingw:
            self.run("autoreconf -i", cwd=self._source_subfolder, win_bash=win_bash)
        host = None
        if host_arch:
            host = False
            configure_args.append("--host=%s" % host_arch)
        autotools.configure(args=configure_args, configure_dir=self._source_subfolder, host=host)
        autotools.make(args=["-j%s" % str(tools.cpu_count())])
        autotools.install()

    def _build_autotools_linux(self, configure_args):
        self._build_autotools_impl(configure_args)

    def _build_autotools_emscripten(self, configure_args):
        self.run("./dist-build/emscripten.sh --standard", cwd=self._source_subfolder)

    def _build_autotools_android(self, configure_args):
        host_arch = "%s-linux-%s" % (tools.to_android_abi(self.settings.arch), self._android_id_str)
        self._build_autotools_impl(configure_args, host_arch)

    def _build_autotools_mingw(self, configure_args):
        arch = "i686" if self.settings.arch == "x86" else self.settings.arch
        host_arch = "%s-w64-mingw32" % arch
        self._build_autotools_impl(configure_args, host_arch)

    def _build_autotools_darwin(self, configure_args):
        os = "ios" if self.settings.os == "iOS" else "darwin"
        host_arch = "%s-apple-%s" % (self.settings.arch, os)
        self._build_autotools_impl(configure_args, host_arch)

    def _build_autotools_neutrino(self, configure_args):
        neutrino_archs = {"x86_64":"x86_64-pc", "x86":"i586-pc", "armv7":"arm-unknown", "armv8": "aarch64-unknown"}
        if self.settings.os.version == "7.0" and str(self.settings.arch) in neutrino_archs:
            host_arch = "%s-nto-qnx7.0.0" % neutrino_archs[str(self.settings.arch)]
            if self.settings.arch == "armv7":
                host_arch += "eabi"
        else:
            raise ConanInvalidConfiguration("Unsupported arch or Neutrino version for libsodium: {} {}".format(self.settings.os, self.settings.arch))
        self._build_autotools_impl(configure_args, host_arch)

    def _build_autotools(self):
        absolute_install_dir = os.path.abspath(os.path.join(".", "install"))
        absolute_install_dir = absolute_install_dir.replace("\\", "/")
        configure_args = self._get_configure_args(absolute_install_dir)

        if self.settings.os in ["Linux", "FreeBSD"]:
            self._build_autotools_linux(configure_args)
        elif self.settings.os == "Emscripten":
            self._build_autotools_emscripten(configure_args)
        elif self.settings.os == "Android":
            self._build_autotools_android(configure_args)
        elif tools.is_apple_os(self.settings.os):
            self._build_autotools_darwin(configure_args)
        elif self._is_mingw:
            self._build_autotools_mingw(configure_args)
        elif self.settings.os == "Neutrino":
            self._build_autotools_neutrino(configure_args)
        else:
            raise ConanInvalidConfiguration("Unsupported os for libsodium: {}".format(self.settings.os))
            
    def validate(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared and "MT" in str(self.settings.compiler.runtime):
                raise ConanInvalidConfiguration("Cannot build shared libsodium libraries with MT(d) runtime")

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.os == "Macos":
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"), r"-install_name \$rpath/", "-install_name ")
        if self.settings.compiler != "Visual Studio":
            self._build_autotools()
        else:
            self._build_visual()

    def package(self):
        self.copy("*LICENSE", dst="licenses", keep_path=False)
        if self.settings.compiler == "Visual Studio":
            self._package_visual()
        else:
            self._package_autotools()

    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if not self.options.shared:
                self.cpp_info.defines = ["SODIUM_STATIC=1"]
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]

    def _package_autotools(self):
        if self.settings.os == "Emscripten":
            prefix = "%s/libsodium-js" % self._source_subfolder
        else:
            prefix = "install"
        lib_folder = os.path.join(prefix, "lib")
        self.copy("*.h", dst="include", src=os.path.join(prefix, "include"))
        self.copy("*.a", dst="lib", src=lib_folder)
        self.copy("*.so*", dst="lib", src=lib_folder, symlinks=True)
        self.copy("*.dylib", dst="lib", src=lib_folder, symlinks=True)

    def _package_visual(self):
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        inc_src = os.path.join(self._source_subfolder, "src", self.name, "include")
        self.copy("*.h", src=inc_src, dst="include", keep_path=True, excludes=("*/private/*"))

    def _autotools_bool_arg(self, arg_base_name, value):
        prefix = "--enable-" if value else "--disable-"
        return prefix + arg_base_name

    def _get_configure_args(self, absolute_install_dir):
        args = [
            "--prefix=%s" % absolute_install_dir,
            self._autotools_bool_arg("shared", self.options.shared),
            self._autotools_bool_arg("static", not self.options.shared),
            self._autotools_bool_arg("soname-versions", self.options.use_soname),
            self._autotools_bool_arg("pie", self.options.PIE)
        ]
        if self.options.get_safe("fPIC"):
            args.append("--with-pic")
        return args
