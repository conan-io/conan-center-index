from conans import ConanFile, tools, AutoToolsBuildEnvironment
import contextlib
import functools
import os

required_conan_version = ">=1.33.0"


class SwigConan(ConanFile):
    name = "swig"
    description = "SWIG is a software development tool that connects programs written in C and C++ with a variety of high-level programming languages."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.swig.org"
    license = "GPL-3.0-or-later"
    topics = ("swig", "python", "java", "wrapper")
    exports_sources = "patches/**", "cmake/*"
    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def requirements(self):
        self.requires("pcre/8.45")

    def build_requirements(self):
        if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("bison/3.7.6")
        self.build_requires("automake/1.16.4")

    def package_id(self):
        del self.info.settings.compiler

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _user_info_build(self):
        # If using the experimental feature with different context for host and
        # build, the 'user_info' attributes of the 'build_requires' packages
        # will be located into the 'user_info_build' object. In other cases they
        # will be located into the 'deps_user_info' object.
        return getattr(self, "user_info_build", self.deps_user_info)

    @contextlib.contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler != "Visual Studio":
            env["YACC"] = self._user_info_build["bison"].YACC
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self):
                env.update({
                    "CC": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.microsoft.unix_path(self, self._user_info_build["automake"].compile)),
                    "AR": "{} link".format(self._user_info_build["automake"].ar_lib),
                    "LD": "link",
                })
                with tools.environment_append(env):
                    yield
        else:
            with tools.environment_append(env):
                yield

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        deps_libpaths = autotools.library_paths
        deps_libs = autotools.libs
        deps_defines = autotools.defines
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            autotools.link_flags.append("-static")

        libargs = list("-L\"{}\"".format(p) for p in deps_libpaths) + list("-l\"{}\"".format(l) for l in deps_libs)
        args = [
            "PCRE_LIBS={}".format(" ".join(libargs)),
            "PCRE_CPPFLAGS={}".format(" ".join("-D{}".format(define) for define in deps_defines)),
            "--host={}".format(self.settings.arch),
            "--with-swiglibdir={}".format(self._swiglibdir),
        ]
        if self.settings.compiler == 'gcc':
            args.append("LIBS=-ldl")

        host, build = None, None

        if self.settings.compiler == "Visual Studio":
            self.output.warn("Visual Studio compiler cannot create ccache-swig. Disabling ccache-swig.")
            args.append("--disable-ccache")
            autotools.flags.append("-FS")
            # MSVC canonical names aren't understood
            host, build = False, False

        if self.settings.os == "Macos" and self.settings.arch == "armv8":
            # FIXME: Apple ARM should be handled by build helpers
            autotools.flags.append("-arch arm64")
            autotools.link_flags.append("-arch arm64")

        autotools.libs = []
        autotools.library_paths = []

        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            autotools.libs.extend(["mingwex", "ssp"])

        autotools.configure(args=args, configure_dir=self._source_subfolder,
                            host=host, build=build)
        return autotools

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def build(self):
        self._patch_sources()
        with tools.files.chdir(self, os.path.join(self._source_subfolder)):
            self.run("./autogen.sh", win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE*", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="COPYRIGHT", dst="licenses", src=self._source_subfolder)
        self.copy("*", src="cmake", dst=self._module_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

    @property
    def _swiglibdir(self):
        return os.path.join(self.package_folder, "bin", "swiglib").replace("\\", "/")

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file(self):
        return "conan-official-{}-targets.cmake".format(self.name)

    def package_info(self):
        self.cpp_info.includedirs=[]
        self.cpp_info.names["cmake_find_package"] = "SWIG"
        self.cpp_info.names["cmake_find_package_multi"] = "SWIG"
        self.cpp_info.builddirs = [self._module_subfolder]
        self.cpp_info.build_modules["cmake_find_package"] = \
            [os.path.join(self._module_subfolder, self._module_file)]
        self.cpp_info.build_modules["cmake_find_package_multi"] = \
            [os.path.join(self._module_subfolder, self._module_file)]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
