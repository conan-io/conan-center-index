from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, collect_libs, get, copy, replace_in_file, save
from conan.tools.build import cross_building
import os
import textwrap

required_conan_version = ">=1.52.0"


class SzipConan(ConanFile):
    name = "szip"
    description = "C Implementation of the extended-Rice lossless compression " \
                  "algorithm, suitable for use with scientific data."
    license = "Szip License"
    topics = "compression", "decompression"
    homepage = "https://support.hdfgroup.org/doc_resource/SZIP/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "enable_encoding": [True, False],
        "enable_large_file": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "enable_encoding": False,
        "enable_large_file": True,
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
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                              "set (CMAKE_POSITION_INDEPENDENT_CODE ON)", "")
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SZIP_ENABLE_ENCODING"] = self.options.enable_encoding
        tc.variables["SZIP_EXTERNALLY_CONFIGURED"] = True
        tc.variables["BUILD_TESTING"] = False
        tc.variables["SZIP_BUILD_FRAMEWORKS"] = False
        tc.variables["SZIP_PACK_MACOSX_FRAMEWORK"] = False
        tc.variables["SZIP_ENABLE_LARGE_FILE"] = self.options.enable_large_file
        if cross_building(self, skip_x64_x86=True) and self.options.enable_large_file:
            # Assume it works, otherwise raise in 'validate' function
            tc.variables["TEST_LFS_WORKS_RUN"] = True
            tc.variables["TEST_LFS_WORKS_RUN__TRYRUN_OUTPUT"] = True
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"szip-shared" if self.options.shared else "szip-static": "szip::szip"}
        )

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
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "szip")
        self.cpp_info.set_property("cmake_target_name", "szip-shared" if self.options.shared else "szip-static")
        self.cpp_info.libs = collect_libs(self)

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["m"])

        if self.options.shared:
            self.cpp_info.defines.append("SZ_BUILT_AS_DYNAMIC_LIB=1")

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
