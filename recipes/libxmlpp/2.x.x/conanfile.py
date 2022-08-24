from conans import ConanFile, Meson, tools
from conan.tools.files import rename
from conan.errors import ConanInvalidConfiguration
from conan.tools.microsoft import is_msvc
import shutil
import os
import functools

required_conan_version = ">=1.45.0"

class LibXMLPlusPlus(ConanFile):
    # FIXME: naming the library "libxml++" causes conan not to add it to the
    # environment path on windows
    name = "libxmlpp"
    description = "libxml++ (a.k.a. libxmlplusplus) provides a C++ interface to XML files"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libxmlplusplus/libxmlplusplus"
    topics = ["xml", "parser", "wrapper"]
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "pkg_config"

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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("libxml2/2.9.14")
        if tools.scm.Version(self, self.version) <= "2.42.1":
            self.requires("glibmm/2.66.4")
        else:
            self.requires("glibmm/2.72.1")

    def validate(self):
        if hasattr(self, "settings_build") and tools.build.cross_building(self, self):
            raise ConanInvalidConfiguration("Cross-building not implemented")

        if self.settings.compiler.get_safe("cppstd"):
            tools.build.check_min_cppstd(self, self, 11)

    def build_requirements(self):
        self.build_requires("meson/0.63.0")
        self.build_requires("pkgconf/1.7.4")

    def source(self):
        tools.files.get(self, 
            **self.conan_data["sources"][self.version],
            strip_root=True,
            destination=self._source_subfolder,
        )

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

        if is_msvc(self):
            # when using cpp_std=c++NM the /permissive- flag is added which
            # attempts enforcing standard conformant c++ code. the problem is
            # that older versions of the Windows SDK isn't standard conformant!
            # see:
            # https://developercommunity.visualstudio.com/t/error-c2760-in-combaseapih-with-windows-sdk-81-and/185399
            tools.files.replace_in_file(self, 
                os.path.join(self._source_subfolder, "meson.build"),
                "cpp_std=c++", "cpp_std=vc++")

    @functools.lru_cache(1)
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
        lib_version = "2.6" if tools.scm.Version(self, self.version) <= "2.42.1" else "5.0"

        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()

        shutil.move(
            os.path.join(self.package_folder, "lib", f"libxml++-{lib_version}", "include", "libxml++config.h"),
            os.path.join(self.package_folder, "include", f"libxml++-{lib_version}", "libxml++config.h"))

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", f"libxml++-{lib_version}"))

        if is_msvc(self):
            tools.files.rm(self, 
                os.path.join(self.package_folder, "bin"), "*.pdb")
            if not self.options.shared:
                rename(
                    self,
                    os.path.join(self.package_folder, "lib", f"libxml++-{lib_version}.a"),
                    os.path.join(self.package_folder, "lib", f"xml++-{lib_version}.lib"))

    def package_info(self):
        lib_version = "2.6" if tools.scm.Version(self, self.version) <= "2.42.1" else "5.0"

        self.cpp_info.set_property("cmake_module_file_name", "libxml++")
        self.cpp_info.set_property("cmake_module_target_name", "libxml++::libxml++")
        self.cpp_info.set_property("pkg_config_name", "libxml++")
        self.cpp_info.components[f"libxml++-{lib_version}"].set_property("pkg_config_name", f"libxml++-{lib_version}")
        self.cpp_info.components[f"libxml++-{lib_version}"].libs = [f"xml++-{lib_version}"]
        self.cpp_info.components[f"libxml++-{lib_version}"].includedirs = [
            os.path.join("include", f"libxml++-{lib_version}")
        ]
        self.cpp_info.components[f"libxml++-{lib_version}"].requires = [
                "glibmm::glibmm", "libxml2::libxml2"
        ]

        self.cpp_info.names["cmake_find_package"] = "libxml++"
        self.cpp_info.names["cmake_find_package_multi"] = "libxml++"
        self.cpp_info.names["pkg_config"] = "libxml++"
        self.cpp_info.components[f"libxml++-{lib_version}"].names["pkg_config"] = f"libxml++-{lib_version}"
