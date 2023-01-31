from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, collect_libs, copy, export_conandata_patches, get, rmdir, save
import os
import textwrap

required_conan_version = ">=1.53.0"


class LibgeotiffConan(ConanFile):
    name = "libgeotiff"
    description = "Libgeotiff is an open source library normally hosted on top " \
                  "of libtiff for reading, and writing GeoTIFF information tags."
    license = ["MIT", "BSD-3-Clause"]
    topics = ("geotiff", "tiff")
    homepage = "https://github.com/OSGeo/libgeotiff"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
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
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("libtiff/4.4.0")
        self.requires("proj/9.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["WITH_UTILITIES"] = False
        tc.variables["WITH_TOWGS84"] = True
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "doc"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_vars_file)
        )
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_target_file),
            {"geotiff_library": "geotiff::geotiff"}
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent("""\
            set(GEOTIFF_FOUND ${GeoTIFF_FOUND})
            if(DEFINED GeoTIFF_INCLUDE_DIR)
                set(GEOTIFF_INCLUDE_DIR ${GeoTIFF_INCLUDE_DIR})
            endif()
            if(DEFINED GeoTIFF_LIBRARIES)
                set(GEOTIFF_LIBRARIES ${GeoTIFF_LIBRARIES})
            endif()
        """)
        save(self, module_file, content)

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
    def _module_vars_file(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    @property
    def _module_target_file(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_module_file_name", "GeoTIFF")
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_file])
        self.cpp_info.set_property("cmake_file_name", "geotiff")
        self.cpp_info.set_property("cmake_target_name", "geotiff_library")

        self.cpp_info.names["cmake_find_package"] = "GeoTIFF"
        self.cpp_info.names["cmake_find_package_multi"] = "geotiff"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_vars_file]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_target_file]

        self.cpp_info.libs = collect_libs(self)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
