from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.errors import ConanInvalidConfiguration
import os
import glob

class MpirConan(ConanFile):
    name = "mpir"
    description = "MPIR is a highly optimised library for bignum arithmetic" \
                  "forked from the GMP bignum library."
    topics = ("conan", "mpir", "multiprecision", "math", "mathematics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mpir.org/"
    license = "LGPL-3.0-or-later"
    settings = "os", "compiler", "arch", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_cxx": [True, False],
        "enable_gmpcompat": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_cxx": True,
        "enable_gmpcompat": True
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            del self.options.enable_cxx
        if not self.options.get_safe("enable_cxx", False):
            del self.settings.compiler.libcxx
            del self.settings.compiler.cppstd

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("m4/1.4.18")
        self.build_requires("yasm/1.3.0")
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio" and \
           "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20200517")

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self, skip_x64_x86=True):
            raise ConanInvalidConfiguration("Cross-building doesn't work (yet)")

    def source(self):
        tools.get(keep_permissions=True, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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
        if "MD" in self.settings.compiler.runtime and not self.options.shared: # RuntimeLibrary only defined in lib props files
                props_path = os.path.join(self._source_subfolder, "build.vc",
                "mpir_{}_{}.props".format(str(self.settings.build_type).lower(), self._dll_or_lib))
                if self.settings.build_type == "Debug":
                    tools.replace_in_file(props_path, "<RuntimeLibrary>MultiThreadedDebug</RuntimeLibrary>",
                                                      "<RuntimeLibrary>MultiThreadedDebugDLL</RuntimeLibrary>")
                else:
                    tools.replace_in_file(props_path, "<RuntimeLibrary>MultiThreaded</RuntimeLibrary>",
                                                      "<RuntimeLibrary>MultiThreadedDLL</RuntimeLibrary>")
        msbuild = MSBuild(self)
        for vcxproj_path in self._vcxproj_paths:
            msbuild.build(vcxproj_path, platforms=self._platforms, upgrade_project=False)

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
        if self.settings.compiler == "Visual Studio":
            self._build_visual_studio()
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.make()

    def package(self):
        self.copy("COPYING*", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
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
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "share"))
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                for filename in glob.glob("*.la"):
                    os.unlink(filename)

    def package_info(self):
        if self.options.get_safe("enable_cxx"):
            self.cpp_info.libs.append("mpirxx")
        self.cpp_info.libs.append("mpir")
        if self.options.enable_gmpcompat and self.settings.compiler != "Visual Studio":
            if self.options.get_safe("enable_cxx"):
                self.cpp_info.libs.append("gmpxx")
            self.cpp_info.libs.append("gmp")
        if self.settings.os == "Windows" and self.options.shared:
            self.cpp_info.defines.append("MSC_USE_DLL")
