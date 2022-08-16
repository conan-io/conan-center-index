import os
import re

from conan.tools.microsoft import is_msvc
from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration

required_conan_version = ">=1.33.0"


class GtkmmConan(ConanFile):
    name = "gtkmm"
    description = "gtkmm is the official C++ interface for the popular GUI library GTK"
    topics = ("gtk", "widgets")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.gtkmm.org"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False]
        }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if is_msvc(self):
            # Static builds not supported by MSVC
            self.options.shared = True

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        self.options["cairo"].with_glib = True

    @property
    def _minimum_cpp_standard(self):
        return 17

    @property
    def _minimum_compilers_version(self):
        return {
            "Visual Studio": "16",
            "gcc": "7",
            "clang": "6",
            "apple-clang": "10",
        }

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimum_cpp_standard)
        min_version = self._minimum_compilers_version.get(str(self.settings.compiler))
        if not min_version:
            self.output.warn("{} recipe lacks information about the {} compiler support.".format(
                self.name, self.settings.compiler))
        else:
            if tools.Version(self.settings.compiler.version) < min_version:
                raise ConanInvalidConfiguration("{} requires C++{} support. The current compiler {} {} does not support it.".format(
                    self.name, self._minimum_cpp_standard, self.settings.compiler, self.settings.compiler.version))

    def build_requirements(self):
        self.build_requires("meson/0.62.2")
        self.build_requires("pkgconf/1.7.4")

    def requirements(self):
        self.requires("cairomm/1.16.1@")
        # gtkmm has a direct dependency on cairo-gobject which is not explicit in the meson configuration
        self.requires("cairo/1.17.4")
        self.requires("glibmm/2.72.1")
        self.requires("glib/2.73.0")
        self.requires("gtk/4.7.0")
        self.requires("libsigcpp/3.0.7")
        self.requires("pangomm/2.50.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        if is_msvc(self):
            for patch in self.conan_data.get("patches", {}).get(self.version, []):
                tools.patch(**patch)

    def _configure_meson(self):
        meson = Meson(self)
        defs = {
            "build-demos": 'false',
            "build-tests": 'false'
        }
        args=[]
        args.append("--wrap-mode=nofallback")
        meson.configure(
            defs=defs,
            build_folder=self._build_subfolder,
            source_folder=self._source_subfolder,
            pkg_config_paths=[self.install_folder],
            args=args
        )
        return meson

    def build(self):
        self._patch_sources()
        with tools.environment_append(tools.RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.build()

    def _get_msvc_toolset(self):
        if self.settings.compiler.get_safe("toolset"):
            return self.settings.compiler.toolset

        version = str(self.settings.compiler.version)
        toolset_map = {
            "15": "v141",
            "16": "v142",
            "17": "v143"
        }
        if version in toolset_map:
            return toolset_map.get(version)

        raise ConanInvalidConfiguration("Cannot get MSVC compiler toolset information")

    @property
    def _msvc_toolset_suffix(self):
        toolset = self._get_msvc_toolset()
        match = re.match("v([0-9]+)", str(toolset))
        if match is not None:
            return f"vc{match.group(1)}"

        raise ConanInvalidConfiguration("Cannot get MSVC compiler toolset information")

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        with tools.environment_append({
            "PKG_CONFIG_PATH": self.install_folder,
            "PATH": [os.path.join(self.package_folder, "bin")]}):
            meson.install()

        self.copy(pattern="COPYING", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "*.pdb")
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.pdb")

    @property
    def _libname(self):
        if is_msvc(self):
            return f"gtkmm-{self._msvc_toolset_suffix}-4.0"
        return "gtkmm-4.0"

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "gtkmm-4.0")
        self.cpp_info.names["pkg_config"] = "gtkmm-4.0"

        self.cpp_info.requires = ["cairo::cairo-gobject"]
        self.cpp_info.libs = [self._libname]
        self.cpp_info.includedirs += [
            os.path.join("include", "gtkmm-4.0"),
            os.path.join("lib", "gtkmm-4.0", "include")
        ]
