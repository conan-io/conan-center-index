from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get, copy, rm, rmdir, save
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import os
import textwrap


required_conan_version = ">=1.52.0"


class GDCMConan(ConanFile):
    name = "gdcm"
    description = "C++ library for DICOM medical files"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://gdcm.sourceforge.net/"
    topics = ("dicom", "images")
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _minimum_cpp_standard(self):
        return 11

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

    def requirements(self):
        self.requires("expat/2.4.9")
        self.requires("openjpeg/2.5.0")
        self.requires("zlib/1.2.12")

    def validate(self):
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, self._minimum_cpp_standard)
        if is_msvc_static_runtime(self) and self.info.options.shared:
            raise ConanInvalidConfiguration(f"{self.ref} does not support shared and static runtime together.")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
                  destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["GDCM_BUILD_DOCBOOK_MANPAGES"] = False
        tc.variables["GDCM_BUILD_SHARED_LIBS"] = bool(self.options.shared)
        # FIXME: unvendor deps https://github.com/conan-io/conan-center-index/pull/5705#discussion_r647224146
        tc.variables["GDCM_USE_SYSTEM_EXPAT"] = True
        tc.variables["GDCM_USE_SYSTEM_OPENJPEG"] = True
        tc.variables["GDCM_USE_SYSTEM_ZLIB"] = True
        if not self.settings.compiler.cppstd:
            tc.variables["CMAKE_CXX_STANDARD"] = self._minimum_cpp_standard
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, pattern="Copyright.txt", dst=os.path.join(self.package_folder, "licenses"), src=self.source_folder)
        cmake = CMake(self)
        cmake.install()

        if self.settings.os == "Windows":
            bin_dir = os.path.join(self.package_folder, "bin")
            rm(self, "[!gs]*.dll", bin_dir)
            rm(self, "*.pdb", bin_dir)

        rm(self, "[!U]*.cmake", os.path.join(self.package_folder, "lib", self._gdcm_subdir)) #leave UseGDCM.cmake untouched
        rmdir(self, os.path.join(self.package_folder, "share"))
        self._create_cmake_variables(os.path.join(self.package_folder, self._gdcm_cmake_variables_path))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets()

    def _create_cmake_variables(self, variables_file):
        v = Version(self.version)
        content = textwrap.dedent(f"""\
            # The GDCM version number.
            set(GDCM_MAJOR_VERSION "{v.major}")
            set(GDCM_MINOR_VERSION "{v.minor}")
            set(GDCM_BUILD_VERSION "{v.patch}")

            get_filename_component(SELF_DIR "${{CMAKE_CURRENT_LIST_FILE}}" PATH)

            # The libraries.
            set(GDCM_LIBRARIES "")

            # The CMake macros dir.
            set(GDCM_CMAKE_DIR "")

            # The configuration options.
            set(GDCM_BUILD_SHARED_LIBS "{"ON" if self.options.shared else "OFF"}")

            set(GDCM_USE_VTK "OFF")

            # The "use" file.
            set(GDCM_USE_FILE ${{SELF_DIR}}/UseGDCM.cmake)

            # The VTK options.
            set(GDCM_VTK_DIR "")

            get_filename_component(GDCM_INCLUDE_ROOT "${{SELF_DIR}}/../../include/{self._gdcm_subdir}" ABSOLUTE)
            set(GDCM_INCLUDE_DIRS ${{GDCM_INCLUDE_ROOT}})
            get_filename_component(GDCM_LIB_ROOT "${{SELF_DIR}}/../../lib" ABSOLUTE)
            set(GDCM_LIBRARY_DIRS ${{GDCM_LIB_ROOT}})
        """)
        save(self, variables_file, content)

    def _create_cmake_module_alias_targets(self):
        module_file = os.path.join(self.package_folder, self._gdcm_cmake_module_aliases_path)
        targets = {library: f"GDCM::{library}" for library in self._gdcm_libraries}
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
    def _gdcm_builddir(self):
        return os.path.join("lib", self._gdcm_subdir)

    @property
    def _gdcm_cmake_module_aliases_path(self):
        return os.path.join("lib", self._gdcm_subdir, "conan-official-gdcm-targets.cmake")

    @property
    def _gdcm_cmake_variables_path(self):
        return os.path.join("lib", self._gdcm_subdir, "conan-official-gdcm-variables.cmake")

    @property
    def _gdcm_build_modules(self):
        return [self._gdcm_cmake_module_aliases_path, self._gdcm_cmake_variables_path]

    @property
    def _gdcm_libraries(self):
        gdcm_libs = ["gdcmcharls",
                     "gdcmCommon",
                     "gdcmDICT",
                     "gdcmDSED",
                     "gdcmIOD",
                     "gdcmjpeg12",
                     "gdcmjpeg16",
                     "gdcmjpeg8",
                     "gdcmMEXD",
                     "gdcmMSFF",
                     "socketxx"]
        if self.settings.os == "Windows":
            gdcm_libs.append("gdcmgetopt")
        else:
            gdcm_libs.append("gdcmuuid")
        return gdcm_libs

    @property
    def _gdcm_subdir(self):
        v = Version(self.version)
        return f"gdcm-{v.major}.{v.minor}"

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "GDCM")
        self.cpp_info.set_property("cmake_build_modules", [self._gdcm_cmake_variables_path])

        for lib in self._gdcm_libraries:
            self.cpp_info.components[lib].set_property("cmake_target_name", lib)
            self.cpp_info.components[lib].libs = [lib]
            self.cpp_info.components[lib].includedirs = [os.path.join("include", self._gdcm_subdir)]
            self.cpp_info.components[lib].builddirs.append(self._gdcm_builddir)

            # TODO: to remove in conan v2 once cmake_find_package* generators removed
            self.cpp_info.components[lib].build_modules["cmake"] = [self._gdcm_cmake_module_aliases_path]
            self.cpp_info.components[lib].build_modules["cmake_find_package"] = self._gdcm_build_modules
            self.cpp_info.components[lib].build_modules["cmake_find_package_multi"] = self._gdcm_build_modules

        self.cpp_info.components["gdcmDSED"].requires.extend(["gdcmCommon", "zlib::zlib"])
        self.cpp_info.components["gdcmIOD"].requires.extend(["gdcmDSED", "gdcmCommon", "expat::expat"])
        self.cpp_info.components["gdcmMSFF"].requires.extend(["gdcmIOD", "gdcmDSED", "gdcmDICT", "openjpeg::openjpeg"])
        if not self.options.shared:
            self.cpp_info.components["gdcmDICT"].requires.extend(["gdcmDSED", "gdcmIOD"])
            self.cpp_info.components["gdcmMEXD"].requires.extend(["gdcmMSFF", "gdcmDICT", "gdcmDSED", "gdcmIOD", "socketxx"])
            self.cpp_info.components["gdcmMSFF"].requires.extend(["gdcmjpeg8", "gdcmjpeg12", "gdcmjpeg16", "gdcmcharls"])

            if self.settings.os == "Windows":
                self.cpp_info.components["gdcmCommon"].system_libs = ["ws2_32", "crypt32"]
                self.cpp_info.components["gdcmMSFF"].system_libs = ["rpcrt4"]
                self.cpp_info.components["socketxx"].system_libs = ["ws2_32"]
            else:
                self.cpp_info.components["gdcmMSFF"].requires.append("gdcmuuid")

                self.cpp_info.components["gdcmCommon"].system_libs = ["dl"]
                if is_apple_os(self):
                    self.cpp_info.components["gdcmCommon"].frameworks = ["CoreFoundation"]

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "GDCM"
        self.cpp_info.names["cmake_find_package_multi"] = "GDCM"
