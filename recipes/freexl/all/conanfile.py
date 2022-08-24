from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
import functools
import os
import shutil

required_conan_version = ">=1.36.0"


class FreexlConan(ConanFile):
    name = "freexl"
    description = "FreeXL is an open source library to extract valid data " \
                  "from within an Excel (.xls) spreadsheet."
    license = ["MPL-1.0", "GPL-2.0-only", "LGPL-2.1-only"]
    topics = ("freexl", "excel", "xls")
    homepage = "https://www.gaia-gis.it/fossil/freexl/index"
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

    @property
    def _user_info_build(self):
        return getattr(self, "user_info_build", self.deps_user_info)

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("libiconv/1.16")

    def build_requirements(self):
        if not self._is_msvc:
            self.build_requires("gnu-config/cci.20201022")
            if self._settings_build.os == "Windows" and not tools.get_env("CONAN_BASH_PATH"):
                self.build_requires("msys2/cci.latest")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        if self._is_msvc:
            self._build_msvc()
        else:
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_SUB,
                    os.path.join(self._source_subfolder, "config.sub"))
            shutil.copy(self._user_info_build["gnu-config"].CONFIG_GUESS,
                    os.path.join(self._source_subfolder, "config.guess"))
            # relocatable shared lib on macOS
            tools.replace_in_file(os.path.join(self._source_subfolder, "configure"),
                                  "-install_name \\$rpath/",
                                  "-install_name @rpath/")
            autotools = self._configure_autotools()
            autotools.make()

    def _build_msvc(self):
        args = "freexl_i.lib FREEXL_EXPORT=-DDLL_EXPORT" if self.options.shared else "freexl.lib"
        with tools.chdir(self._source_subfolder):
            with tools.vcvars(self.settings):
                with tools.environment_append(VisualStudioBuildEnvironment(self).vars):
                    self.run("nmake -f makefile.vc {}".format(args))

    @functools.lru_cache(1)
    def _configure_autotools(self):
        autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        yes_no = lambda v: "yes" if v else "no"
        args = [
            "--enable-shared={}".format(yes_no(self.options.shared)),
            "--enable-static={}".format(yes_no(not self.options.shared)),
        ]
        autotools.configure(args=args, configure_dir=self._source_subfolder)
        return autotools

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy("freexl.h", dst="include", src=os.path.join(self._source_subfolder, "headers"))
            self.copy("*.lib", dst="lib", src=self._source_subfolder)
            self.copy("*.dll", dst="bin", src=self._source_subfolder)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.la")

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "freexl")
        suffix = "_i" if self._is_msvc and self.options.shared else ""
        self.cpp_info.libs = ["freexl{}".format(suffix)]
        if self.settings.os in ("FreeBSD", "Linux"):
            self.cpp_info.system_libs.append("m")
