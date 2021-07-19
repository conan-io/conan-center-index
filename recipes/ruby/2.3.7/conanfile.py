from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException
import os.path


class RubyConan(ConanFile):
    name = "ruby"
    version = "2.3.7"
    license = "MIT"
    url = "https://github.com/elizagamedev/conan-ruby"
    description = "The Ruby Programming Language"
    settings = "os", "compiler", "build_type", "arch"
    requires = "zlib/1.2.11"
    extensions = (
        "dbm",
        "gdbm",
        "openssl",
        "pty",
        "readline",
        "syslog",
    )
    options = {"with_" + extension: [True, False] for extension in extensions}
    default_options = tuple("with_{}=False".format(extension) for extension in extensions)

    folder = "ruby-{}".format(version)

    def config_options(self):
        del self.settings.compiler.libcxx
        if self.settings.compiler == "Visual Studio":
            del self.settings.build_type

    def build_requirements(self):
        if tools.os_info.is_windows:
            self.build_requires("msys2/20200517")

    def requirements(self):
        if self.options.with_openssl:
            self.requires("openssl/1.1.1d")

    def source(self):
        tools.get("https://cache.ruby-lang.org/pub/ruby/{}/{}.tar.gz".format(
            self.version.rpartition(".")[0],
            self.folder))

    def build_configure(self):
        without_ext = (tuple(extension for extension in self.extensions
                             if not getattr(self.options, "with_" + extension)))

        with tools.chdir(self.folder):
            if self.settings.compiler == "Visual Studio":
                with tools.environment_append({"INCLUDE": self.deps_cpp_info.include_paths,
                                               "LIB": self.deps_cpp_info.lib_paths}):
                    if self.settings.arch == "x86":
                        target = "i686-mswin32"
                    elif self.settings.arch == "x86_64":
                        target = "x64-mswin64"
                    else:
                        raise Exception("Invalid arch")
                    self.run("{} --prefix={} --target={} --without-ext=\"{},\" --disable-install-doc".format(
                        os.path.join("win32", "configure.bat"),
                        self.package_folder,
                        target,
                        ",".join(without_ext)))
                    self.run("nmake")
                    self.run("nmake install")
            else:
                win_bash = tools.os_info.is_windows
                autotools = AutoToolsBuildEnvironment(self, win_bash=win_bash)
                # Remove our libs; Ruby doesn't like Conan's help
                autotools.libs = []

                args = [
                    "--with-out-ext=" + ",".join(without_ext),
                    "--disable-install-doc",
                    "--without-gmp",
                    "--enable-shared",
                ]

                autotools.configure(args=args)
                autotools.make()
                autotools.install()

    def build(self):
        if tools.os_info.is_windows:
            msys_bin = self.deps_env_info["msys2"].MSYS_BIN
            # Make sure that Ruby is first in the path order
            with tools.environment_append({"CONAN_BASH_PATH": os.path.join(msys_bin, "bash.exe")}):
                if self.settings.compiler == "Visual Studio":
                    with tools.vcvars(self.settings):
                        self.build_configure()
                else:
                    self.build_configure()
        else:
            self.build_configure()

    def package_info(self):
        # Find correct lib (shared)
        libname = None
        for f in os.listdir("lib"):
            name, ext = os.path.splitext(f)
            if ext in (".so", ".lib", ".a", ".dylib"):
                if ext != ".lib" and name.startswith("lib"):
                    name = name[3:]
                if not name.endswith("-static"):
                    libname = name
                    break
        if not libname:
            raise ConanException("Could not find built shared library")
        self.cpp_info.libs = [libname]
        bindir = os.path.join(self.package_folder, "bin")
        self.env_info.PATH.append(bindir)
        # Find include config dir
        includedir = os.path.join("include", "ruby-2.3.0")
        configdir = None
        for f in os.listdir(os.path.join(self.package_folder, includedir)):
            if "mswin" in f or "mingw" in f or "linux" in f or "darwin" in f:
                configdir = f
                break
        if not includedir:
            raise Exception("Could not find Ruby config dir")
        self.cpp_info.includedirs = [includedir,
                                     os.path.join(includedir, configdir)]