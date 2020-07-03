from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.errors import ConanInvalidConfiguration
from conans.model.version import Version
import os


class QuickfastConan(ConanFile):
    name = "quickfast"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://objectcomputing.com/"
    description = "QuickFAST is an Open Source native C++ implementation of the FAST Protocol"
    topics = ("conan", "QuickFAST", "FAST", "FIX", "Fix Adapted for STreaming", "Financial Information Exchange",
              "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    requires = ["boost/1.73.0", "xerces-c/3.2.3"]
    build_requires = "makefile-project-workspace-creator/4.1.46"
    exports_sources = "patches/**"
    generators = "visual_studio", "make"
    _msbuild = None
    _env_build = None
    _args = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _visual_studio_platform(self):
        if self.settings.arch == "x86":
            return "Win32"
        elif self.settings.arch == "x86_64":
            return "x64"
        else:
            raise ConanInvalidConfiguration("QuickFAST cannot be built on Visual Studio for the {} architecture"
                                            .format(self.settings.arch))

    @property
    def _wss_platform(self):
        subsystem = tools.os_info.detect_windows_subsystem()
        if subsystem:
            raise ConanInvalidConfiguration("QuickFAST cannot be built for Windows subsytems ({})"
                                            .format(subsystem))
        return "mingw_msys"

    @property
    def _platform(self):
        if self.settings.compiler == "Visual Studio":
            return self._visual_studio_platform
        elif self.settings.os == 'Macos':
            return 'macosx'
        elif self.settings.os == 'Linux':
            return 'linux'
        elif self.settings.os == 'Windows':
            return self._wss_platform
        else:
            raise ConanInvalidConfiguration("QuickFAST cannot be built for the {} operating system"
                                            .format(self.settings.os))

    @property
    def _visual_studio_build_type(self):
        compiler = self.settings.compiler
        version = Version(compiler.version.value)

        if "8" <= version <= "14":
            return "v" + version
        elif version == "14":
            return "vs2017"
        elif version == "16":
            return "vs2019"
        else:
            raise ConanInvalidConfiguration("QuickFAST cannot be built with Visual Studio version {}"
                                            .format(version))

    @property
    def _build_type(self):
        if self.settings.compiler == "Visual Studio":
            return self._visual_studio_build_type
        else:
            return 'make'

    @property
    def _core_value_template_linkflags(self):
        if self.settings.os == "Macos":
            return ' -value_template "linkflags+=-framework CoreServices -framework CoreFoundation"'
        return ''

    @property
    def _mwc_command_line(self):
        link_flag = ' -static' if not self.options.shared else ' '
        fpic_flag = '-fPIC' if self.options.get_safe("fPIC", default=True) else ''
        platform = self._platform
        build_type = self._build_type
        core_value_template_linkflags = self._core_value_template_linkflags

        return 'perl -S mwc.pl -type {} -exclude src/Examples'.format(build_type) + \
               link_flag + \
               ' -value_template "pic={}"'.format(fpic_flag) + \
               ' -value_template platforms={}'.format(platform) + \
               core_value_template_linkflags + \
               ' -value_template extracppflags+=-DBOOST_BIND_GLOBAL_PLACEHOLDERS' + \
               ' QuickFAST.mwc'

    def _configure_msbuild(self):
        if self._msbuild:
            return self._msbuild

        self.run(self._mwc_command_line)
        self._msbuild = MSBuild(self)
        return self._msbuild

    def _configure_autotools(self):
        if self._env_build:
            return self._env_build, self._args

        self._env_build = AutoToolsBuildEnvironment(self, win_bash=self.settings.os is "Windows")
        self._args = ['CONAN_MAKE_FILE=' + os.path.join(self.build_folder, "conanbuildinfo.mak")]
        self.run(self._mwc_command_line, win_bash=self.settings.os is "Windows")
        return self._env_build, self._args

    def _patch_sources(self):
        patches = self.conan_data["patches"][self.version]
        for patch in patches:
            tools.patch(**patch)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version.replace(".", "_"), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("Windows builds still not working...")

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

        if self.options.shared:
            del self.options.fPIC

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio" and \
                tools.os_info.is_windows and \
                "CONAN_BASH_PATH" not in os.environ and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def build(self):
        self._patch_sources()

        with tools.chdir(self._source_subfolder), \
             tools.environment_append(
                 {"QUICKFAST_ROOT": os.path.join(self.build_folder, self._source_subfolder),
                  "XERCESCROOT": self.deps_cpp_info["xerces-c"].rootpath,
                  }):

            if self.settings.compiler == "Visual Studio":
                msbuild = self._configure_msbuild()
                msbuild.build("QuickFAST.sln")
            else:
                env_build, args = self._configure_autotools()
                env_build.make(args=args, target="QuickFAST")

    def package(self):
        with tools.chdir(self._source_subfolder), \
             tools.environment_append(
                 {"QUICKFAST_ROOT": os.path.join(self.build_folder, self._source_subfolder),
                  "XERCESCROOT": self.deps_cpp_info["xerces-c"].rootpath,
                  }):

            if self.settings.compiler == "Visual Studio":
                msbuild = self._configure_msbuild()
                msbuild.build("QuickFAST")
            else:
                env_build, args = self._configure_autotools()
                env_build.make(args=args, target="QuickFAST")

        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.h", dst="include/quickfast", src=os.path.join(self._source_subfolder, "src"))
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "quickfast"))
        self.cpp_info.defines.append("BOOST_BIND_NO_PLACEHOLDERS")
        self.cpp_info.defines.append("XML_USE_PTHREADS")
        if self.options.shared:
            self.cpp_info.defines.append("QUICKFAST_BUILD_DLL")
