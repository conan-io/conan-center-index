from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.50.2"


class OpenjpegConan(ConanFile):
    name = "openjpeg"
    url = "https://github.com/conan-io/conan-center-index"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language."
    topics = ("jpeg2000", "jp2", "openjpeg", "image", "multimedia", "format", "graphics")
    homepage = "https://github.com/uclouvain/openjpeg"
    license = "BSD 2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_codec": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_codec": False,
    }

    def export_sources(self):
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
           del self.settings.compiler.libcxx
        except Exception:
           pass
        try:
           del self.settings.compiler.cppstd
        except Exception:
           pass

    def package_id(self):
        del self.info.options.build_codec # not used for the moment

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_INSTALL_SYSTEM_RUNTIME_LIBS_SKIP"] = True
        tc.variables["BUILD_DOC"] = False
        tc.variables["BUILD_STATIC_LIBS"] = not self.options.shared
        tc.variables["BUILD_LUTS_GENERATOR"] = False
        tc.variables["BUILD_CODEC"] = False
        if Version(self.version) < "2.5.0":
            tc.variables["BUILD_MJ2"] = False
            tc.variables["BUILD_JPWL"] = False
            tc.variables["BUILD_JP3D"] = False
        tc.variables["BUILD_JPIP"] = False
        tc.variables["BUILD_VIEWER"] = False
        tc.variables["BUILD_JAVA"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["BUILD_PKGCONFIG_FILES"] = False
        tc.variables["OPJ_DISABLE_TPSOT_FIX"] = False
        tc.variables["OPJ_USE_THREAD"] = True
        # Honor BUILD_SHARED_LIBS from conan_toolchain (see https://github.com/conan-io/conan/issues/11840)
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", self._openjpeg_subdir))

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"openjp2": "OpenJPEG::OpenJPEG"}
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
    def _openjpeg_subdir(self):
        openjpeg_version = Version(self.version)
        return f"openjpeg-{openjpeg_version.major}.{openjpeg_version.minor}"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenJPEG")
        self.cpp_info.set_property("cmake_target_name", "openjp2")
        self.cpp_info.set_property("pkg_config_name", "libopenjp2")
        self.cpp_info.includedirs.append(os.path.join("include", self._openjpeg_subdir))
        self.cpp_info.libs = ["openjp2"]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("OPJ_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "m"]
        elif self.settings.os == "Android":
            self.cpp_info.system_libs = ["m"]

        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenJPEG"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenJPEG"
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "libopenjp2"
