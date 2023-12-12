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
        "enable_websockets": False,  # FIXME: should be True (cannot be True because of missing gnutls recipe)
        "with_gnutls": False,  # FIXME: should be True
        "with_jansson": True,
        "with_libcurl": True,
        "with_yder": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.enable_websockets = False
            del self.options.fPIC

    def validate(self):
        if self.options.with_gnutls:
            raise ConanInvalidConfiguration("with_gnutls=True is not yet implemented due to missing gnutls CCI recipe")
        if self.settings.os == "Windows" and self.options.enable_websockets:
            raise ConanInvalidConfiguration("ulfius does not support with_websockets=True on Windows")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def requirements(self):
        self.requires("orcania/2.3.1", transitive_headers=True)
        self.requires("libmicrohttpd/0.9.75", transitive_headers=True)
        if self.options.with_yder:
            self.requires("yder/1.4.18", transitive_headers=True)
        if self.options.with_jansson:
            self.requires("jansson/2.14", transitive_headers=True)
        if self.options.with_libcurl:
            self.requires("libcurl/[>=7.78.0 <9]")

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
        tc.variables["WITH_WEBSOCKETS"] = self.options.enable_websockets
        tc.variables["WITH_CURL"] = self.options.with_libcurl
        tc.variables["WITH_JANSSON"] = self.options.with_jansson
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

        # https://github.com/conan-io/conan/issues/12367 + move this before running CMakeDeps.generate()
        save(self, os.path.join(self.generators_folder, "MHDConfig.cmake"), textwrap.dedent(f"""\
            include(CMakeFindDependencyMacro)
            find_dependency(libmicrohttpd)

            set(MHD_FOUND TRUE)
            add_library(MHD::MHD INTERFACE IMPORTED)
            set_target_properties(MHD::MHD PROPERTIES INTERFACE_LINK_LIBRARIES "libmicrohttpd::libmicrohttpd")
            set(MHD_VERSION_STRING {self.dependencies['libmicrohttpd'].ref.version})
        """))
        save(self, os.path.join(self.generators_folder, "MHDConfigVersion.cmake"), textwrap.dedent(f"""\
            set(PACKAGE_VERSION "{ self.dependencies['libmicrohttpd'].ref.version }")

            if(PACKAGE_VERSION VERSION_LESS PACKAGE_FIND_VERSION)
                set(PACKAGE_VERSION_COMPATIBLE FALSE)
            else()
                set(PACKAGE_VERSION_COMPATIBLE TRUE)
                if(PACKAGE_FIND_VERSION STREQUAL PACKAGE_VERSION)
                    set(PACKAGE_VERSION_EXACT TRUE)
                endif()
            endif()
        """))

        # Shared ulfius looks for Orcania::Orcania and Yder::Yder
        # Static ulfius looks for Orcania::Orcania-static and Yder::Yder-static
        if self.options.shared:
            if not self.dependencies["orcania"].options.shared:
                save(self, os.path.join(self.generators_folder, "OrcaniaConfig.cmake"), textwrap.dedent("""\
                    add_library(Orcania::Orcania INTERFACE IMPORTED)
                    set_target_properties(Orcania::Orcania PROPERTIES INTERFACE_LINK_LIBRARIES "Orcania::Orcania-static")
                """), append=True)
            if self.options.with_yder and not self.dependencies["yder"].options.shared:
                save(self, os.path.join(self.generators_folder, "YderConfig.cmake"), textwrap.dedent("""\
                    add_library(Yder::Yder INTERFACE IMPORTED)
                    set_target_properties(Yder::Yder PROPERTIES INTERFACE_LINK_LIBRARIES "Yder::Yder-static")
                """), append=True)

        # Create Jansson::Jansson
        if self.options.with_jansson:
            save(self, os.path.join(self.generators_folder, "jansson-config.cmake"), textwrap.dedent(f"""\
                add_library(Jansson::Jansson INTERFACE IMPORTED)
                set_target_properties(Jansson::Jansson PROPERTIES INTERFACE_LINK_LIBRARIES "jansson::jansson")
                set(JANSSON_VERSION_STRING {self.dependencies['jansson'].ref.version})
            """), append=True)

        if self.options.with_gnutls:
            # FIXME: make sure gnutls creates GnuTLSCOnfig.cmake + GnuTLS::GnuTLS target + GNUTLS_VERSION_STRING
            pass

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
