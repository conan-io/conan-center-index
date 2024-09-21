from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir, save, replace_in_file
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=1.54.0"


class OpenjpegConan(ConanFile):
    name = "openjpeg"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language."
    license = "BSD-2-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/uclouvain/openjpeg"
    topics = ("jpeg2000", "jp2", "openjpeg", "image", "multimedia", "format", "graphics")
    package_type = "library"
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

    def package_id(self):
        del self.info.options.build_codec # not used for the moment

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

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
        tc.generate()

    def _patch_sources(self):
        apply_conandata_patches(self)
        # The finite-math-only optimization has no effect and can cause linking errors
        # when linked against glibc >= 2.31
        replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                        "-ffast-math", "-ffast-math;-fno-finite-math-only")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", self._openjpeg_subdir))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake", self._openjpeg_subdir))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        self._create_cmake_module_variables(
            os.path.join(self.package_folder, self._module_vars_rel_path)
        )
        # TODO: to remove in conan v2 once cmake_find_package* & pkg_config generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_target_rel_path),
            {"openjp2": "OpenJPEG::OpenJPEG"}
        )

    def _create_cmake_module_variables(self, module_file):
        content = textwrap.dedent(f"""\
            set(OPENJPEG_FOUND TRUE)
            if(DEFINED OpenJPEG_INCLUDE_DIRS)
                set(OPENJPEG_INCLUDE_DIRS ${{OpenJPEG_INCLUDE_DIRS}})
            endif()
            if(DEFINED OpenJPEG_LIBRARIES)
                set(OPENJPEG_LIBRARIES ${{OpenJPEG_LIBRARIES}})
            endif()
            set(OPENJPEG_MAJOR_VERSION "{Version(self.version).major}")
            set(OPENJPEG_MINOR_VERSION "{Version(self.version).minor}")
            set(OPENJPEG_BUILD_VERSION "{Version(self.version).patch}")
            set(OPENJPEG_BUILD_SHARED_LIBS {"TRUE" if self.options.shared else "FALSE"})
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
    def _module_vars_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-variables.cmake")

    @property
    def _module_target_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    @property
    def _openjpeg_subdir(self):
        openjpeg_version = Version(self.version)
        return f"openjpeg-{openjpeg_version.major}.{openjpeg_version.minor}"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenJPEG")
        self.cpp_info.set_property("cmake_target_name", "openjp2")
        self.cpp_info.set_property("cmake_build_modules", [self._module_vars_rel_path])
        self.cpp_info.set_property("pkg_config_name", "libopenjp2")
        self.cpp_info.includedirs.append(os.path.join("include", self._openjpeg_subdir))
        self.cpp_info.builddirs.append(os.path.join("lib", "cmake"))
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
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_target_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_target_rel_path]
        self.cpp_info.names["pkg_config"] = "libopenjp2"
