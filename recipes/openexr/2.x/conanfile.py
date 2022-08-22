from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, replace_in_file, rmdir, save
from conan.tools.scm import Version
from conans import tools as tools_legacy
import os
import textwrap

required_conan_version = ">=1.50.2 <1.51.0 || >=1.51.2"


class OpenEXRConan(ConanFile):
    name = "openexr"
    description = "OpenEXR is a high dynamic-range (HDR) image file format developed by Industrial Light & " \
                  "Magic for use in computer imaging applications."
    topics = ("openexr", "hdr", "image", "picture")
    license = "BSD-3-Clause"
    homepage = "https://github.com/AcademySoftwareFoundation/openexr"
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

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.12")

    def validate(self):
        if Version(self.version) < "2.5.0" and hasattr(self, "settings_build") and cross_building(self):
            # cross-build supported since https://github.com/AcademySoftwareFoundation/openexr/pull/606
            raise ConanInvalidConfiguration("Cross-build not supported before openexr 2.5.0")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version],
            destination=self.source_folder, strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["OPENEXR_BUILD_BOTH_STATIC_SHARED"] = False
        tc.variables["ILMBASE_BUILD_BOTH_STATIC_SHARED"] = False
        tc.variables["PYILMBASE_ENABLE"] = False
        if Version(self.version) < "2.5.0":
            tc.variables["OPENEXR_VIEWERS_ENABLE"] = False
        else:
            tc.variables["INSTALL_OPENEXR_EXAMPLES"] = False
            tc.variables["INSTALL_OPENEXR_DOCS"] = False
        tc.variables["OPENEXR_BUILD_UTILS"] = False
        tc.variables["BUILD_TESTING"] = False
        tc.variables["CMAKE_SKIP_INSTALL_RPATH"] = True
        tc.generate()
        cd = CMakeDeps(self)
        cd.generate()

    def _patch_sources(self):
        pkg_version = Version(self.version)
        if pkg_version < "2.5.2" and self.settings.os == "Windows":
            # This fixes symlink creation on Windows.
            # OpenEXR's build system no longer creates symlinks on windows, starting with commit
            # 7f9e1b410de92de244329b614cf551b30bc30421 (included in 2.5.2).
            for lib in ("OpenEXR", "IlmBase"):
                replace_in_file(self, os.path.join(self.source_folder,  lib, "config", "LibraryDefine.cmake"),
                                      "${CMAKE_COMMAND} -E chdir ${CMAKE_INSTALL_FULL_LIBDIR}",
                                      "${CMAKE_COMMAND} -E chdir ${CMAKE_INSTALL_FULL_BINDIR}")

        # Add  "_d" suffix to lib file names.
        if pkg_version < "2.5.7" and self.settings.build_type == "Debug":
            for lib in ("OpenEXR", "IlmBase"):
                replace_in_file(self, os.path.join(self.source_folder,  lib, "config", "LibraryDefine.cmake"),
                                      "set(verlibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}${@LIB@_LIB_SUFFIX}${CMAKE_SHARED_LIBRARY_SUFFIX})".replace("@LIB@", lib.upper()),
                                      "set(verlibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}${@LIB@_LIB_SUFFIX}_d${CMAKE_SHARED_LIBRARY_SUFFIX})".replace("@LIB@", lib.upper()))
                replace_in_file(self, os.path.join(self.source_folder,  lib, "config", "LibraryDefine.cmake"),
                                      "set(baselibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}${CMAKE_SHARED_LIBRARY_SUFFIX})",
                                      "set(baselibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}_d${CMAKE_SHARED_LIBRARY_SUFFIX})")

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "IlmBase::IlmBaseConfig": "OpenEXR::IlmBaseConfig",
                "IlmBase::Half": "OpenEXR::Half",
                "IlmBase::Iex": "OpenEXR::Iex",
                "IlmBase::IexMath": "OpenEXR::IexMath",
                "IlmBase::IMath": "OpenEXR::IMath",
                "IlmBase::IlmThread": "OpenEXR::IlmThread",
            }
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
        # FIXME: we should generate 2 CMake config files: OpenEXRConfig.cmake and IlmBaseConfig.cmake
        #        waiting an implementation of https://github.com/conan-io/conan/issues/9000
        self.cpp_info.set_property("cmake_file_name", "OpenEXR")

        openexr_version = Version(self.version)
        lib_suffix = f"-{openexr_version.major}_{openexr_version.minor}"
        if self.settings.build_type == "Debug":
            lib_suffix += "_d"

        include_dir = os.path.join("include", "OpenEXR")

        # IlmImfConfig
        self.cpp_info.components["openexr_ilmimfconfig"].set_property("cmake_target_name", "OpenEXR::IlmImfConfig")
        self.cpp_info.components["openexr_ilmimfconfig"].includedirs.append(include_dir)

        # IlmImf
        self.cpp_info.components["openexr_ilmimf"].set_property("cmake_target_name", "OpenEXR::IlmImf")
        self.cpp_info.components["openexr_ilmimf"].set_property("pkg_config_name", "OpenEXR")
        self.cpp_info.components["openexr_ilmimf"].includedirs.append(include_dir)
        self.cpp_info.components["openexr_ilmimf"].libs = [f"IlmImf{lib_suffix}"]
        self.cpp_info.components["openexr_ilmimf"].requires = [
            "openexr_ilmimfconfig", "ilmbase_iex", "ilmbase_half",
            "ilmbase_imath", "ilmbase_ilmthread", "zlib::zlib",
        ]

        # IlmImfUtil
        self.cpp_info.components["openexr_ilmimfutil"].set_property("cmake_target_name", "OpenEXR::IlmImfUtil")
        self.cpp_info.components["openexr_ilmimfutil"].includedirs.append(include_dir)
        self.cpp_info.components["openexr_ilmimfutil"].libs = [f"IlmImfUtil{lib_suffix}"]
        self.cpp_info.components["openexr_ilmimfutil"].requires = ["openexr_ilmimfconfig", "openexr_ilmimf"]

        # IlmBaseConfig
        self.cpp_info.components["ilmbase_ilmbaseconfig"].set_property("cmake_target_name", "IlmBase::IlmBaseConfig")
        self.cpp_info.components["ilmbase_ilmbaseconfig"].includedirs.append(include_dir)

        # Half
        self.cpp_info.components["ilmbase_half"].set_property("cmake_target_name", "IlmBase::Half")
        self.cpp_info.components["ilmbase_half"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_half"].libs = [f"Half{lib_suffix}"]
        self.cpp_info.components["ilmbase_half"].requires = ["ilmbase_ilmbaseconfig"]

        # Iex
        self.cpp_info.components["ilmbase_iex"].set_property("cmake_target_name", "IlmBase::Iex")
        self.cpp_info.components["ilmbase_iex"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_iex"].libs = [f"Iex{lib_suffix}"]
        self.cpp_info.components["ilmbase_iex"].requires = ["ilmbase_ilmbaseconfig"]

        # IexMath
        self.cpp_info.components["ilmbase_iexmath"].set_property("cmake_target_name", "IlmBase::IexMath")
        self.cpp_info.components["ilmbase_iexmath"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_iexmath"].libs = [f"IexMath{lib_suffix}"]
        self.cpp_info.components["ilmbase_iexmath"].requires = ["ilmbase_ilmbaseconfig", "ilmbase_iex"]

        # IMath
        self.cpp_info.components["ilmbase_imath"].set_property("cmake_target_name", "IlmBase::IMath")
        self.cpp_info.components["ilmbase_imath"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_imath"].libs = [f"Imath{lib_suffix}"]
        self.cpp_info.components["ilmbase_imath"].requires = ["ilmbase_ilmbaseconfig", "ilmbase_half", "ilmbase_iexmath"]

        # IlmThread
        self.cpp_info.components["ilmbase_ilmthread"].set_property("cmake_target_name", "IlmBase::IlmThread")
        self.cpp_info.components["ilmbase_ilmthread"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_ilmthread"].libs = [f"IlmThread{lib_suffix}"]
        self.cpp_info.components["ilmbase_ilmthread"].requires = ["ilmbase_ilmbaseconfig", "ilmbase_iex"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["ilmbase_ilmthread"].system_libs.append("pthread")

        # Convenient component to model official IlmBase.pc
        self.cpp_info.components["ilmbase_conan_pkgconfig"].set_property("pkg_config_name", "IlmBase")
        self.cpp_info.components["ilmbase_conan_pkgconfig"].requires = [
            "ilmbase_ilmbaseconfig", "ilmbase_half", "ilmbase_iex",
            "ilmbase_iexmath", "ilmbase_imath", "ilmbase_ilmthread"
        ]

        if self.options.shared and self.settings.os == "Windows":
            self.cpp_info.components["openexr_ilmimfconfig"].defines.append("OPENEXR_DLL")
            self.cpp_info.components["ilmbase_ilmbaseconfig"].defines.append("OPENEXR_DLL")

        if not self.options.shared:
            libcxx = tools_legacy.stdcpp_library(self)
            if libcxx:
                self.cpp_info.components["openexr_ilmimfconfig"].system_libs.append(libcxx)
                self.cpp_info.components["ilmbase_ilmbaseconfig"].system_libs.append(libcxx)

        # TODO: to remove in conan v2 once cmake_find_package* generators removed
        self.cpp_info.names["cmake_find_package"] = "OpenEXR"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenEXR"
        self.cpp_info.components["openexr_ilmimfconfig"].names["cmake_find_package"] = "IlmImfConfig"
        self.cpp_info.components["openexr_ilmimfconfig"].names["cmake_find_package_multi"] = "IlmImfConfig"
        self.cpp_info.components["openexr_ilmimf"].names["cmake_find_package"] = "IlmImf"
        self.cpp_info.components["openexr_ilmimf"].names["cmake_find_package_multi"] = "IlmImf"
        self.cpp_info.components["openexr_ilmimfutil"].names["cmake_find_package"] = "IlmImfUtil"
        self.cpp_info.components["openexr_ilmimfutil"].names["cmake_find_package_multi"] = "IlmImfUtil"
        self.cpp_info.components["ilmbase_ilmbaseconfig"].names["cmake_find_package"] = "IlmBaseConfig"
        self.cpp_info.components["ilmbase_ilmbaseconfig"].names["cmake_find_package_multi"] = "IlmBaseConfig"
        self.cpp_info.components["ilmbase_ilmbaseconfig"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_ilmbaseconfig"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_half"].names["cmake_find_package"] = "Half"
        self.cpp_info.components["ilmbase_half"].names["cmake_find_package_multi"] = "Half"
        self.cpp_info.components["ilmbase_half"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_half"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_iex"].names["cmake_find_package"] = "Iex"
        self.cpp_info.components["ilmbase_iex"].names["cmake_find_package_multi"] = "Iex"
        self.cpp_info.components["ilmbase_iex"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_iex"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_iexmath"].names["cmake_find_package"] = "IexMath"
        self.cpp_info.components["ilmbase_iexmath"].names["cmake_find_package_multi"] = "IexMath"
        self.cpp_info.components["ilmbase_iexmath"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_iexmath"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_imath"].names["cmake_find_package"] = "IMath"
        self.cpp_info.components["ilmbase_imath"].names["cmake_find_package_multi"] = "IMath"
        self.cpp_info.components["ilmbase_imath"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_imath"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_ilmthread"].names["cmake_find_package"] = "IlmThread"
        self.cpp_info.components["ilmbase_ilmthread"].names["cmake_find_package_multi"] = "IlmThread"
        self.cpp_info.components["ilmbase_ilmthread"].build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.components["ilmbase_ilmthread"].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
