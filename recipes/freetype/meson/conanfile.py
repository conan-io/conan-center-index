from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.files import (
    apply_conandata_patches, copy, export_conandata_patches, load,
    get, rename, replace_in_file, rm, rmdir, save
)
from conan.tools.env import VirtualBuildEnv
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.scm import Version
import os
import re
import shutil
import textwrap

required_conan_version = ">=1.53.0"


class FreetypeConan(ConanFile):
    name = "freetype"
    description = "FreeType is a freely available software library to render fonts."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.freetype.org"
    license = "FTL"
    topics = ("freetype", "fonts")
    package_type = "library"
    short_paths = True
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_png": [True, False],
        "with_zlib": [True, False],
        "with_bzip2": [True, False],
        "with_brotli": [True, False],
        "subpixel": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_png": True,
        "with_zlib": True,
        "with_bzip2": True,
        "with_brotli": True,
        "subpixel": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.with_zlib:
            self.requires("zlib/[>=1.2.10 <2]")
        if self.options.with_bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.get_safe("with_brotli"):
            self.requires("brotli/1.1.0")

    def build_requirements(self):
        self.tool_requires("meson/1.3.2")
        if not self.conf.get("tools.gnu:pkg_config", default=False, check_type=str):
            self.tool_requires("pkgconf/2.1.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        virtual_build_env = VirtualBuildEnv(self)
        virtual_build_env.generate()
        deps = PkgConfigDeps(self)
        deps.generate()

        def feature(option):
            return "enabled" if option else "disabled"

        tc = MesonToolchain(self)
        tc.project_options["brotli"] = feature(self.options.with_brotli)
        tc.project_options["bzip2"] = feature(self.options.with_bzip2)
        # Harfbuzz support introduces a circular dependency between Harfbuzz and Freetype.
        # They both have options to require each other.
        tc.project_options["harfbuzz"] = "disabled"
        tc.project_options["png"] = feature(self.options.with_png)
        tc.project_options["tests"] = "disabled"
        tc.project_options["zlib"] = "system" if self.options.with_zlib else "disabled"
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        config_h = os.path.join(self.source_folder, "include", "freetype", "config", "ftoption.h")
        if self.options.subpixel:
            replace_in_file(self, config_h, "/* #define FT_CONFIG_OPTION_SUBPIXEL_RENDERING */", "#define FT_CONFIG_OPTION_SUBPIXEL_RENDERING")

    def build(self):
        self._patch_sources()
        meson = Meson(self)
        meson.configure()
        meson.build()

    def _make_freetype_config(self, version):
        freetype_config_in = os.path.join(self.source_folder, "builds", "unix", "freetype-config.in")
        if not os.path.isdir(os.path.join(self.package_folder, "bin")):
            os.makedirs(os.path.join(self.package_folder, "bin"))
        freetype_config = os.path.join(self.package_folder, "bin", "freetype-config")
        rename(self, freetype_config_in, freetype_config)
        staticlibs = "-lm -lfreetype" if self.settings.os == "Linux" else "-lfreetype"
        replace_in_file(self, freetype_config, r"%PKG_CONFIG%", r"/bin/false")  # never use pkg-config
        replace_in_file(self, freetype_config, r"%prefix%", r"$conan_prefix")
        replace_in_file(self, freetype_config, r"%exec_prefix%", r"$conan_exec_prefix")
        replace_in_file(self, freetype_config, r"%includedir%", r"$conan_includedir")
        replace_in_file(self, freetype_config, r"%libdir%", r"$conan_libdir")
        replace_in_file(self, freetype_config, r"%ft_version%", r"$conan_ftversion")
        replace_in_file(self, freetype_config, r"%LIBSSTATIC_CONFIG%", r"$conan_staticlibs")
        replace_in_file(self, freetype_config, r"export LC_ALL", textwrap.dedent("""\
            export LC_ALL
            BINDIR=$(dirname $0)
            conan_prefix=$(dirname $BINDIR)
            conan_exec_prefix=${{conan_prefix}}/bin
            conan_includedir=${{conan_prefix}}/include
            conan_libdir=${{conan_prefix}}/lib
            conan_ftversion={version}
            conan_staticlibs="{staticlibs}"
        """).format(version=version, staticlibs=staticlibs))

    def _extract_libtool_version(self):
        conf_raw = load(self, os.path.join(self.source_folder, "builds", "unix", "configure.raw"))
        return re.search(r"^version_info='([0-9:]+)'", conf_raw, flags=re.M).group(1).replace(":", ".")

    @property
    def _libtool_version_txt(self):
        return os.path.join(self.package_folder, "res", "freetype-libtool-version.txt")

    def package(self):
        meson = Meson(self)
        meson.install()

        # As a workaround to support versions of CMake before 3.29, rename the libfreetype.a static library to freetype.lib on Windows.
        if self.settings.os == "Windows" and not self.options.shared:
            rename(self, os.path.join(self.package_folder, "lib", "libfreetype.a"), os.path.join(self.package_folder, "lib", "freetype.lib"))

        ver = Version(self.version)
        if self.settings.os == "Windows" and self.options.shared and ver >= "2.13.0" and ver < "2.14.0":
            # Duplicate DLL name for backwards compatibility with earlier recipe revisions
            # See https://github.com/conan-io/conan-center-index/issues/23768
            suffix = "d" if self.settings.build_type == "Debug" else ""
            src = os.path.join(self.package_folder, "bin", "freetype-6.dll")
            dst = os.path.join(self.package_folder, "bin", f"freetype{suffix}.dll")
            shutil.copyfile(src, dst)

        libtool_version = self._extract_libtool_version()

        save(self, self._libtool_version_txt, libtool_version)
        self._make_freetype_config(libtool_version)

        doc_folder = os.path.join(self.source_folder, "docs")
        license_folder = os.path.join(self.package_folder, "licenses")
        copy(self, "FTL.TXT", doc_folder, license_folder)
        copy(self, "GPLv2.TXT", doc_folder, license_folder)
        copy(self, "LICENSE.TXT", doc_folder, license_folder)

        rm(self, "*.pdb", os.path.join(self.package_folder, "bin"))

        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_vars_rel_path)
        )
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_target_rel_path),
            {"freetype": "Freetype::Freetype"}
        )

        fix_apple_shared_install_name(self)

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent(f"""\
            set(FREETYPE_FOUND TRUE)
            if(DEFINED Freetype_INCLUDE_DIRS)
                set(FREETYPE_INCLUDE_DIRS ${{Freetype_INCLUDE_DIRS}})
            endif()
            if(DEFINED Freetype_LIBRARIES)
                set(FREETYPE_LIBRARIES ${{Freetype_LIBRARIES}})
            endif()
            set(FREETYPE_VERSION_STRING "{self.version}")
        """)
        save(self, module_file, content)

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        save(self, module_file, content)

    @property
    def _module_vars_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    @property
    def _module_target_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @staticmethod
    def _chmod_plus_x(filename):
        if os.name == "posix" and (os.stat(filename).st_mode & 0o111) != 0o111:
            os.chmod(filename, os.stat(filename).st_mode | 0o111)

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "Freetype")
        self.cpp_info.set_property("cmake_file_name", "freetype")
        self.cpp_info.set_property("cmake_target_name", "Freetype::Freetype")
        self.cpp_info.set_property("cmake_target_aliases", ["freetype"]) # other possible target name in upstream config file
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_rel_path])
        self.cpp_info.set_property("pkg_config_name", "freetype2")
        self.cpp_info.libs = ["freetype"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
        self.cpp_info.includedirs.append(os.path.join("include", "freetype2"))

        libtool_version = load(self, self._libtool_version_txt).strip()
        self.conf_info.define("user.freetype:libtool_version", libtool_version)
        self.cpp_info.set_property("system_package_version", libtool_version)

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.set_property("component_version", libtool_version)
        self.cpp_info.filenames["cmake_find_package"] = "Freetype"
        self.cpp_info.filenames["cmake_find_package_multi"] = "freetype"
        self.cpp_info.names["cmake_find_package"] = "Freetype"
        self.cpp_info.names["cmake_find_package_multi"] = "Freetype"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_vars_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_target_rel_path]
        self.cpp_info.names["pkg_config"] = "freetype2"
        freetype_config = os.path.join(self.package_folder, "bin", "freetype-config")
        self.env_info.PATH.append(os.path.join(self.package_folder, "bin"))
        self.env_info.FT2_CONFIG = freetype_config
        self._chmod_plus_x(freetype_config)
        self.user_info.LIBTOOL_VERSION = libtool_version
