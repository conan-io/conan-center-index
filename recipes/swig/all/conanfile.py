from conans import ConanFile, tools, AutoToolsBuildEnvironment
from contextlib import contextmanager
import os


class SwigConan(ConanFile):
    name = "swig"
    description = "SWIG is a software development tool that connects programs written in C and C++ with a variety of high-level programming languages."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.swig.org"
    license = "GPL-3.0-or-later"
    topics = ("conan", "swig", "python", "java", "wrapper")
    exports_sources = "patches/**", "cmake/*"
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def package_id(self):
        del self.info.settings.compiler

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/cci.latest")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("winflexbison/2.5.24")
        else:
            self.build_requires("bison/3.7.1")
        self.build_requires("automake/1.16.3")

    def requirements(self):
        self.requires("pcre/8.44")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("swig-rel-{}".format(self.version), self._source_subfolder)

    @property
    def _user_info_build(self):
        # If using the experimental feature with different context for host and
        # build, the 'user_info' attributes of the 'build_requires' packages
        # will be located into the 'user_info_build' object. In other cases they
        # will be located into the 'deps_user_info' object.
        return getattr(self, "user_info_build", None) or self.deps_user_info

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler != "Visual Studio":
            env["YACC"] = self._user_info_build["bison"].YACC
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "CC": "{} cl -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self._user_info_build["automake"].compile)),
                    "AR": "{} link".format(self._user_info_build["automake"].ar_lib),
                    "LD": "link",
                })
                with tools.environment_append(env):
                    yield
        else:
            with tools.environment_append(env):
                yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools

        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        deps_libpaths = self._autotools.library_paths
        deps_libs = self._autotools.libs
        deps_defines = self._autotools.defines
        if self.settings.os == "Windows" and self.settings.compiler != "Visual Studio":
            self._autotools.link_flags.append("-static")

        libargs = list("-L\"{}\"".format(p) for p in deps_libpaths) + list("-l\"{}\"".format(l) for l in deps_libs)
        args = [
            "PCRE_LIBS={}".format(" ".join(libargs)),
            "PCRE_CPPFLAGS={}".format(" ".join("-D{}".format(define) for define in deps_defines)),
            "--host={}".format(self.settings.arch),
            "--with-swiglibdir={}".format(self._swiglibdir),
        ]

        host, build = None, None

        if self.settings.compiler == "Visual Studio":
            self.output.warn("Visual Studio compiler cannot create ccache-swig. Disabling ccache-swig.")
            args.append("--disable-ccache")
            self._autotools.flags.append("-FS")
            # MSVC canonical names aren't understood
            host, build = False, False

        self._autotools.libs = []
        self._autotools.library_paths = []

        self._autotools.configure(args=args, configure_dir=self._source_subfolder,
                                  host=host, build=build)
        return self._autotools

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        with tools.chdir(os.path.join(self._source_subfolder)):
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
        self.cpp_info.names["cmake_find_package"] = "SWIG"
        self.cpp_info.names["cmake_find_package_multi"] = "SWIG"
        self.cpp_info.builddirs = [self._module_subfolder]
        self.cpp_info.build_modules = [os.path.join(self._module_subfolder, self._module_file)]

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
