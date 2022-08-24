from conans import AutoToolsBuildEnvironment, ConanFile, tools
from conan.errors import ConanInvalidConfiguration
import glob
import os


class LibBsdConan(ConanFile):
    name = "libbsd"
    description = "This library provides useful functions commonly found on BSD systems, and lacking on others like GNU systems, " \
                  "thus making it easier to port projects with strong BSD origins, without needing to embed the same code over and over again on each project."
    topics = ("conan", "libbsd", "useful", "functions", "bsd", "GNU")
    license = ("ISC", "MIT", "Beerware", "BSD-2-clause", "BSD-3-clause", "BSD-4-clause")
    homepage = "https://libbsd.freedesktop.org/wiki/"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = "patches/**"

    _autotools = None

    def build_requirements(self):
        self.build_requires("libtool/2.4.6")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
    
    def validate(self):
        if not tools.apple.is_apple_os(self, self.settings.os) and self.settings.os != "Linux":
            raise ConanInvalidConfiguration("libbsd is only available for GNU-like operating systems (e.g. Linux)")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        if tools.apple.is_apple_os(self, self.settings.os):
            self._autotools.flags.append("-Wno-error=implicit-function-declaration")
        conf_args = [
        ]
        if self.options.shared:
            conf_args.extend(["--enable-shared", "--disable-static"])
        else:
            conf_args.extend(["--disable-shared", "--enable-static"])
        self._autotools.configure(args=conf_args, configure_dir=self._source_subfolder)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        with tools.files.chdir(self, self._source_subfolder):
            self.run("autoreconf -fiv")
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        autotools = self._configure_autotools()
        autotools.install()

        os.unlink(os.path.join(os.path.join(self.package_folder, "lib", "libbsd.la")))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.components["bsd"].libs = ["bsd"]
        self.cpp_info.components["bsd"].names["pkg_config"] = "libbsd"

        self.cpp_info.components["libbsd-overlay"].libs = []
        self.cpp_info.components["libbsd-overlay"].requires = ["bsd"]
        self.cpp_info.components["libbsd-overlay"].includedirs.append(os.path.join("include", "bsd"))
        self.cpp_info.components["libbsd-overlay"].defines = ["LIBBSD_OVERLAY"]
        self.cpp_info.components["libbsd-overlay"].names["pkg_config"] = "libbsd-overlay"

        # on apple-clang, GNU .init_array section is not supported
        if self.settings.compiler != "apple-clang":
            self.cpp_info.components["libbsd-ctor"].libs = ["bsd-ctor"]
            self.cpp_info.components["libbsd-ctor"].requires = ["bsd"]
            if self.settings.os == "Linux":
                self.cpp_info.components["libbsd-ctor"].exelinkflags = ["-Wl,-z,nodlopen", "-Wl,-u,libbsd_init_func"]
                self.cpp_info.components["libbsd-ctor"].sharedlinkflags = ["-Wl,-z,nodlopen", "-Wl,-u,libbsd_init_func"]
            self.cpp_info.components["libbsd-ctor"].names["pkg_config"] = "libbsd-ctor"
