from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.microsoft import is_msvc
import os
import textwrap

required_conan_version = ">=1.52.0"


class OrcaniaConan(ConanFile):
    name = "orcania"
    description = "Potluck with different functions for different purposes that can be shared among C programs"
    homepage = "https://github.com/babelouest/orcania"
    topics = ("utility", "functions", )
    license = "LGPL-2.1-or-later"
    url = "https://github.com/conan-io/conan-center-index"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_base64url": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_base64url": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def requirements(self):
        if is_msvc(self) and self.options.enable_base64url:
            self.requires("getopt-for-visual-studio/20200201")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_BASE64URL"] = self.options.enable_base64url
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.generate()
        deps = CMakeDeps(self)
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
                set(ORCANIA_VERSION_STRING "{self.version}")
           """))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {} if self.options.shared else {"Orcania::Orcania-static": "Orcania::Orcania"}
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
        libname = "orcania"
        if is_msvc(self) and not self.options.shared:
            libname += "-static"
        self.cpp_info.libs = [libname]

        target_name = "Orcania::Orcania" if self.options.shared else "Orcania::Orcania-static"
        self.cpp_info.set_property("cmake_file_name", "Orcania")
        self.cpp_info.set_property("cmake_target_name", target_name)
        self.cpp_info.set_property("cmake_module_file_name", "Orcania")
        self.cpp_info.set_property("cmake_module_target_name", target_name)
        self.cpp_info.set_property("pkg_config_name", "liborcania")
        self.cpp_info.set_property("cmake_build_modules", [self._variable_file_rel_path])

        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.filenames["cmake_find_package"] = "Orcania"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Orcania"
        self.cpp_info.names["cmake_find_package"] = "Orcania"
        self.cpp_info.names["cmake_find_package_multi"] = "Orcania"
        self.cpp_info.names["pkg_config"] = "liborcania"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path, self._variable_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path, self._variable_file_rel_path]
