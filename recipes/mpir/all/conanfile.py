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
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _platforms = {'x86': 'Win32', 'x86_64': 'x64'}
    _autotools = None

    def build_requirements(self):
        self.build_requires("yasm/1.3.0")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    @property
    def _dll_or_lib(self):
        return "dll" if self.options.shared else "lib"

    @property
    def _vcxproj_path(self):
        compiler_version = self.settings.compiler.version if tools.Version(self.settings.compiler.version) < "16" else "15"
        return os.path.join(self._source_subfolder,"build.vc{}".format(compiler_version),
                                                   "{}_mpir_gc".format(self._dll_or_lib),
                                                   "{}_mpir_gc.vcxproj".format(self._dll_or_lib))

    def source(self):
        tools.get(keep_permissions=True, **self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

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
        msbuild.build(self._vcxproj_path, platforms=self._platforms, upgrade_project=False)

    def _configure_autotools(self):
        if not self._autotools:
            self._autotools = AutoToolsBuildEnvironment(self)
            args = []
            if self.options.shared:
                args.extend(['--disable-static', '--enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            args.append("--with-pic" if self.options.get_safe("fPIC") else "--without-pic")

            args.extend(['--disable-silent-rules', '--enable-gmpcompat', '--enable-cxx'])
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
        if self.settings.compiler == 'Visual Studio':
            lib_folder = os.path.join(self._source_subfolder, self._dll_or_lib, 
                                    self._platforms.get(str(self.settings.arch)), 
                                    str(self.settings.build_type))
            self.copy("*.h", dst="include", src=lib_folder, keep_path=True)
            self.copy(pattern="*.dll*", dst="bin", src=lib_folder, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=lib_folder, keep_path=False)        
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()
            tools.rmdir(os.path.join(self.package_folder, 'share'))
            with tools.chdir(os.path.join(self.package_folder, "lib")):
                for filename in glob.glob("*.la"):
                    os.unlink(filename)

    def package_info(self):
        self.cpp_info.libs = ['mpir']
