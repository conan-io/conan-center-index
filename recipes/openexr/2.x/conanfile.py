from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.43.0"


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

    exports_sources = "CMakeLists.txt"
    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("zlib/1.2.12")

    def validate(self):
        if tools.Version(self.version) < "2.5.0" and hasattr(self, "settings_build") and tools.cross_building(self):
            # cross-build supported since https://github.com/AcademySoftwareFoundation/openexr/pull/606
            raise ConanInvalidConfiguration("Cross-build not supported before openexr 2.5.0")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OPENEXR_BUILD_BOTH_STATIC_SHARED"] = False
        self._cmake.definitions["ILMBASE_BUILD_BOTH_STATIC_SHARED"] = False
        self._cmake.definitions["PYILMBASE_ENABLE"] = False
        if tools.Version(self.version) < "2.5.0":
            self._cmake.definitions["OPENEXR_VIEWERS_ENABLE"] = False
        else:
            self._cmake.definitions["INSTALL_OPENEXR_EXAMPLES"] = False
            self._cmake.definitions["INSTALL_OPENEXR_DOCS"] = False
        self._cmake.definitions["OPENEXR_BUILD_UTILS"] = False
        self._cmake.definitions["BUILD_TESTING"] = False
        self._cmake.definitions["CMAKE_SKIP_INSTALL_RPATH"] = True
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        pkg_version = tools.Version(self.version)
        if pkg_version < "2.5.2" and self.settings.os == "Windows":
            # This fixes symlink creation on Windows.
            # OpenEXR's build system no longer creates symlinks on windows, starting with commit
            # 7f9e1b410de92de244329b614cf551b30bc30421 (included in 2.5.2).
            for lib in ("OpenEXR", "IlmBase"):
                tools.replace_in_file(os.path.join(self._source_subfolder,  lib, "config", "LibraryDefine.cmake"),
                                      "${CMAKE_COMMAND} -E chdir ${CMAKE_INSTALL_FULL_LIBDIR}",
                                      "${CMAKE_COMMAND} -E chdir ${CMAKE_INSTALL_FULL_BINDIR}")

        # Add  "_d" suffix to lib file names.
        if pkg_version < "2.5.7" and self.settings.build_type == "Debug":
            for lib in ("OpenEXR", "IlmBase"):
                tools.replace_in_file(os.path.join(self._source_subfolder,  lib, "config", "LibraryDefine.cmake"),
                                      "set(verlibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}${@LIB@_LIB_SUFFIX}${CMAKE_SHARED_LIBRARY_SUFFIX})".replace("@LIB@", lib.upper()),
                                      "set(verlibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}${@LIB@_LIB_SUFFIX}_d${CMAKE_SHARED_LIBRARY_SUFFIX})".replace("@LIB@", lib.upper()))
                tools.replace_in_file(os.path.join(self._source_subfolder,  lib, "config", "LibraryDefine.cmake"),
                                      "set(baselibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}${CMAKE_SHARED_LIBRARY_SUFFIX})",
                                      "set(baselibname ${CMAKE_SHARED_LIBRARY_PREFIX}${libname}_d${CMAKE_SHARED_LIBRARY_SUFFIX})")

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

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
        # FIXME: we should generate 2 CMake config files: OpenEXRConfig.cmake and IlmBaseConfig.cmake
        #        waiting an implementation of https://github.com/conan-io/conan/issues/9000
        self.cpp_info.set_property("cmake_file_name", "OpenEXR")

        openexr_version = tools.Version(self.version)
        lib_suffix = "-{}_{}".format(openexr_version.major, openexr_version.minor)
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
        self.cpp_info.components["openexr_ilmimf"].libs = ["IlmImf{}".format(lib_suffix)]
        self.cpp_info.components["openexr_ilmimf"].requires = [
            "openexr_ilmimfconfig", "ilmbase_iex", "ilmbase_half",
            "ilmbase_imath", "ilmbase_ilmthread", "zlib::zlib",
        ]

        # IlmImfUtil
        self.cpp_info.components["openexr_ilmimfutil"].set_property("cmake_target_name", "OpenEXR::IlmImfUtil")
        self.cpp_info.components["openexr_ilmimfutil"].includedirs.append(include_dir)
        self.cpp_info.components["openexr_ilmimfutil"].libs = ["IlmImfUtil{}".format(lib_suffix)]
        self.cpp_info.components["openexr_ilmimfutil"].requires = ["openexr_ilmimfconfig", "openexr_ilmimf"]

        # IlmBaseConfig
        self.cpp_info.components["ilmbase_ilmbaseconfig"].set_property("cmake_target_name", "IlmBase::IlmBaseConfig")
        self.cpp_info.components["ilmbase_ilmbaseconfig"].includedirs.append(include_dir)

        # Half
        self.cpp_info.components["ilmbase_half"].set_property("cmake_target_name", "IlmBase::Half")
        self.cpp_info.components["ilmbase_half"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_half"].libs = ["Half{}".format(lib_suffix)]
        self.cpp_info.components["ilmbase_half"].requires = ["ilmbase_ilmbaseconfig"]

        # Iex
        self.cpp_info.components["ilmbase_half"].set_property("cmake_target_name", "IlmBase::Iex")
        self.cpp_info.components["ilmbase_iex"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_iex"].libs = ["Iex{}".format(lib_suffix)]
        self.cpp_info.components["ilmbase_iex"].requires = ["ilmbase_ilmbaseconfig"]

        # IexMath
        self.cpp_info.components["ilmbase_iexmath"].set_property("cmake_target_name", "IlmBase::IexMath")
        self.cpp_info.components["ilmbase_iexmath"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_iexmath"].libs = ["IexMath{}".format(lib_suffix)]
        self.cpp_info.components["ilmbase_iexmath"].requires = ["ilmbase_ilmbaseconfig", "ilmbase_iex"]

        # IMath
        self.cpp_info.components["ilmbase_imath"].set_property("cmake_target_name", "IlmBase::IMath")
        self.cpp_info.components["ilmbase_imath"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_imath"].libs = ["Imath{}".format(lib_suffix)]
        self.cpp_info.components["ilmbase_imath"].requires = ["ilmbase_ilmbaseconfig", "ilmbase_half", "ilmbase_iexmath"]

        # IlmThread
        self.cpp_info.components["ilmbase_ilmthread"].set_property("cmake_target_name", "IlmBase::IlmThread")
        self.cpp_info.components["ilmbase_ilmthread"].includedirs.append(include_dir)
        self.cpp_info.components["ilmbase_ilmthread"].libs = ["IlmThread{}".format(lib_suffix)]
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

        stdlib = tools.stdcpp_library(self)
        if not self.options.shared and stdlib:
            self.cpp_info.components["openexr_ilmimfconfig"].system_libs.append(stdlib)
            self.cpp_info.components["ilmbase_ilmbaseconfig"].system_libs.append(stdlib)

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
