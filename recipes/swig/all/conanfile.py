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
    exports_sources = "patches/**"
    settings = "os", "arch", "compiler", "build_type"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH") \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")
        if self.settings.compiler == "Visual Studio":
            self.build_requires("winflexbison/2.5.22")
        else:
            self.build_requires("bison/3.7.1")
        self.build_requires("automake/1.16.2")

    def requirements(self):
        self.requires("pcre/8.41")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("swig-rel-{}".format(self.version), self._source_subfolder)

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler != "Visual Studio":
            env["YACC"] = self.deps_user_info["bison"].YACC
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "CC": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "CXX": "{} cl -nologo".format(tools.unix_path(self.deps_user_info["automake"].compile)),
                    "AR": "{} link".format(self.deps_user_info["automake"].ar_lib),
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
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        if self.settings.compiler != "Visual Studio":
            with tools.chdir(os.path.join(self.package_folder, "bin")):
                strip = (tools.get_env("STRIP") or tools.which("strip")).replace("\\", "/")
                ext = ".exe" if tools.os_info.is_windows else ""
                if strip:
                    self.run("{} swig{}".format(strip, ext), win_bash=tools.os_info.is_windows)
                    self.run("{} ccache-swig{}".format(strip, ext), win_bash=tools.os_info.is_windows)

    @property
    def _swiglibdir(self):
        return os.path.join(self.package_folder, "bin", "swiglib").replace("\\", "/")

    def package_info(self):
        # FIXME: Don't set cmake_find_package name because conan cmake generators do not define SWIG_EXECUTABLE
        # self.cpp_info.names["cmake_find_package"] = "SWIG"
        # self.cpp_info.names["cmake_find_package_multi"] = "SWIG"

        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
