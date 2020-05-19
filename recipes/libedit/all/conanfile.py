from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
from contextlib import contextmanager
import glob
import os


class LibeditConan(ConanFile):
    name = "libedit"
    description = "Autotool- and libtoolized port of the NetBSD Editline library (libedit)."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://thrysoee.dk/editline/"
    topics = ("conan", "libedit", "line", "editing", "history", "tokenization")
    license = "BSD-3-Clause"
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "terminal_db": ["termcap", "ncurses", "tinfo"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "terminal_db": "termcap",
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.terminal_db == "termcap":
            self.requires("termcap/1.3.1")
        elif self.options.terminal_db == "ncurses":
            self.requires("ncurses/6.2")
        elif self.options.terminal_db == "tinfo":
            raise ConanInvalidConfiguration("tinfo is not (yet) available on CCI")
            self.requires("libtinfo/x.y.z")

    def build_requirements(self):
        if tools.os_info.is_windows and "CONAN_BASH_PATH" not in os.environ \
                and tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        archive_name = glob.glob("{}-*-{}".format(self.name, self.version))[0]
        os.rename(archive_name, self._source_subfolder)

    @contextmanager
    def _build_context(self):
        env_vars = {}
        if self.settings.compiler == "Visual Studio":
            build_aux_path = os.path.join(self.build_folder, self._source_subfolder, "build-aux")
            lt_compile = tools.unix_path(os.path.join(build_aux_path, "compile"))
            lt_ar = tools.unix_path(os.path.join(build_aux_path, "ar-lib"))
            env_vars.update({
                "CC": "{} cl -nologo".format(lt_compile),
                "CXX": "{} cl -nologo".format(lt_compile),
                "LD": "link",
                "STRIP": ":",
                "AR": "{} lib".format(lt_ar),
                "RANLIB": ":",
                "NM": "dumpbin -symbols"
            })
            with tools.vcvars(self.settings):
                with tools.environment_append(env_vars):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)

        configure_args = []
        if self.options.shared:
            configure_args.extend(["--disable-static", "--enable-shared"])
        else:
            configure_args.extend(["--enable-static", "--disable-shared"])

        self._autotools.configure(args=configure_args, configure_dir=self._source_subfolder)
        return self._autotools

    def _patch_sources(self):
        for patchdata in self.conan_data.get("patches",{}).get(self.version, []):
            tools.patch(**patchdata)

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        os.unlink(os.path.join(self.package_folder, "lib", "libedit.la"))

    def package_info(self):
        self.cpp_info.libs = ["edit"]
        self.cpp_info.includedirs.append(os.path.join("include", "editline"))
