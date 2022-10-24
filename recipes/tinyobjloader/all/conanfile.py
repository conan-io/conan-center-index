from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, get, export_conandata_patches, load, replace_in_file, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.52.0"


class TinyObjLoaderConan(ConanFile):
    name = "tinyobjloader"
    description = "Tiny but powerful single file wavefront obj loader"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/syoyo/tinyobjloader"
    topics = ("loader", "obj", "3d", "wavefront", "geometry")

    settings = "os", "arch", "build_type", "compiler"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "double": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "double": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            try:
                del self.options.fPIC
            except Exception:
                pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["TINYOBJLOADER_USE_DOUBLE"] = self.options.double
        tc.variables["TINYOBJLOADER_BUILD_TEST_LOADER"] = False
        if Version(self.version) < "1.0.7":
            tc.variables["TINYOBJLOADER_COMPILATION_SHARED"] = self.options.shared
        tc.variables["TINYOBJLOADER_BUILD_OBJ_STICHER"] = False
        tc.variables["CMAKE_INSTALL_DOCDIR"] = "licenses"
        if Version(self.version).major < 2:
            tc.variables["CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS"] = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "tinyobjloader"))
        self._remove_implementation(os.path.join(self.package_folder, "include", "tiny_obj_loader.h"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        cmake_target = "tinyobjloader_double" if self.options.double else "tinyobjloader"
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {cmake_target: "tinyobjloader::tinyobjloader"}
        )

    def _remove_implementation(self, header_fullpath):
        header_content = load(self, header_fullpath)
        begin = header_content.find("#ifdef TINYOBJLOADER_IMPLEMENTATION")
        implementation = header_content[begin:-1]
        replace_in_file(self, header_fullpath, implementation, "")

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

    def package_info(self):
        suffix = "_double" if self.options.double else ""
        self.cpp_info.set_property("cmake_file_name", "tinyobjloader")
        self.cpp_info.set_property("cmake_target_name", f"tinyobjloader::tinyobjloader{suffix}")
        self.cpp_info.set_property("cmake_target_aliases", [f"tinyobjloader{suffix}"]) # old target (before 1.0.7)
        self.cpp_info.set_property("pkg_config_name", f"tinyobjloader{suffix}")
        self.cpp_info.libs = [f"tinyobjloader{suffix}"]
        if self.options.double:
            self.cpp_info.defines.append("TINYOBJLOADER_USE_DOUBLE")

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
