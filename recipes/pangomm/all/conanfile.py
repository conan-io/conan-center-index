import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, cross_building
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rename, replace_in_file, rm, rmdir
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import MesonToolchain, Meson
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PangommConan(ConanFile):
    name = "pangomm"
    description = "pangomm is a C++ API for Pango: a library for layout and rendering of text."
    license = "LGPL-2.1"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://gitlab.gnome.org/GNOME/pangomm"
    topics = ["pango", "wrapper", "text rendering", "fonts", "freedesktop"]
    package_type = "library"
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
    def _is_2_48_api(self):
        return Version(self.version) >= "2.48.0"

    @property
    def _is_1_4_api(self):
        return "1.4.0" <= Version(self.version) < "2.48.0"

    @property
    def _api_version(self):
        return "2.48" if self._is_2_48_api else "1.4"

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
        self.requires("pango/1.51.0", transitive_headers=True, transitive_libs=True)
        if self._is_2_48_api:
            self.requires("glibmm/2.75.0", transitive_headers=True, transitive_libs=True)
            self.requires("cairomm/1.18.0", transitive_headers=True, transitive_libs=True)
        elif self._is_1_4_api:
            self.requires("glibmm/2.66.4", transitive_headers=True, transitive_libs=True)
            self.requires("cairomm/1.14.3", transitive_headers=True, transitive_libs=True)

    def validate(self):
        if hasattr(self, "settings_build") and cross_building(self):
            raise ConanInvalidConfiguration("Cross-building not implemented")

        if self.settings.compiler.get_safe("cppstd"):
            if self._is_2_48_api:
                check_min_cppstd(self, 17)
            elif self._is_1_4_api:
                check_min_cppstd(self, 11)

    def build_requirements(self):
        self.tool_requires("meson/1.3.1")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = PkgConfigDeps(self)
        tc.generate()
        tc = MesonToolchain(self)
        tc.project_options = {
            "build-documentation": "false",
            "msvc14x-parallel-installable": "false",
            "default_library": "shared" if self.options.shared else "static",
            "libdir": "lib",
        }
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

        # glibmm_generate_extra_defs library does not provide any standard way
        # for discovery, which is why pangomm uses "find_library" method instead
        # of "dependency". this patch adds a hint to where this library is
        glibmm_generate_extra_defs_dir = [
            os.path.join(self.dependencies["glibmm"].package_folder, libdir)
            for libdir in self.dependencies["glibmm"].cpp_info.libdirs
        ]

        replace_in_file(self, os.path.join(self.source_folder, "tools", "extra_defs_gen", "meson.build"),
            "required: glibmm_dep.type_name() != 'internal',",
            f"required: glibmm_dep.type_name() != 'internal', dirs: {glibmm_generate_extra_defs_dir}")

        if is_msvc(self):
            # when using cpp_std=c++NM the /permissive- flag is added which
            # attempts enforcing standard conformant c++ code
            # the problem is that older versions of Windows SDK is not standard
            # conformant! see:
            # https://developercommunity.visualstudio.com/t/error-c2760-in-combaseapih-with-windows-sdk-81-and/185399
            replace_in_file(self, os.path.join(self.source_folder, "meson.build"),
                            "cpp_std=c++",
                            "cpp_std=vc++")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        meson = Meson(self)
        meson.install()

        copy(self, "pangommconfig.h",
             dst=os.path.join(self.package_folder, "include", f"pangomm-{self._api_version}"),
             src=os.path.join(self.build_folder, "pango"))

        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", f"pangomm-{self._api_version}", "include"))

        if is_msvc(self):
            rm(self, "*.pdb", os.path.join(self.package_folder, "bin"), recursive=True)
            if not self.options.shared:
                rename(self, os.path.join(self.package_folder, "lib", f"libpangomm-{self._api_version}.a"),
                       os.path.join(self.package_folder, "lib", f"pangomm-{self._api_version}.lib"))

    def package_info(self):
        pangomm_lib = f"pangomm-{self._api_version}"
        glibmm_lib = "glibmm::glibmm-2.68" if self._is_2_48_api else "glibmm::glibmm-2.4"
        giomm_lib = "glibmm::giomm-2.68" if self._is_2_48_api else "glibmm::giomm-2.4"
        cairomm_lib = "cairomm::cairomm-1.16" if self._is_2_48_api else "cairomm::cairomm-1.0"

        self.cpp_info.components[pangomm_lib].set_property("pkg_config_name", pangomm_lib)
        self.cpp_info.components[pangomm_lib].libs = [pangomm_lib]
        self.cpp_info.components[pangomm_lib].includedirs = [os.path.join("include", pangomm_lib)]
        self.cpp_info.components[pangomm_lib].requires = ["pango::pangocairo", glibmm_lib, giomm_lib, cairomm_lib]
        self.cpp_info.components[pangomm_lib].set_property("pkg_config_custom_content", f"gmmprocm4dir=${{libdir}}/{pangomm_lib}/proc/m4")
