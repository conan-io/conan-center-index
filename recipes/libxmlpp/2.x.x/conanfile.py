import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class LibXMLPlusPlus(ConanFile):
    name = "libxmlpp"
    description = "libxml++ (a.k.a. libxmlplusplus) provides a C++ interface to XML files"
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/libxmlplusplus/libxmlplusplus"
    topics = ["xml", "parser", "wrapper"]

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libxml2/2.11.4", transitive_headers=True)
        if Version(self.version) <= "2.42.1":
            self.requires("glibmm/2.66.4")
        else:
            self.requires("glibmm/2.75.0")

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")

        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, 11)

    def build_requirements(self):
        self.tool_requires("meson/1.2.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/1.9.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = MesonToolchain(self)
        tc.project_options = {
            "build-examples": "false",
            "build-tests": "false",
            "build-documentation": "false",
            "msvc14x-parallel-installable": "false",
            "default_library": "shared" if self.options.shared else "static",
            "libdir": "lib",
        }
        tc.generate()

        tc = PkgConfigDeps(self)
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        if is_msvc(self):
            # when using cpp_std=c++NM the /permissive- flag is added which
            # attempts enforcing standard conformant c++ code. the problem is
            # that older versions of the Windows SDK isn't standard conformant!
            # see:
            # https://developercommunity.visualstudio.com/t/error-c2760-in-combaseapih-with-windows-sdk-81-and/185399
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"), "cpp_std=c++", "cpp_std=vc++")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    @property
    def _lib_version(self):
        return "2.6" if Version(self.version) <= "2.42.1" else "5.0"

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()

        copy(self, "libxml++config.h",
             dst=os.path.join(self.package_folder, "include", f"libxml++-{self._lib_version}"),
             src=self.build_folder)

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", f"libxml++-{self._lib_version}"))

        if is_msvc(self):
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"), recursive=True)
            if not self.options.shared:
                rename(self,
                       os.path.join(self.package_folder, "lib", f"libxml++-{self._lib_version}.a"),
                       os.path.join(self.package_folder, "lib", f"xml++-{self._lib_version}.lib"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libxml++")
        self.cpp_info.set_property("cmake_target_name", "libxml++::libxml++")
        self.cpp_info.set_property("pkg_config_name", "libxml++")

        main_component = self.cpp_info.components[f"libxml++-{self._lib_version}"]
        main_component.set_property("pkg_config_name", f"libxml++-{self._lib_version}")
        main_component.libs = [f"xml++-{self._lib_version}"]
        main_component.includedirs = [os.path.join("include", f"libxml++-{self._lib_version}")]
        main_component.requires = ["glibmm::glibmm", "libxml2::libxml2"]

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "libxml++"
        self.cpp_info.names["cmake_find_package_multi"] = "libxml++"
