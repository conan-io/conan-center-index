from conans import ConanFile, AutoToolsBuildEnvironment, tools
from contextlib import contextmanager
import os


class LibConfuse(ConanFile):
    name = "libconfuse"
    description = "Small configuration file parser library for C"
    topics = ("conan", "libconfuse", "configuration", "parser")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/martinh/libconfuse"
    license = "ISC"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("confuse-{}".format(self.version), self._source_subfolder)

    def build_requirements(self):
        if tools.os_info.is_windows and not os.environ.get("CONAN_BASH_PATH") and \
                tools.os_info.detect_windows_subsystem() != "msys2":
            self.build_requires("msys2/20190524")

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        conf_args = []
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(configure_dir=self._source_subfolder, args=conf_args)
        return self._autotools

    @contextmanager
    def _build_context(self):
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                with tools.environment_append({"CC": "cl -nologo",
                                               "CXX": "cl -nologo",
                                               "LD": "link"}):
                    yield
        else:
            yield

    def _patch_sources(self):
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.in"),
                              "SUBDIRS = m4 po src $(EXAMPLES) tests doc",
                              "SUBDIRS = m4 src")
        if not self.options.shared:
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "confuse.h"),
                                  "__declspec (dllimport)", "")

    def build(self):
        self._patch_sources()
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()

        os.unlink(os.path.join(self.package_folder, "lib", "libconfuse.la"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        lib = "confuse"
        if self.settings.os == "Windows" and self.options.shared:
            lib += ".dll.{}".format("lib" if self.settings.compiler == "Visual Studio" else "a")
        self.cpp_info.libs = [lib]
        self.cpp_info.names["pkg_config"] = "libconfuse"
