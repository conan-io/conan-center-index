from conans import ConanFile, Meson, tools
from conan.tools.files import rename
from conans.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import shutil
import os


class LibXMLPlusPlus(ConanFile):
    # FIXME: naming the library "libxml++" causes conan not to add it to the
    # environment path on windows
    name = "libxmlpp"
    homepage = "https://github.com/libxmlplusplus/libxmlplusplus"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxml++ (a.k.a. libxmlplusplus) provides a C++ interface to XML files"
    topics = ["xml", "parser", "wrapper"]
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    generators = "pkg_config"
    exports_sources = "patches/**"

    def validate(self):
        if hasattr(self, "settings_build") and tools.cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def build_requirements(self):
        self.build_requires("meson/0.59.1")
        self.build_requires("pkgconf/1.7.4")

    def requirements(self):
        self.requires("libxml2/2.9.14")
        self.requires("glibmm/2.66.4")

    def source(self):
        tools.get(
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder,
        )

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

        if is_msvc(self):
            # when using cpp_std=c++NM the /permissive- flag is added which
            # attempts enforcing standard conformant c++ code. the problem is
            # that older versions of the Windows SDK isn't standard conformant!
            # see:
            # https://developercommunity.visualstudio.com/t/error-c2760-in-combaseapih-with-windows-sdk-81-and/185399
            tools.replace_in_file(
                os.path.join(self._source_subfolder, "meson.build"),
                "cpp_std=c++", "cpp_std=vc++")

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def _configure_meson(self):
        meson = Meson(self)
        defs = {
            "build-examples": "false",
            "build-tests": "false",
            "build-documentation": "false",
            "msvc14x-parallel-installable": "false",
            "default_library": "shared" if self.options.shared else "static",
        }
        meson.configure(
            defs=defs,
            build_folder=self._build_subfolder,
            source_folder=self._source_subfolder,
            pkg_config_paths=[self.install_folder],
        )
        return meson

    def build(self):
        self._patch_sources()
        with tools.environment_append(tools.RunEnvironment(self).vars):
            meson = self._configure_meson()
            meson.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()

        shutil.move(
            os.path.join(self.package_folder, "lib", "libxml++-2.6",
                         "include", "libxml++config.h"),
            os.path.join(self.package_folder, "include", "libxml++-2.6",
                         "libxml++config.h"))

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "libxml++-2.6"))

        if is_msvc(self):
            tools.remove_files_by_mask(
                os.path.join(self.package_folder, "bin"), "*.pdb")
            if not self.options.shared:
                rename(
                    self,
                    os.path.join(self.package_folder, "lib", "libxml++-2.6.a"),
                    os.path.join(self.package_folder, "lib", "xml++-2.6.lib"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "libxml++"
        self.cpp_info.names["cmake_find_package_multi"] = "libxml++"
        self.cpp_info.names["pkg_config"] = "libxml++"

        self.cpp_info.components["libxml++-2.6"].names[
            "pkg_config"] = "libxml++-2.6"
        self.cpp_info.components["libxml++-2.6"].libs = ["xml++-2.6"]
        self.cpp_info.components["libxml++-2.6"].includedirs = [
            os.path.join("include", "libxml++-2.6")
        ]
        self.cpp_info.components["libxml++-2.6"].requires = [
                "glibmm::glibmm-2.4", "libxml2::libxml2"
        ]
