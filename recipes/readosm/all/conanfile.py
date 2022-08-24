from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import functools
import os

required_conan_version = ">=1.36.0"


class ReadosmConan(ConanFile):
    name = "readosm"
    description = (
        "ReadOSM is an open source library to extract valid data from within "
        "an Open Street Map input file."
    )
    license = ("MPL-1.1", "GPL-2.0-or-later", "LGPL-2.1-or-later")
    topics = ("readosm", "osm", "open-street-map", "xml", "protobuf")
    homepage = "https://www.gaia-gis.it/fossil/readosm"
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

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def requirements(self):
        self.requires("expat/2.4.8")
        self.requires("zlib/1.2.12")

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("libtool/2.4.6")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _build_msvc(self):
        target = "readosm_i.lib" if self.options.shared else "readosm.lib"
        optflags = ["-DDLL_EXPORT"] if self.options.shared else []
        system_libs = [lib + ".lib" for lib in self.deps_cpp_info.system_libs]
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    self.run("nmake -f makefile.vc {} OPTFLAGS=\"{}\" SYSTEM_LIBS=\"{}\"".format(target,
                                                                                                 " ".join(optflags),
                                                                                                 " ".join(system_libs)))

    def _build_autotools(self):
        # fix MinGW
        tools.replace_in_file(os.path.join(self._source_subfolder, "configure.ac"),
                              "AC_CHECK_LIB(z,",
                              "AC_CHECK_LIB({},".format(self.deps_cpp_info["zlib"].libs[0]))
        # Disable tests & examples
        tools.replace_in_file(os.path.join(self._source_subfolder, "Makefile.am"),
                              "SUBDIRS = headers src tests examples",
                              "SUBDIRS = headers src")

        with tools.chdir(self._source_subfolder):
            self.run("{} -fiv".format(tools.get_env("AUTORECONF")), win_bash=tools.os_info.is_windows)
            # Relocatable shared lib for Apple platforms
            tools.replace_in_file("configure", "-install_name \\$rpath/", "-install_name @rpath/")
            autotools = self._configure_autotools()
            autotools.make()

    @functools.lru_cache(1)
    def _configure_autotools(self):
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-static={}".format(yes_no(not self.options.shared)),
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--disable-gcov",
        ]
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        autotools.configure(args=args)
        return autotools

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        if self._is_msvc:
            self._build_msvc()
        else:
            self._build_autotools()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy("readosm.h", dst="include", src=os.path.join(self._source_subfolder, "headers"))
            self.copy("*.lib", dst="lib", src=self._source_subfolder)
            self.copy("*.dll", dst="bin", src=self._source_subfolder)
        else:
            with tools.chdir(self._source_subfolder):
                autotools = self._configure_autotools()
                autotools.install()
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "readosm")
        suffix = "_i" if self._is_msvc and self.options.shared else ""
        self.cpp_info.libs = ["readosm{}".format(suffix)]
