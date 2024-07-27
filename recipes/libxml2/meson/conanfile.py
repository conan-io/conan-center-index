import os
import textwrap

from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, rm, rmdir, save
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
from conan.tools.microsoft import is_msvc

required_conan_version = ">=1.55.0"


class Libxml2Conan(ConanFile):
    name = "libxml2"
    package_type = "library"
    url = "https://github.com/conan-io/conan-center-index"
    description = "libxml2 is a software library for parsing XML documents"
    topics = "xml", "parser", "validation"
    homepage = "https://gitlab.gnome.org/GNOME/libxml2/-/wikis/"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    default_options = {
        "shared": False,
        "fPIC": True,
        "c14n": True,
        "catalog": True,
        "ftp": True,
        "http": True,
        "html": True,
        "iconv": True,
        "icu": False,
        "iso8859x": True,
        "legacy": True,
        "output": True,
        "pattern": True,
        "push": True,
        "python": False,
        "reader": True,
        "regexps": True,
        "sax1": True,
        "schemas": True,
        "schematron": True,
        "threads": True,
        "tree": True,
        "valid": True,
        "writer": True,
        "xinclude": True,
        "xpath": True,
        "xptr": True,
        "zlib": True,
        "lzma": False,
    }
    options = {name: [True, False] for name in default_options.keys()}

    @property
    def _boolean_option_names(self):
        return ["c14n", "catalog", "ftp", "http", "html", "iso8859x", "legacy", "output", "pattern", "push", "python", "reader", "regexps", "sax1", "schemas", "schematron", "tree", "valid", "writer", "xinclude", "xpath", "xptr"]

    @property
    def _feature_option_names(self):
        return ["iconv", "icu", "lzma", "threads", "zlib"]

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
        if self.options.zlib:
            self.requires("zlib/[>=1.2.11 <2]")
        if self.options.lzma:
            self.requires("xz_utils/5.4.5")
        if self.options.iconv:
            self.requires("libiconv/1.17", transitive_headers=True, transitive_libs=True)
        if self.options.icu:
            self.requires("icu/73.2")

    def build_requirements(self):
        self.tool_requires("meson/[>=1.5.0 <2]")
        if not self.conf.get("tools.gnu:pkg_config", check_type=str):
            self.tool_requires("pkgconf/2.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        def feature(option):
            return "enabled" if self.options.get_safe(option) else "disabled"

        env = VirtualBuildEnv(self)
        env.generate()

        tc = MesonToolchain(self)
        tc.project_options["auto_features"] = "disabled"
        for option in self._boolean_option_names:
            tc.project_options[option] = self.options.get_safe(option)
        for option in self._feature_option_names:
            tc.project_options[option] = feature(option)
        tc.generate()

        tc = PkgConfigDeps(self)
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", self.source_folder, os.path.join(self.package_folder, "licenses"), ignore_case=True, keep_path=False)
        copy(self, "Copyright", self.source_folder, os.path.join(self.package_folder, "licenses"), ignore_case=True, keep_path=False)
        meson = Meson(self)
        meson.install()
        rm(self, "*.la", os.path.join(self.package_folder, "lib"))
        rm(self, "*.sh", os.path.join(self.package_folder, "lib"))
        rm(self, "run*", os.path.join(self.package_folder, "bin"))
        rm(self, "test*", os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        fix_apple_shared_install_name(self)

        for header in ["win32config.h", "wsockcompat.h"]:
            copy(self, header, os.path.join(self.source_folder, "include"),
                    os.path.join(self.package_folder, "include", "libxml2"), keep_path=False)

        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_file_rel_path)
        )

    def _create_cmake_module_variables(self, module_file):
        # FIXME: also define LIBXML2_XMLLINT_EXECUTABLE variable
        content = textwrap.dedent(f"""\
            set(LibXml2_FOUND TRUE)
            set(LIBXML2_FOUND TRUE)
            if(DEFINED LibXml2_INCLUDE_DIRS)
                set(LIBXML2_INCLUDE_DIR ${{LibXml2_INCLUDE_DIRS}})
                set(LIBXML2_INCLUDE_DIRS ${{LibXml2_INCLUDE_DIRS}})
            elseif(DEFINED libxml2_INCLUDE_DIRS)
                set(LIBXML2_INCLUDE_DIR ${{libxml2_INCLUDE_DIRS}})
                set(LIBXML2_INCLUDE_DIRS ${{libxml2_INCLUDE_DIRS}})
            endif()
            if(DEFINED LibXml2_LIBRARIES)
                set(LIBXML2_LIBRARIES ${{LibXml2_LIBRARIES}})
                set(LIBXML2_LIBRARY ${{LibXml2_LIBRARIES}})
            elseif(DEFINED libxml2_LIBRARIES)
                set(LIBXML2_LIBRARIES ${{libxml2_LIBRARIES}})
                set(LIBXML2_LIBRARY ${{libxml2_LIBRARIES}})
            endif()
            if(DEFINED LibXml2_DEFINITIONS)
                set(LIBXML2_DEFINITIONS ${{LibXml2_DEFINITIONS}})
            elseif(DEFINED libxml2_DEFINITIONS)
                set(LIBXML2_DEFINITIONS ${{libxml2_DEFINITIONS}})
            else()
                set(LIBXML2_DEFINITIONS "")
            endif()
            set(LIBXML2_VERSION_STRING "{self.version}")
        """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        # FIXME: Provide LibXml2::xmllint & LibXml2::xmlcatalog imported target for executables
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "LibXml2")
        self.cpp_info.set_property("cmake_file_name", "libxml2")
        self.cpp_info.set_property("cmake_target_name", "LibXml2::LibXml2")
        self.cpp_info.set_property("cmake_build_modules", [self._module_file_rel_path])
        self.cpp_info.set_property("pkg_config_name", "libxml-2.0")
        prefix = "lib" if is_msvc(self) else ""
        suffix = "_a" if is_msvc(self) and not self.options.shared else ""
        self.cpp_info.libs = [f"{prefix}xml2{suffix}"]
        self.cpp_info.includedirs.append(os.path.join("include", "libxml2"))
        if not self.options.shared:
            self.cpp_info.defines = ["LIBXML_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD", "Android"]:
            self.cpp_info.system_libs.append("m")
            if self.options.threads and self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("pthread")
            if self.settings.os in ["Linux", "FreeBSD"]:
                self.cpp_info.system_libs.append("dl")
        elif self.settings.os == "Windows":
            if self.options.ftp or self.options.http:
                self.cpp_info.system_libs.extend(["ws2_32", "wsock32"])

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.filenames["cmake_find_package"] = "LibXml2"
        self.cpp_info.filenames["cmake_find_package_multi"] = "libxml2"
        self.cpp_info.names["cmake_find_package"] = "LibXml2"
        self.cpp_info.names["cmake_find_package_multi"] = "LibXml2"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "libxml-2.0"
