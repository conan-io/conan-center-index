from conans import ConanFile, tools, Meson, VisualStudioBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os
import shutil
import glob


class GobjectIntrospectionConan(ConanFile):
    name = "gobject-introspection"
    description = "GObject introspection is a middleware layer between C libraries (using GObject) and language bindings"
    topics = ("conan", "gobject-instrospection")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/gobject-introspection"
    license = "LGPL-2.1"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    generators = "pkg_config"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os == "Windows":
            raise ConanInvalidConfiguration("%s recipe does not support windows. Contributions are welcome!" % self.name)

    def build_requirements(self):
        self.build_requires("meson/0.56.2")
        self.build_requires("pkgconf/1.7.3")
        if self.settings.os == "Windows":
            self.build_requires("winflexbison/2.5.22")
        else:
            self.build_requires("flex/2.6.4")
            self.build_requires("bison/3.7.1")

    def requirements(self):
        self.requires("glib/2.67.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        defs = dict()
        defs["build_introspection_data"] = self.options["glib"].shared

        meson.configure(
            source_folder=self._source_subfolder,
            args=["--wrap-mode=nofallback"],
            build_folder=self._build_subfolder,
            defs=defs,
        )
        return meson

    def build(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "meson.build"),
            "subdir('tests')",
            "#subdir('tests')",
        )
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "meson.build"),
            "if meson.version().version_compare('>=0.54.0')",
            "if false",
        )

        with tools.environment_append(
            VisualStudioBuildEnvironment(self).vars
            if self._is_msvc
            else {"PKG_CONFIG_PATH": self.build_folder}
        ):
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        with tools.environment_append(
            VisualStudioBuildEnvironment(self).vars
        ) if self._is_msvc else tools.no_op():
            meson = self._configure_meson()
            meson.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        shutil.move(
            os.path.join(self.package_folder, "share"),
            os.path.join(self.package_folder, "res"),
        )
        for pdb_file in glob.glob(os.path.join(self.package_folder, "bin", "*.pdb")):
            os.unlink(pdb_file)

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "gobject-introspection-1.0"
        self.cpp_info.libs = ["girepository-1.0"]
        self.cpp_info.includedirs.append(
            os.path.join("include", "gobject-introspection-1.0")
        )

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)
