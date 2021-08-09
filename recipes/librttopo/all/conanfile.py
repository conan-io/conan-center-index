from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import os
import shutil

required_conan_version = ">=1.33.0"


class LibrttopoConan(ConanFile):
    name = "librttopo"
    description = (
        "The RT Topology Library exposes an API to create and manage "
        "standard (ISO 13249 aka SQL/MM) topologies."
    )
    license = "GPL-2.0-or-later"
    topics = ("librttopo", "topology", "geospatial", "gis")
    homepage = "https://git.osgeo.org/gitea/rttopo/librttopo"
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
        self.requires("geos/3.9.1")

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self.settings.compiler != "Visual Studio":
            self.build_requires("libtool/2.4.6")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @property
    def _rtgeom_geos_version(self):
        geos_version = tools.Version(self.deps_cpp_info["geos"].version)
        return "{}{}".format(geos_version.major, geos_version.minor)

    def _build_msvc(self):
        # Honor flags from profile and inject RTGEOM_GEOS_VERSION definition
        makefilevc = os.path.join(self._source_subfolder, "Makefile.vc")
        tools.replace_in_file(makefilevc, "!INCLUDE nmake.opt", "")
        tools.replace_in_file(makefilevc,
                              "-IC:\OSGeo4W\include",
                              "$(CFLAGS) -DRTGEOM_GEOS_VERSION={}".format(self._rtgeom_geos_version))
        tools.replace_in_file(makefilevc, "C:\OSGeo4W\lib\geos_c.lib", "")

        # "configure" librttopo_geom.h.in as it is done in autoconf
        librttopo_geom = os.path.join(self._source_subfolder, "headers", "librttopo_geom.h")
        shutil.copy(os.path.join(self._source_subfolder, "headers", "librttopo_geom.h.in"),
                    librttopo_geom)
        tools.replace_in_file(librttopo_geom, "@SRID_MAX@", "999999")
        tools.replace_in_file(librttopo_geom, "@SRID_USR_MAX@", "998999")

        args = "librttopo_i.lib" if self.options.shared else "librttopo.lib"
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    self.run("nmake -f makefile.vc {}".format(args))

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "RTGEOM_GEOS_VERSION={}".format(self._rtgeom_geos_version),
        ]
        self._autotools.configure(configure_dir=self._source_subfolder, args=args)
        return self._autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            self._build_msvc()
        else:
            with tools.chdir(self._source_subfolder):
                self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy("*.h", dst="include", src=os.path.join(self._source_subfolder, "headers"))
            self.copy("*.lib", dst="lib", src=self._source_subfolder)
            self.copy("*.dll", dst="bin", src=self._source_subfolder)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "rttopo"
        prefix = "lib" if self.settings.compiler == "Visual Studio" else ""
        suffix = "_i" if self.settings.compiler == "Visual Studio" and self.options.shared else ""
        self.cpp_info.libs = ["{}rttopo{}".format(prefix, suffix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
