from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc
import os
import textwrap

required_conan_version = ">=1.53.0"


class UlfiusConan(ConanFile):
    name = "ulfius"
    description = "Web Framework to build REST APIs, Webservices or any HTTP endpoint in C language"
    homepage = "https://github.com/babelouest/ulfius"
    topics = ("web", "http", "rest", "endpoint", "json", "websocket")
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_websockets": [True, False],
        "with_gnutls": [True, False],
        "with_jansson": [True, False],
        "with_libcurl": [True, False],
        "with_yder": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_websockets": True,
        "with_gnutls": True,
        "with_jansson": True,
        "with_libcurl": True,
        "with_yder": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            # INSTALL.md says that websockets are not supported on Windows
            del self.options.enable_websockets
            del self.options.fPIC

    def validate(self):
        if self.options.get_safe("enable_websockets") and not self.options.with_gnutls:
            raise ConanInvalidConfiguration(f"{self.ref} requires -o=&:with_gnutls=True when -o=&:enable_websockets=True")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def requirements(self):
        self.requires("orcania/2.3.3", transitive_headers=True)
        self.requires("libmicrohttpd/0.9.75", transitive_headers=True)
        if self.options.with_yder:
            self.requires("yder/1.4.18", transitive_headers=True)
        if self.options.with_jansson:
            self.requires("jansson/2.14", transitive_headers=True)
        if self.options.with_libcurl:
            self.requires("libcurl/[>=7.78.0 <9]")
        if self.options.with_gnutls:
            # Used in public ulfius.h:43
            self.requires("gnutls/3.8.2", transitive_headers=True)
        if self.options.get_safe("enable_websockets"):
            self.requires("zlib/[>=1.2.11 <2]")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.variables["DOWNLOAD_DEPENDENCIES"] = False
        tc.variables["WITH_GNUTLS"] = self.options.with_gnutls
        tc.variables["WITH_WEBSOCKET"] = self.options.get_safe("enable_websockets")
        tc.variables["WITH_CURL"] = self.options.with_libcurl
        tc.variables["WITH_JANSSON"] = self.options.with_jansson

        # Compilation issues when setting Ulifus as a dependency internally
        tc.variables["BUILD_UWSC"] = False

        tc.generate()

        deps = CMakeDeps(self)

        deps.set_property("libmicrohttpd", "cmake_file_name", "MHD")
        deps.set_property("libmicrohttpd", "cmake_target_name", "MHD::MHD")

        # Orcania generates -static targets for static libraries, but Ulfius does not check for them,
        # unconditionally set the target name to Orcania::Orcania
        deps.set_property("orcania", "cmake_target_name", "Orcania::Orcania")

        # Same for Yder
        if self.options.with_yder:
            deps.set_property("yder", "cmake_target_name", "Yder::Yder")

        if self.options.with_jansson:
            deps.set_property("jansson", "cmake_file_name", "Jansson")
            deps.set_property("jansson", "cmake_target_name", "Jansson::Jansson")

        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", os.path.join(self.source_folder), os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

        save(self, os.path.join(self.package_folder, self._variable_file_rel_path),
            textwrap.dedent(f"""\
                set(ULFIUS_VERSION_STRING "{self.version}")
           """))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {} if self.options.shared else {"Ulfius::Ulfius-static": "Ulfius::Ulfius"}
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """)
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @property
    def _variable_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    def package_info(self):
        libname = "ulfius"
        if is_msvc(self) and not self.options.shared:
            libname += "-static"
        self.cpp_info.libs = [libname]

        target_name = "Ulfius::Ulfius" if self.options.shared else "Ulfius::Ulfius-static"
        self.cpp_info.set_property("cmake_file_name", "Ulfius")
        self.cpp_info.set_property("cmake_target_name", target_name)
        self.cpp_info.set_property("pkg_config_name", "libulfius")
        self.cpp_info.set_property("cmake_build_modules", [self._variable_file_rel_path])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Ulfius"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Ulfius"
        self.cpp_info.names["cmake_find_package"] = "Ulfius"
        self.cpp_info.names["cmake_find_package_multi"] = "Ulfius"
        self.cpp_info.names["pkg_config"] = "libulfius"
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path, self._variable_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path, self._variable_file_rel_path]
