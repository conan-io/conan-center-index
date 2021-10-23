from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os

required_conan_version = ">=1.33.0"


class LibrasterliteConan(ConanFile):
    name = "librasterlite"
    description = (
        "librasterlite is an open source library that stores and retrieves "
        "huge raster coverages using a SpatiaLite DBMS."
    )
    license = ("MPL-1.1", "GPL-2.0-or-later", "LGPL-2.1-or-later")
    topics = ("rasterlite", "raster", "spatialite")
    homepage = "https://www.gaia-gis.it/fossil/librasterlite"
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
    generators = "pkg_config"
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

    def requirements(self):
        self.requires("libgeotiff/1.7.0")
        self.requires("libjpeg/9d")
        self.requires("libpng/1.6.37")
        self.requires("libspatialite/5.0.1")
        self.requires("libtiff/4.3.0")
        self.requires("sqlite3/3.36.0")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("libtool/2.4.6")
            self.build_requires("pkgconf/1.7.4")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_msvc(self):
        target = "rasterlite_i.lib" if self.options.shared else "rasterlite.lib"
        optflags = ["-D_USE_MATH_DEFINES"]
        system_libs = [lib + ".lib" for lib in self.deps_cpp_info.system_libs]
        if self.options.shared:
            optflags.append("-DDLL_EXPORT")
        with tools.chdir(self._source_subfolder):
            tools.save(os.path.join("headers", "config.h"), "#define VERSION \"{}\"\n".format(self.version))
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    self.run("nmake -f makefile.vc {} OPTFLAGS=\"{}\" SYSTEM_LIBS=\"{}\"".format(target,
                                                                                                 " ".join(optflags),
                                                                                                 " ".join(system_libs)))

    def _build_autotools(self):
        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            with tools.run_environment(self):
                autotools = self._configure_autotools()
                autotools.make()

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--disable-gcov",
        ]
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        self._autotools.configure(args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy("rasterlite.h", dst="include", src=os.path.join(self._source_subfolder, "headers"))
            self.copy("*.lib", dst="lib", src=self._source_subfolder)
            self.copy("*.dll", dst="bin", src=self._source_subfolder)
        else:
            with tools.chdir(self._source_subfolder):
                with tools.run_environment(self):
                    autotools = self._configure_autotools()
                    autotools.install()
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "rasterlite"
        suffix = "_i" if self.settings.compiler == "Visual Studio" and self.options.shared else ""
        self.cpp_info.libs = ["rasterlite{}".format(suffix)]
