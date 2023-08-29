from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, load, rm, rmdir, save
from conan.tools.microsoft import check_min_vs
from conan.tools.scm import Version
import glob
import os
import textwrap

required_conan_version = ">=1.53.0"


class EmbreeConan(ConanFile):
    name = "embree3"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("embree", "raytracing", "rendering")
    description = "Intel's collection of high-performance ray tracing kernels."
    homepage = "https://embree.github.io/"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "sse2": [True, False],
        "sse42": [True, False],
        "avx": [True, False],
        "avx2": [True, False],
        "avx512": [True, False],
        "neon": [True, False],
        "neon2x": [True, False],
        "geometry_curve": [True, False],
        "geometry_grid": [True, False],
        "geometry_instance": [True, False],
        "geometry_quad": [True, False],
        "geometry_subdivision": [True, False],
        "geometry_triangle": [True, False],
        "geometry_user": [True, False],
        "ray_packets": [True, False],
        "ray_masking": [True, False],
        "backface_culling": [True, False],
        "ignore_invalid_rays": [True, False],
        "with_tbb": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "sse2": True,
        "sse42": False,
        "avx": False,
        "avx2": False,
        "avx512": False,
        "neon": False,
        "neon2x": False,
        "geometry_curve": True,
        "geometry_grid": True,
        "geometry_instance": True,
        "geometry_quad": True,
        "geometry_subdivision": True,
        "geometry_triangle": True,
        "geometry_user": True,
        "ray_packets": True,
        "ray_masking": False,
        "backface_culling": False,
        "ignore_invalid_rays": False,
        "with_tbb": False,
    }

    @property
    def _has_sse_avx(self):
        return self.settings.arch in ["x86", "x86_64"]

    @property
    def _embree_has_neon_support(self):
        return Version(self.version) >= "3.13.0"

    @property
    def _embree_has_neon2x_support(self):
        return Version(self.version) >= "3.13.4"

    @property
    def _has_neon(self):
        return "arm" in self.settings.arch

    @property
    def _has_neon2x(self):
        return "arm" in self.settings.arch and is_apple_os(self)

    @property
    def _num_isa(self):
        num_isa = 0
        if self._has_neon:
            if self._embree_has_neon_support and self.options.neon:
                num_isa += 1
            if self._embree_has_neon2x_support and self.options.neon2x:
                num_isa += 1
        for simd_option in ["sse2", "sse42", "avx", "avx2", "avx512"]:
            if self.options.get_safe(simd_option):
                num_isa += 1
        return num_isa

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_sse_avx:
            del self.options.sse2
            del self.options.sse42
            del self.options.avx
            del self.options.avx2
            del self.options.avx512
        if not self._has_neon:
            del self.options.neon
            del self.options.neon2x
        else:
            if not self._embree_has_neon_support:
                del self.options.neon
            if not self._embree_has_neon2x_support:
                del self.options.neon2x

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_tbb:
            self.requires("onetbb/2021.7.0")

    def validate(self):
        if not (self._has_sse_avx or (self._embree_has_neon_support and self._has_neon)):
            raise ConanInvalidConfiguration(f"{self.ref} doesn't support {self.settings.arch}")

        compiler_version = Version(self.settings.compiler.version)
        if self.settings.compiler == "clang" and compiler_version < "4":
            raise ConanInvalidConfiguration("Clang < 4 is not supported")

        check_min_vs(self, 191)

        if self.settings.os == "Linux" and self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++":
            raise ConanInvalidConfiguration(f"{self.ref} cannot be built with clang libc++, use libstdc++ instead")

        if self.settings.compiler == "apple-clang" and not self.options.shared and compiler_version >= "9.0" and self._num_isa > 1:
            raise ConanInvalidConfiguration(f"{self.ref} static with apple-clang >=9 and multiple ISA (simd) is not supported")

        if self._num_isa == 0:
            raise ConanInvalidConfiguration("At least one ISA (simd) must be enabled")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["EMBREE_STATIC_LIB"] = not self.options.shared
        tc.variables["BUILD_TESTING"] = False
        tc.variables["EMBREE_TUTORIALS"] = False
        tc.variables["EMBREE_GEOMETRY_CURVE"] = self.options.geometry_curve
        tc.variables["EMBREE_GEOMETRY_GRID"] = self.options.geometry_grid
        tc.variables["EMBREE_GEOMETRY_INSTANCE"] = self.options.geometry_instance
        tc.variables["EMBREE_GEOMETRY_QUAD"] = self.options.geometry_quad
        tc.variables["EMBREE_GEOMETRY_SUBDIVISION"] = self.options.geometry_subdivision
        tc.variables["EMBREE_GEOMETRY_TRIANGLE"] = self.options.geometry_triangle
        tc.variables["EMBREE_GEOMETRY_USER"] = self.options.geometry_user
        tc.variables["EMBREE_RAY_PACKETS"] = self.options.ray_packets
        tc.variables["EMBREE_RAY_MASK"] = self.options.ray_masking
        tc.variables["EMBREE_BACKFACE_CULLING"] = self.options.backface_culling
        tc.variables["EMBREE_IGNORE_INVALID_RAYS"] = self.options.ignore_invalid_rays
        tc.variables["EMBREE_ISPC_SUPPORT"] = False
        tc.variables["EMBREE_TASKING_SYSTEM"] = "TBB" if self.options.with_tbb else "INTERNAL"
        tc.variables["EMBREE_MAX_ISA"] = "NONE"
        if self._embree_has_neon_support:
            tc.variables["EMBREE_ISA_NEON"] = self.options.get_safe("neon", False)
        if self._embree_has_neon2x_support:
            tc.variables["EMBREE_ISA_NEON2X"] = self.options.get_safe("neon2x", False)

        tc.variables["EMBREE_ISA_SSE2"] = self.options.get_safe("sse2", False)
        tc.variables["EMBREE_ISA_SSE42"] = self.options.get_safe("sse42", False)
        tc.variables["EMBREE_ISA_AVX"] = self.options.get_safe("avx", False)
        tc.variables["EMBREE_ISA_AVX2"] = self.options.get_safe("avx2", False)
        if Version(self.version) < "3.12.2":
            # TODO: probably broken if avx512 enabled, must cumbersome to add specific options in the recipe
            tc.variables["EMBREE_ISA_AVX512KNL"] = self.options.get_safe("avx512", False)
            tc.variables["EMBREE_ISA_AVX512SKX"] = self.options.get_safe("avx512", False)
        else:
            tc.variables["EMBREE_ISA_AVX512"] = self.options.get_safe("avx512", False)
        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # some compilers (e.g. clang) do not like UTF-16 sources
        rc = os.path.join(self.source_folder, "kernels", "embree.rc")
        content = load(self, rc, encoding="utf_16_le")
        if content[0] == '\ufeff':
            content = content[1:]
        content = "#pragma code_page(65001)\n" + content
        save(self, rc, content)
        os.remove(os.path.join(self.source_folder, "common", "cmake", "FindTBB.cmake"))

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        rm(self, "*.command", os.path.join(self.package_folder))
        rm(self, "*.cmake", os.path.join(self.package_folder))

        if self.settings.os == "Windows" and self.options.shared:
            for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                rm(self, dll_pattern_to_remove, os.path.join(self.package_folder, "bin"))
        else:
            rmdir(self, os.path.join(self.package_folder, "bin"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"embree": "embree::embree"}
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

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "embree")
        self.cpp_info.set_property("cmake_target_name", "embree")

        def _lib_exists(name):
            return bool(glob.glob(os.path.join(self.package_folder, "lib", f"*{name}.*")))

        self.cpp_info.libs = ["embree3"]
        if not self.options.shared:
            self.cpp_info.libs.extend(["sys", "math", "simd", "lexers", "tasking"])
            simd_libs = ["embree_sse42", "embree_avx", "embree_avx2"]
            simd_libs.extend(["embree_avx512knl", "embree_avx512skx"] if Version(self.version) < "3.12.2" else ["embree_avx512"])
            for lib in simd_libs:
                if _lib_exists(lib):
                    self.cpp_info.libs.append(lib)

        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.extend(["dl", "m", "pthread"])

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "embree"
        self.cpp_info.names["cmake_find_package_multi"] = "embree"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
