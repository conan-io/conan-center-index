from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.scm import Version
from conan.tools.files import apply_conandata_patches, get, rmdir, replace_in_file, copy, rm
from conan.tools.microsoft import is_msvc
from conan.tools.build.cross_building import cross_building
from conan.tools.apple import is_apple_os
from conan.errors import ConanInvalidConfiguration
import os


required_conan_version = ">=1.51.3"


class LibpngConan(ConanFile):
    name = "libpng"
    description = "libpng is the official PNG file format reference library."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.libpng.org"
    license = "libpng-2.0"
    topics = ("png", "graphics", "image")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "neon": [True, "check", False],
        "msa": [True, False],
        "sse": [True, False],
        "vsx": [True, False],
        "api_prefix": ["ANY"],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "neon": True,
        "msa": True,
        "sse": True,
        "vsx": True,
        "api_prefix": "",
    }

    @property
    def _has_neon_support(self):
        return "arm" in self.settings.arch

    @property
    def _has_msa_support(self):
        return "mips" in self.settings.arch

    @property
    def _has_sse_support(self):
        return self.settings.arch in ["x86", "x86_64"]

    @property
    def _has_vsx_support(self):
        return "ppc" in self.settings.arch

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if not self._has_neon_support:
            del self.options.neon
        if not self._has_msa_support:
            del self.options.msa
        if not self._has_sse_support:
            del self.options.sse
        if not self._has_vsx_support:
            del self.options.vsx

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
        self.requires("zlib/1.2.12")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def _patch_source(self):
        if self.settings.os == "Windows":
            if is_msvc(self):
                if Version(self.version) <= "1.5.2":
                    replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                          'set(PNG_LIB_NAME_STATIC ${PNG_LIB_NAME}_static)',
                                          'set(PNG_LIB_NAME_STATIC ${PNG_LIB_NAME})')
                else:
                    replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                        'OUTPUT_NAME "${PNG_LIB_NAME}_static',
                                        'OUTPUT_NAME "${PNG_LIB_NAME}')
            else:
                replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                                      'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}',
                                      'COMMAND "${CMAKE_COMMAND}" -E copy_if_different $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/$<TARGET_LINKER_FILE_NAME:${S_TARGET}> $<TARGET_LINKER_FILE_DIR:${S_TARGET}>/${DEST_FILE}')

    @property
    def _neon_msa_sse_vsx_mapping(self):
        return {
            "True": "on",
            "False": "off",
            "check": "check",
        }

    @property
    def _libpng_cmake_system_processor(self):
        # FIXME: too specific and error prone, should be delegated to a conan helper function
        # It should satisfy libpng CMakeLists specifically, do not use it naively in an other recipe
        if "mips" in self.settings.arch:
            return "mipsel"
        if "ppc" in self.settings.arch:
            return "powerpc"
        return str(self.settings.arch)

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["PNG_TESTS"] = False
        tc.variables["PNG_SHARED"] = self.options.shared
        tc.variables["PNG_STATIC"] = not self.options.shared
        tc.variables["PNG_DEBUG"] = self.settings.build_type == "Debug"
        tc.variables["PNG_PREFIX"] = self.options.api_prefix
        if cross_building(self):
            system_processor = self.conf.get("tools.cmake.cmaketoolchain:system_processor",
                                                  self._libpng_cmake_system_processor, check_type=str)
            tc.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = system_processor
        if self._has_neon_support:
            tc.variables["PNG_ARM_NEON"] = self._neon_msa_sse_vsx_mapping[str(self.options.neon)]
        if self._has_msa_support:
            tc.variables["PNG_MIPS_MSA"] = self._neon_msa_sse_vsx_mapping[str(self.options.msa)]
        if self._has_sse_support:
            tc.variables["PNG_INTEL_SSE"] = self._neon_msa_sse_vsx_mapping[str(self.options.sse)]
        if self._has_vsx_support:
            tc.variables["PNG_POWERPC_VSX"] = self._neon_msa_sse_vsx_mapping[str(self.options.vsx)]
        tc.cache_variables["CMAKE_MACOSX_BUNDLE"] = False
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def validate(self):
        if Version(self.version) < "1.6" and self.info.settings.arch == "armv8" and is_apple_os(self):
            raise ConanInvalidConfiguration(f"{self.ref} could not be cross build on Mac.")

    def build(self):
        apply_conandata_patches(self)
        self._patch_source()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        if self.options.shared:
            rm(self, "*[!.dll]", os.path.join(self.package_folder, "bin"))
        else:
            rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "libpng"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        major_min_version = f"{Version(self.version).major}{Version(self.version).minor}"

        # TODO: Remove after Conan 2.0
        self.cpp_info.names["cmake_find_package"] = "PNG"
        self.cpp_info.names["cmake_find_package_multi"] = "PNG"

        self.cpp_info.set_property("cmake_file_name", "PNG")
        self.cpp_info.set_property("cmake_target_name", "PNG::PNG")
        self.cpp_info.set_property("pkg_config_name", "libpng")
        self.cpp_info.set_property("pkg_config_aliases", [f"libpng{major_min_version}"])

        prefix = "lib" if is_msvc(self) else ""
        suffix = major_min_version if is_msvc(self) else ""
        suffix += "d" if is_msvc(self) and self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = [f"{prefix}png{suffix}"]
        if self.settings.os in ["Linux", "Android", "FreeBSD", "SunOS", "AIX"]:
            self.cpp_info.system_libs.append("m")
