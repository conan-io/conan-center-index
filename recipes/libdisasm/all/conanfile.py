from conans import AutoToolsBuildEnvironment, ConanFile, tools
import os
from contextlib import contextmanager


class LibdisasmConan(ConanFile):
    name = "libdisasm"
    description = "The libdisasm library provides basic disassembly of Intel x86 instructions from a binary stream."
    homepage = "http://bastard.sourceforge.net/libdisasm.html"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("conan", "libdisasm", "disassembler", "x86", "asm")
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports_sources = "patches/**"
    options = {
        "fPIC": [True, False],
        "shared": [True, False]
    }
    default_options = {
        "fPIC": True,
        "shared": False
    }

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")
        if tools.os_info.is_windows and not tools.get_env("CONAN_BASH_PATH"):
            self.build_requires("msys2/20190524")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = self.name + "-" + self.version
        os.rename(extracted_folder, self._source_subfolder)

    @contextmanager
    def _build_context(self):
        env = {}
        if self.settings.compiler == "Visual Studio":
            with tools.vcvars(self.settings):
                env.update({
                    "CC": "cl -nologo",
                    "CXX": "cl -nologo",
                    "CPP": "cl -E -nologo",
                    "AR": "{} lib".format(self.deps_user_info["automake"].ar_lib.replace("\\", "/")),
                    "LD": "link -nologo",
                    "NM": "dumpbin -symbols",
                    "STRIP": ":",
                    "RANLIB": ":",
                })
                with tools.environment_append(env):
                    yield
        else:
            yield

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        yes_no = lambda v: "yes" if v else "no"
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.libs = []

        conf_args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"].get(self.version, []):
            tools.patch(**patch)
        with tools.chdir(self._source_subfolder):
            self.run("autoreconf -fiv", run_environment=True, win_bash=tools.os_info.is_windows)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.make()
            if self.settings.os != "Windows":
                autotools.make(args=["-C", "x86dis"])

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        with self._build_context():
            autotools = self._configure_autotools()
            autotools.install()
            if self.settings.os != "Windows":
                autotools.install(args=["-C", "x86dis"])

        os.unlink(os.path.join(self.package_folder, "lib", "libdisasm.la"))

    def package_info(self):
        libname = "disasm"
        if self.settings.os == "Windows" and self.options.shared:
            libname += ".dll.lib" if self.settings.compiler == "Visual Studio" else ".dll.a"
        self.cpp_info.libs = [libname]

        if self.settings.os != "Windows":
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
