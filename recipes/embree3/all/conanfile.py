from conan import ConanFile, tools
from conan.tools.cmake import CMake
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import save, load
import glob
import os
import textwrap

required_conan_version = ">=1.43.0"


class EmbreeConan(ConanFile):
    name = "embree3"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("embree", "raytracing", "rendering")
    description = "Intel's collection of high-performance ray tracing kernels."
    homepage = "https://embree.github.io/"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "sse2": [True, False],
        "sse42": [True, False],
        "avx": [True, False],
        "avx2": [True, False],
        "avx512": [True, False],
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
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "sse2": True,
        "sse42": False,
        "avx": False,
        "avx2": False,
        "avx512": False,
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
    }

    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _has_sse_avx(self):
        return self.settings.arch in ["x86", "x86_64"]

    @property
    def _embree_has_neon_support(self):
        return tools.Version(self.version) >= "3.13.0"

    @property
    def _has_neon(self):
        return "arm" in self.settings.arch

    @property
    def _num_isa(self):
        num_isa = 0
        if self._embree_has_neon_support and self._has_neon:
            num_isa += 1
        for simd_option in ["sse2", "sse42", "avx", "avx2", "avx512"]:
            if self.options.get_safe(simd_option):
                num_isa += 1
        return num_isa

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_sse_avx:
            del self.options.sse2
            del self.options.sse42
            del self.options.avx
            del self.options.avx2
            del self.options.avx512

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def validate(self):
        if not (self._has_sse_avx or (self._embree_has_neon_support and self._has_neon)):
            raise ConanInvalidConfiguration("Embree {} doesn't support {}".format(self.version, self.settings.arch))

        compiler_version = tools.Version(self.settings.compiler.version)
        if self.settings.compiler == "clang" and compiler_version < "4":
            raise ConanInvalidConfiguration("Clang < 4 is not supported")
        elif self.settings.compiler == "Visual Studio" and compiler_version < "15":
            raise ConanInvalidConfiguration("Visual Studio < 15 is not supported")

        if self.settings.os == "Linux" and self.settings.compiler == "clang" and self.settings.compiler.libcxx == "libc++":
            raise ConanInvalidConfiguration("conan recipe for Embree v{0} \
                cannot be built with clang libc++, use libstdc++ instead".format(self.version))

        if self.settings.compiler == "apple-clang" and not self.options.shared and compiler_version >= "9.0" and self._num_isa > 1:
            raise ConanInvalidConfiguration("Embree static with apple-clang >=9 and multiple ISA (simd) is not supported")

        if self._num_isa == 0:
            raise ConanInvalidConfiguration("At least one ISA (simd) must be enabled")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        # Configure CMake library build:
        self._cmake.definitions["EMBREE_STATIC_LIB"] = not self.options.shared
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["EMBREE_TUTORIALS"] = False
        self._cmake.definitions["EMBREE_GEOMETRY_CURVE"] = self.options.geometry_curve
        self._cmake.definitions["EMBREE_GEOMETRY_GRID"] = self.options.geometry_grid
        self._cmake.definitions["EMBREE_GEOMETRY_INSTANCE"] = self.options.geometry_instance
        self._cmake.definitions["EMBREE_GEOMETRY_QUAD"] = self.options.geometry_quad
        self._cmake.definitions["EMBREE_GEOMETRY_SUBDIVISION"] = self.options.geometry_subdivision
        self._cmake.definitions["EMBREE_GEOMETRY_TRIANGLE"] = self.options.geometry_triangle
        self._cmake.definitions["EMBREE_GEOMETRY_USER"] = self.options.geometry_user
        self._cmake.definitions["EMBREE_RAY_PACKETS"] = self.options.ray_packets
        self._cmake.definitions["EMBREE_RAY_MASK"] = self.options.ray_masking
        self._cmake.definitions["EMBREE_BACKFACE_CULLING"] = self.options.backface_culling
        self._cmake.definitions["EMBREE_IGNORE_INVALID_RAYS"] = self.options.ignore_invalid_rays
        self._cmake.definitions["EMBREE_ISPC_SUPPORT"] = False
        self._cmake.definitions["EMBREE_TASKING_SYSTEM"] = "INTERNAL"
        self._cmake.definitions["EMBREE_MAX_ISA"] = "NONE"
        if self._embree_has_neon_support:
            self._cmake.definitions["EMBREE_ISA_NEON"] = self._has_neon
        self._cmake.definitions["EMBREE_ISA_SSE2"] = self.options.get_safe("sse2", False)
        self._cmake.definitions["EMBREE_ISA_SSE42"] = self.options.get_safe("sse42", False)
        self._cmake.definitions["EMBREE_ISA_AVX"] = self.options.get_safe("avx", False)
        self._cmake.definitions["EMBREE_ISA_AVX2"] = self.options.get_safe("avx2", False)
        if tools.Version(self.version) < "3.12.2":
            # TODO: probably broken if avx512 enabled, must cumbersome to add specific options in the recipe
            self._cmake.definitions["EMBREE_ISA_AVX512KNL"] = self.options.get_safe("avx512", False)
            self._cmake.definitions["EMBREE_ISA_AVX512SKX"] = self.options.get_safe("avx512", False)
        else:
            self._cmake.definitions["EMBREE_ISA_AVX512"] = self.options.get_safe("avx512", False)

        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        # some compilers (e.g. clang) do not like UTF-16 sources
        rc = os.path.join(self._source_subfolder, "kernels", "embree.rc")
        content = load(self, rc, encoding="utf_16_le")
        if content[0] == '\ufeff':
            content = content[1:]
        content = "#pragma code_page(65001)\n" + content
        save(self, rc, content)
        os.remove(os.path.join(self._source_subfolder, "common", "cmake", "FindTBB.cmake"))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.remove_files_by_mask(os.path.join(self.package_folder), "*.command")
        tools.remove_files_by_mask(os.path.join(self.package_folder), "*.cmake")

        if self.settings.os == "Windows" and self.options.shared:
            for dll_pattern_to_remove in ["concrt*.dll", "msvcp*.dll", "vcruntime*.dll"]:
                tools.remove_files_by_mask(os.path.join(self.package_folder), dll_pattern_to_remove)
        else:
            tools.rmdir(os.path.join(self.package_folder, "bin"))

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"embree": "embree::embree"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "embree")
        self.cpp_info.set_property("cmake_target_name", "embree")

        def _lib_exists(name):
            return True if glob.glob(os.path.join(self.package_folder, "lib", "*{}.*".format(name))) else False

        self.cpp_info.libs = ["embree3"]
        if not self.options.shared:
            self.cpp_info.libs.extend(["sys", "math", "simd", "lexers", "tasking"])
            simd_libs = ["embree_sse42", "embree_avx", "embree_avx2"]
            simd_libs.extend(["embree_avx512knl", "embree_avx512skx"] if tools.Version(self.version) < "3.12.2" else ["embree_avx512"])
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
