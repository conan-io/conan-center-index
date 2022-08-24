from conan.tools.microsoft import msvc_runtime_flag
from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conan.errors import ConanInvalidConfiguration
import contextlib
import os

required_conan_version = ">=1.33.0"


class MpirConan(ConanFile):
    name = "mpir"
    description = "MPIR is a highly optimised library for bignum arithmetic" \
                  "forked from the GMP bignum library."
    topics = ("mpir", "multiprecision", "math", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mpir.org/"
    license = "LGPL-3.0-or-later"

    provides = []

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cxx": [True, False],
        "enable_gmpcompat": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cxx": True,
        "enable_gmpcompat": True,
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self._is_msvc and self.options.shared:
            del self.options.enable_cxx
        if not self.options.get_safe("enable_cxx", False):
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd
        if self.options.enable_gmpcompat:
            self.provides.append("gmp")

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building doesn't work (yet)")

    def build_requirements(self):
        self.build_requires("yasm/1.3.0")
        if not self._is_msvc:
            self.build_requires("m4/1.4.19")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, keep_permissions=True, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    @property
    def _platforms(self):
        return {"x86": "Win32", "x86_64": "x64"}

    @property
    def _dll_or_lib(self):
        return "dll" if self.options.shared else "lib"

    @property
    def _vcxproj_paths(self):
        compiler_version = self.settings.compiler.version if tools.Version(self.settings.compiler.version) < "16" else "15"
        build_subdir = "build.vc{}".format(compiler_version)
        vcxproj_paths = [
            os.path.join(self._source_subfolder, build_subdir,
                         "{}_mpir_gc".format(self._dll_or_lib),
                         "{}_mpir_gc.vcxproj".format(self._dll_or_lib))
        ]
        if self.options.get_safe("enable_cxx"):
            vcxproj_paths.append(os.path.join(self._source_subfolder, build_subdir,
                                              "lib_mpir_cxx", "lib_mpir_cxx.vcxproj"))
        return vcxproj_paths

    def _build_visual_studio(self):
        if not self.options.shared: # RuntimeLibrary only defined in lib props files
            build_type = "debug" if self.settings.build_type == "Debug" else "release"
            props_path = os.path.join(self._source_subfolder, "build.vc",
                                      "mpir_{}_lib.props".format(build_type))
            old_runtime = "MultiThreaded{}".format(
                "Debug" if build_type == "debug" else "",
            )
            new_runtime = "MultiThreaded{}{}".format(
                "Debug" if "d" in msvc_runtime_flag(self) else "",
                "DLL" if "MD" in msvc_runtime_flag(self) else "",
            )
            tools.replace_in_file(props_path, old_runtime, new_runtime)
        msbuild = MSBuild(self)
        for vcxproj_path in self._vcxproj_paths:
            msbuild.build(vcxproj_path, platforms=self._platforms, upgrade_project=False)

    @contextlib.contextmanager
    def _build_context(self):
        if self.settings.compiler == "apple-clang":
            env_build = {"CC": tools.XCRun(self.settings).cc,
                         "CXX": tools.XCRun(self.settings).cxx}
            if hasattr(self, "settings_build"):
                # there is no CFLAGS_FOR_BUILD/CXXFLAGS_FOR_BUILD
                xcrun = tools.XCRun(self.settings_build)
                flags = " -Wno-implicit-function-declaration -isysroot {} -arch {}".format(xcrun.sdk_path, tools.to_apple_arch(self.settings_build.arch))
                env_build["CC_FOR_BUILD"] = xcrun.cc + flags
                env_build["CXX_FOR_BUILD"] = xcrun.cxx + flags
            with tools.environment_append(env_build):
                yield
        else:
            yield

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
            args = []
            if self.options.shared:
                args.extend(["--disable-static", "--enable-shared"])
            else:
                args.extend(["--disable-shared", "--enable-static"])
            args.append("--with-pic" if self.options.get_safe("fPIC", True) else "--without-pic")

            args.append("--disable-silent-rules")
            args.append("--enable-cxx" if self.options.get_safe("enable_cxx") else "--disable-cxx")
            args.append("--enable-gmpcompat" if self.options.enable_gmpcompat else "--disable-gmpcompat")

            # compiler checks are written for C89 but compilers that default to C99 treat implicit functions as error
            self._autotools.flags.append("-Wno-implicit-function-declaration")
            self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        if self._is_msvc:
            self._build_visual_studio()
        else:
            with tools.chdir(self._source_subfolder), self._build_context():
                # relocatable shared lib on macOS
                tools.replace_in_file("configure", "-install_name \\$rpath/", "-install_name @rpath/")
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("COPYING*", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            lib_folder = os.path.join(self._source_subfolder, self._dll_or_lib,
                                    self._platforms.get(str(self.settings.arch)),
                                    str(self.settings.build_type))
            self.copy("mpir.h", dst="include", src=lib_folder, keep_path=True)
            if self.options.enable_gmpcompat:
                self.copy("gmp.h", dst="include", src=lib_folder, keep_path=True)
            if self.options.get_safe("enable_cxx"):
                self.copy("mpirxx.h", dst="include", src=lib_folder, keep_path=True)
                if self.options.enable_gmpcompat:
                    self.copy("gmpxx.h", dst="include", src=lib_folder, keep_path=True)
            self.copy(pattern="*.dll*", dst="bin", src=lib_folder, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=lib_folder, keep_path=False)
        else:
            with tools.chdir(self._source_subfolder), self._build_context():
                autotools = self._configure_autotools()
                autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "share"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        if self.options.get_safe("enable_cxx"):
            self.cpp_info.libs.append("mpirxx")
        self.cpp_info.libs.append("mpir")
        if self.options.enable_gmpcompat and not self._is_msvc:
            if self.options.get_safe("enable_cxx"):
                self.cpp_info.libs.append("gmpxx")
            self.cpp_info.libs.append("gmp")
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("MSC_USE_DLL")
