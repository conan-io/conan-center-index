from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class OpenCascadeConan(ConanFile):
    name = "opencascade"
    description = "A software development platform providing services for 3D " \
                  "surface and solid modeling, CAD data exchange, and visualization."
    homepage = "https://dev.opencascade.org"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    topics = ("conan", "opencascade", "occt", "3d", "modeling", "cad")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ffmpeg": [True, False],
        "with_freeimage": [True, False],
        "with_openvr": [True, False],
        "with_rapidjson": [True, False],
        "with_tbb": [True, False],
        "extended_debug_messages": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ffmpeg": False,
        "with_freeimage": False,
        "with_openvr": False,
        "with_rapidjson": False,
        "with_tbb": False,
        "extended_debug_messages": False,
    }

    short_paths = True

    generators = "cmake"
    exports_sources = "patches/**"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_linux(self):
        return self.settings.os in ["Linux", "FreeBSD"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.build_type != "Debug":
            del self.options.extended_debug_messages

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def requirements(self):
        self.requires("tcl/8.6.10")
        self.requires("tk/8.6.10")
        self.requires("freetype/2.10.4")
        self.requires("opengl/system")
        if self._is_linux:
            self.requires("fontconfig/2.13.93")
            self.requires("xorg/system")
        # TODO: add ffmpeg & freeimage support (also vtk?)
        if self.options.with_ffmpeg:
            raise ConanInvalidConfiguration("ffmpeg recipe not yet available in CCI")
        if self.options.with_freeimage:
            raise ConanInvalidConfiguration("freeimage recipe not yet available in CCI")
        if self.options.with_openvr:
            self.requires("openvr/1.14.15")
        if self.options.with_rapidjson:
            self.requires("rapidjson/1.1.0")
        if self.options.with_tbb:
            self.requires("tbb/2020.3")

    def validate(self):
        if self.settings.compiler == "clang" and self.settings.compiler.version == "6.0" and \
           self.settings.build_type == "Release":
            raise ConanInvalidConfiguration("OpenCASCADE {} doesn't support Clang 6.0 if Release build type".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "OCCT-" + self.version.replace(".", "_")
        tools.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        cmakelists_tools = os.path.join(self._source_subfolder, "tools", "CMakeLists.txt")
        occt_toolkit_cmake = os.path.join(self._source_subfolder, "adm", "cmake", "occt_toolkit.cmake")
        occt_csf_cmake = os.path.join(self._source_subfolder, "adm", "cmake", "occt_csf.cmake")
        occt_defs_flags_cmake = os.path.join(self._source_subfolder, "adm", "cmake", "occt_defs_flags.cmake")

        # Inject conanbuildinfo, upstream build files are not ready for a CMake wrapper (too much modifications required)
        # Also inject compile flags
        tools.replace_in_file(
            cmakelists,
            "project (OCCT)",
            "project (OCCT)\n"
            "include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)\n"
            "conan_basic_setup(TARGETS)\n"
            "conan_global_flags()")

        # Avoid to add system include/libs directories
        tools.replace_in_file(cmakelists, "3RDPARTY_INCLUDE_DIRS", "CONAN_INCLUDE_DIRS")
        tools.replace_in_file(cmakelists, "3RDPARTY_LIBRARY_DIRS", "CONAN_LIB_DIRS")
        tools.replace_in_file(cmakelists_tools, "3RDPARTY_INCLUDE_DIRS", "CONAN_INCLUDE_DIRS")
        tools.replace_in_file(cmakelists_tools, "3RDPARTY_LIBRARY_DIRS", "CONAN_LIB_DIRS")

        # Do not fail due to "fragile" upstream logic to find dependencies
        tools.replace_in_file(cmakelists, "if (3RDPARTY_NOT_INCLUDED)", "if(0)")
        tools.replace_in_file(cmakelists, "if (3RDPARTY_NO_LIBS)", "if(0)")
        tools.replace_in_file(cmakelists, "if (3RDPARTY_NO_DLLS)", "if(0)")

        # Inject dependencies from conan, and avoid to rely on upstream custom CMake files
        conan_targets = []

        ## freetype
        conan_targets.append("CONAN_PKG::freetype")
        tools.replace_in_file(cmakelists, "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/freetype\")", "")
        tools.replace_in_file(
            occt_csf_cmake,
            "set (CSF_FREETYPE \"freetype\")",
            "set (CSF_FREETYPE \"{}\")".format(" ".join(self.deps_cpp_info["freetype"].libs)))
        ## tcl
        conan_targets.append("CONAN_PKG::tcl")
        tools.replace_in_file(cmakelists, "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/tcl\")", "")
        csf_tcl_libs = "set (CSF_TclLibs \"{}\")".format(" ".join(self.deps_cpp_info["tcl"].libs))
        tools.replace_in_file(occt_csf_cmake, "set (CSF_TclLibs     \"tcl86\")", csf_tcl_libs)
        tools.replace_in_file(occt_csf_cmake, "set (CSF_TclLibs   Tcl)", csf_tcl_libs)
        tools.replace_in_file(occt_csf_cmake, "set (CSF_TclLibs     \"tcl8.6\")", csf_tcl_libs)
        ## tk
        conan_targets.append("CONAN_PKG::tk")
        tools.replace_in_file(cmakelists, "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/tk\")", "")
        csf_tk_libs = "set (CSF_TclTkLibs \"{}\")".format(" ".join(self.deps_cpp_info["tk"].libs))
        tools.replace_in_file(occt_csf_cmake, "set (CSF_TclTkLibs   \"tk86\")", csf_tk_libs)
        tools.replace_in_file(occt_csf_cmake, "set (CSF_TclTkLibs Tk)", csf_tk_libs)
        tools.replace_in_file(occt_csf_cmake, "set (CSF_TclTkLibs   \"tk8.6\")", csf_tk_libs)
        ## fontconfig
        if self._is_linux:
            conan_targets.append("CONAN_PKG::fontconfig")
            tools.replace_in_file(
                occt_csf_cmake,
                "set (CSF_fontconfig  \"fontconfig\")",
                "set (CSF_fontconfig  \"{}\")".format(" ".join(self.deps_cpp_info["fontconfig"].libs)))
        ## tbb
        if self.options.with_tbb:
            conan_targets.append("CONAN_PKG::tbb")
            tools.replace_in_file(cmakelists, "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/tbb\")", "")
            tools.replace_in_file(
                occt_csf_cmake,
                "set (CSF_TBB \"tbb tbbmalloc\")",
                "set (CSF_TBB \"{}\")".format(" ".join(self.deps_cpp_info["tbb"].libs)))
        ## ffmpeg
        if self.options.with_ffmpeg:
            conan_targets.append("CONAN_PKG::ffmpeg")
            tools.replace_in_file(cmakelists, "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/ffmpeg\")", "")
            tools.replace_in_file(
                occt_csf_cmake,
                "set (CSF_FFmpeg \"avcodec avformat swscale avutil\")",
                "set (CSF_FFmpeg \"{}\")".format(" ".join(self.deps_cpp_info["ffmpeg"].libs)))
        ## freeimage
        if self.options.with_freeimage:
            conan_targets.append("CONAN_PKG::freeimage")
            tools.replace_in_file(cmakelists, "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/freeimage\")", "")
            tools.replace_in_file(
                occt_csf_cmake,
                "set (CSF_FreeImagePlus \"freeimage\")",
                "set (CSF_FreeImagePlus \"{}\")".format(" ".join(self.deps_cpp_info["freeimage"].libs)))
        ## openvr
        if self.options.with_openvr:
            conan_targets.append("CONAN_PKG::openvr")
            tools.replace_in_file(cmakelists, "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/openvr\")", "")
            tools.replace_in_file(
                occt_csf_cmake,
                "set (CSF_OpenVR \"openvr_api\")",
                "set (CSF_OpenVR \"{}\")".format(" ".join(self.deps_cpp_info["openvr"].libs)))
        ## rapidjson
        if self.options.with_rapidjson:
            conan_targets.append("CONAN_PKG::rapidjson")
            tools.replace_in_file(cmakelists, "OCCT_INCLUDE_CMAKE_FILE (\"adm/cmake/rapidjson\")", "")

        ## Inject conan targets
        tools.replace_in_file(
            occt_toolkit_cmake,
            "${USED_EXTERNAL_LIBS_BY_CURRENT_PROJECT}",
            "${{USED_EXTERNAL_LIBS_BY_CURRENT_PROJECT}} {}".format(" ".join(conan_targets)))

        # Do not install pdb files
        tools.replace_in_file(
            occt_toolkit_cmake,
            """    install (FILES  ${CMAKE_BINARY_DIR}/${OS_WITH_BIT}/${COMPILER}/bin\\${OCCT_INSTALL_BIN_LETTER}/${PROJECT_NAME}.pdb
             CONFIGURATIONS Debug RelWithDebInfo
             DESTINATION "${INSTALL_DIR_BIN}\\${OCCT_INSTALL_BIN_LETTER}")""",
            "")

        # Honor fPIC option, compiler.cppstd and compiler.libcxx
        tools.replace_in_file(occt_defs_flags_cmake, "-fPIC", "")
        tools.replace_in_file(occt_defs_flags_cmake, "-std=c++0x", "")
        tools.replace_in_file(occt_defs_flags_cmake, "-std=gnu++0x", "")
        tools.replace_in_file(occt_defs_flags_cmake, "-stdlib=libc++", "")
        tools.replace_in_file(occt_csf_cmake,
                              "set (CSF_ThreadLibs  \"pthread rt stdc++\")",
                              "set (CSF_ThreadLibs  \"pthread rt\")")

        # No hardcoded link through #pragma
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "src", "Font", "Font_FontMgr.cxx"),
            "#pragma comment (lib, \"freetype.lib\")",
            "")
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "src", "Draw", "Draw.cxx"),
            """#pragma comment (lib, "tcl" STRINGIZE2(TCL_MAJOR_VERSION) STRINGIZE2(TCL_MINOR_VERSION) ".lib")
#pragma comment (lib, "tk"  STRINGIZE2(TCL_MAJOR_VERSION) STRINGIZE2(TCL_MINOR_VERSION) ".lib")""",
            ""
        )

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)

        # Inject C++ standard from profile since we have removed hardcoded C++11 from upstream build files
        self._cmake.definitions["CMAKE_CXX_STANDARD"] = self.settings.compiler.get_safe("cppstd", "11")

        self._cmake.definitions["BUILD_LIBRARY_TYPE"] = "Shared" if self.options.shared else "Static"
        self._cmake.definitions["INSTALL_TEST_CASES"] = False
        self._cmake.definitions["BUILD_RESOURCES"] = False
        self._cmake.definitions["BUILD_RELEASE_DISABLE_EXCEPTIONS"] = True
        if self.settings.build_type == "Debug":
            self._cmake.definitions["BUILD_WITH_DEBUG"] = self.options.extended_debug_messages
        self._cmake.definitions["BUILD_USE_PCH"] = False
        self._cmake.definitions["INSTALL_SAMPLES"] = False

        self._cmake.definitions["INSTALL_DIR_LAYOUT"] = "Unix"
        self._cmake.definitions["INSTALL_DIR_BIN"] = "bin"
        self._cmake.definitions["INSTALL_DIR_LIB"] = "lib"
        self._cmake.definitions["INSTALL_DIR_INCLUDE"] = "include"
        self._cmake.definitions["INSTALL_DIR_RESOURCE"] = "res/resource"
        self._cmake.definitions["INSTALL_DIR_DATA"] = "res/data"
        self._cmake.definitions["INSTALL_DIR_SAMPLES"] = "res/samples"
        self._cmake.definitions["INSTALL_DIR_DOC"] = "res/doc"

        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["BUILD_SAMPLES_MFC"] = False
        self._cmake.definitions["BUILD_SAMPLES_QT"] = False
        self._cmake.definitions["BUILD_Inspector"] = False
        if tools.is_apple_os(self.settings.os):
            self._cmake.definitions["USE_GLX"] = False
        if self.settings.os == "Windows":
            self._cmake.definitions["USE_D3D"] = False
        self._cmake.definitions["BUILD_ENABLE_FPE_SIGNAL_HANDLER"] = False
        self._cmake.definitions["BUILD_DOC_Overview"] = False

        self._cmake.definitions["USE_FREEIMAGE"] = self.options.with_freeimage
        self._cmake.definitions["USE_OPENVR"] = self.options.with_openvr
        self._cmake.definitions["USE_FFMPEG"] = self.options.with_ffmpeg
        self._cmake.definitions["USE_TBB"] = self.options.with_tbb
        self._cmake.definitions["USE_RAPIDJSON"] = self.options.with_rapidjson

        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def _replace_package_folder(self, source, target):
        new_name = ""
        if os.path.isdir(os.path.join(self.package_folder, source)):
            tools.rmdir(os.path.join(self.package_folder, target))
            tools.rename(
                os.path.join(self.package_folder, source),
                os.path.join(self.package_folder, target))

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(
            "LICENSE_LGPL_21.txt",
            src=self._source_subfolder,
            dst="licenses")
        self.copy(
            "OCCT_LGPL_EXCEPTION.txt",
            src=self._source_subfolder,
            dst="licenses")
        tools.rmdir(os.path.join(self.package_folder, "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        if self.settings.build_type == "Debug":
            self._replace_package_folder("libd", "lib")
            self._replace_package_folder("bind", "bin")
        elif self.settings.build_type == "RelWithDebInfo":
            self._replace_package_folder("libi", "lib")
            self._replace_package_folder("bini", "bin")

        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {target: "OpenCASCADE::{}".format(target) for module in self._occt_components.values() for target in module}
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
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    @property
    def _occt_components(self):
        # TODO: Might be improved to something more robust and maintainable where
        # we extract information from source code at package time and write it
        # in a file read at consume time. We could extract this information like
        # this:
        # - list of modules and potential associated components from adm/MODULE file
        # - add component if its lib file can be found in lib folder after the build
        # - dependencies of each component from src/<component>/EXTERNLIB file

        # External libs
        def _ffmpeg():
            return ["ffmpeg::ffmpeg"] if self.options.with_ffmpeg else []

        def _freeimage():
            return ["freeimage::freeimage"] if self.options.with_freeimage else []

        def _openvr():
            return ["openvr::openvr"] if self.options.with_openvr else []

        def _rapidjson():
            return ["rapidjson::rapidjson"] if self.options.with_rapidjson else []

        def _tbb():
            return ["tbb::tbb"] if self.options.with_tbb else []

        def _fontconfig():
            return ["fontconfig::fontconfig"] if self._is_linux else []

        def _xorg():
            return ["xorg::xorg"] if self._is_linux else []

        # system libs
        def _dl():
            return ["dl"] if self._is_linux else []

        def _pthread():
            return ["pthread"] if self._is_linux else []

        def _rt():
            return ["rt"] if self._is_linux else []

        def _log():
            return ["log"] if self.settings.os == "Android" else []

        def _advapi32():
            return ["advapi32"] if self.settings.os == "Windows" else []

        def _gdi32():
            return ["gdi32"] if self.settings.os == "Windows" else []

        def _psapi():
            return ["psapi"] if self.settings.os == "Windows" else []

        def _shell32():
            return ["shell32"] if self.settings.os == "Windows" else []

        def _user32():
            return ["user32"] if self.settings.os == "Windows" else []

        def _winmm():
            return ["winmm"] if self.settings.os == "Windows" else []

        def _wsock32():
            return ["wsock32"] if self.settings.os == "Windows" else []

        # frameworks
        def _appkit():
            appkit = []
            if tools.is_apple_os(self.settings.os):
                appkit = ["UIKit"] if self.settings.os == "iOS" else ["Appkit"]
            return appkit

        def _iokit():
            return ["IOKit"] if tools.is_apple_os(self.settings.os) else []

        # components
        return {
            "FoundationClasses": {
                "TKernel": {
                    "external": _tbb(),
                    "system_libs": _dl() + _pthread() + _rt() + _log() + _advapi32() + _gdi32() + _psapi() + _user32() + _wsock32(),
                },
                "TKMath": {
                    "internal": ["TKernel"],
                    "external": _tbb(),
                },
            },
            "ModelingData": {
                "TKG2d": {"internal": ["TKernel", "TKMath"]},
                "TKG3d": {"internal": ["TKMath", "TKernel", "TKG2d"]},
                "TKGeomBase": {
                    "internal": ["TKernel", "TKMath", "TKG2d", "TKG3d"],
                    "external": _tbb(),
                },
                "TKBRep": {"internal": ["TKMath", "TKernel", "TKG2d", "TKG3d", "TKGeomBase"]},
            },
            "ModelingAlgorithms": {
                "TKGeomAlgo": {"internal": ["TKernel", "TKMath", "TKG3d", "TKG2d", "TKGeomBase", "TKBRep"]},
                "TKTopAlgo": {
                    "internal": ["TKMath", "TKernel", "TKG2d", "TKG3d", "TKGeomBase", "TKBRep", "TKGeomAlgo"],
                    "external": _tbb(),
                },
                "TKPrim": {"internal": ["TKBRep", "TKernel", "TKMath", "TKG2d", "TKGeomBase", "TKG3d", "TKTopAlgo"]},
                "TKBO": {
                    "internal": ["TKBRep", "TKTopAlgo", "TKMath", "TKernel", "TKG2d", "TKG3d", "TKGeomAlgo", "TKGeomBase",
                                 "TKPrim", "TKShHealing"],
                    "external": _tbb(),
                },
                "TKBool": {"internal": ["TKBRep", "TKTopAlgo", "TKMath", "TKernel", "TKPrim", "TKG2d", "TKG3d", "TKShHealing",
                           "TKGeomBase", "TKGeomAlgo", "TKBO"]},
                "TKHLR": {"internal": ["TKBRep", "TKernel", "TKMath", "TKGeomBase", "TKG2d", "TKG3d", "TKGeomAlgo", "TKTopAlgo"]},
                "TKFillet": {"internal": ["TKBRep", "TKernel", "TKMath", "TKGeomBase", "TKGeomAlgo", "TKG2d", "TKTopAlgo", "TKG3d",
                             "TKBool", "TKShHealing", "TKBO"]},
                "TKOffset": {"internal": ["TKFillet", "TKBRep", "TKTopAlgo", "TKMath", "TKernel", "TKGeomBase", "TKG2d", "TKG3d",
                             "TKGeomAlgo", "TKShHealing", "TKBO", "TKPrim", "TKBool"]},
                "TKFeat": {"internal": ["TKBRep", "TKTopAlgo", "TKGeomAlgo", "TKMath", "TKernel", "TKGeomBase", "TKPrim", "TKG2d",
                           "TKBO", "TKG3d", "TKBool", "TKShHealing"]},
                "TKMesh": {"internal": ["TKernel", "TKMath", "TKBRep", "TKTopAlgo", "TKShHealing", "TKGeomBase", "TKG3d", "TKG2d"]},
                "TKXMesh": {"internal": ["TKBRep", "TKMath", "TKernel", "TKG2d", "TKG3d", "TKMesh"]},
                "TKShHealing": {
                    "internal": ["TKBRep", "TKernel", "TKMath", "TKG2d", "TKTopAlgo", "TKG3d", "TKGeomBase", "TKGeomAlgo"],
                    "system_libs": _wsock32(),
                },
            },
            "Visualization": {
                "TKService": {
                    "internal": ["TKernel", "TKMath"],
                    "external": ["freetype::freetype", "opengl::opengl"] + _ffmpeg() + _freeimage() + _openvr() + _xorg() + _fontconfig(),
                    "system_libs": _advapi32() + _gdi32() + _user32() + _winmm(),
                    "frameworks": _appkit() + _iokit(),
                },
                "TKV3d": {
                    "internal": ["TKBRep", "TKMath", "TKernel", "TKService", "TKShHealing", "TKTopAlgo", "TKG2d", "TKG3d",
                                 "TKGeomBase", "TKMesh", "TKGeomAlgo", "TKHLR"],
                    "external": ["freetype::freetype", "opengl::opengl"] + _tbb() + _xorg(),
                    "system_libs": _gdi32() + _user32(),
                },
                "TKOpenGl": {
                    "internal": ["TKernel", "TKService", "TKMath"],
                    "external": ["freetype::freetype", "opengl::opengl"] + _tbb() + _xorg(),
                    "system_libs": _gdi32() + _user32(),
                    "frameworks": _appkit() + _iokit(),
                },
                "TKMeshVS": {"internal": ["TKV3d", "TKMath", "TKService", "TKernel", "TKG3d", "TKG2d"]},
            },
            "ApplicationFramework": {
                "TKCDF": {"internal": ["TKernel"]},
                "TKLCAF": {"internal": ["TKCDF", "TKernel"]},
                "TKCAF": {"internal": ["TKernel", "TKGeomBase", "TKBRep", "TKTopAlgo", "TKMath", "TKG2d", "TKG3d", "TKCDF",
                          "TKLCAF", "TKBO"]},
                "TKBinL": {"internal": ["TKCDF", "TKernel", "TKLCAF"]},
                "TKXmlL": {"internal": ["TKCDF", "TKernel", "TKMath", "TKLCAF"]},
                "TKBin": {"internal": ["TKBRep", "TKMath", "TKernel", "TKG2d", "TKG3d", "TKCAF", "TKCDF", "TKLCAF", "TKBinL"]},
                "TKXml": {"internal": ["TKCDF", "TKernel", "TKMath", "TKBRep", "TKG2d", "TKGeomBase", "TKG3d", "TKLCAF", "TKCAF",
                          "TKXmlL"]},
                "TKStdL": {"internal": ["TKernel", "TKCDF", "TKLCAF"]},
                "TKStd": {"internal": ["TKernel", "TKCDF", "TKCAF", "TKLCAF", "TKBRep", "TKMath", "TKG2d", "TKG3d", "TKStdL"]},
                "TKTObj": {"internal": ["TKCDF", "TKernel", "TKMath", "TKLCAF"]},
                "TKBinTObj": {"internal": ["TKCDF", "TKernel", "TKTObj", "TKMath", "TKLCAF", "TKBinL"]},
                "TKXmlTObj": {"internal": ["TKCDF", "TKernel", "TKTObj", "TKMath", "TKLCAF", "TKXmlL"]},
                "TKVCAF": {"internal": ["TKernel", "TKGeomBase", "TKBRep", "TKTopAlgo", "TKMath", "TKService", "TKG2d", "TKG3d",
                           "TKCDF", "TKLCAF", "TKBO", "TKCAF", "TKV3d"]},
            },
            "DataExchange": {
                "TKXSBase": {"internal": ["TKBRep", "TKernel", "TKMath", "TKG2d", "TKG3d", "TKTopAlgo", "TKGeomBase", "TKShHealing"]},
                "TKSTEPBase": {"internal": ["TKernel", "TKXSBase", "TKMath"]},
                "TKSTEPAttr": {"internal": ["TKernel", "TKXSBase", "TKSTEPBase"]},
                "TKSTEP209": {"internal": ["TKernel", "TKXSBase", "TKSTEPBase"]},
                "TKSTEP": {"internal": ["TKernel", "TKSTEPAttr", "TKSTEP209", "TKSTEPBase", "TKBRep", "TKMath", "TKG2d",
                           "TKShHealing", "TKTopAlgo", "TKG3d", "TKGeomBase", "TKGeomAlgo", "TKXSBase"]},
                "TKIGES": {"internal": ["TKBRep", "TKernel", "TKMath", "TKTopAlgo", "TKShHealing", "TKG2d", "TKG3d", "TKGeomBase",
                           "TKGeomAlgo", "TKPrim", "TKBool", "TKXSBase"]},
                "TKXCAF": {"internal": ["TKBRep", "TKernel", "TKMath", "TKService", "TKG2d", "TKTopAlgo", "TKV3d", "TKCDF", "TKLCAF",
                           "TKG3d", "TKCAF", "TKVCAF"]},
                "TKXDEIGES": {"internal": ["TKBRep", "TKernel", "TKMath", "TKXSBase", "TKCDF", "TKLCAF", "TKG2d", "TKG3d", "TKXCAF",
                              "TKIGES"]},
                "TKXDESTEP": {"internal": ["TKBRep", "TKSTEPAttr", "TKernel", "TKMath", "TKXSBase", "TKTopAlgo", "TKG2d", "TKCAF",
                              "TKSTEPBase", "TKCDF", "TKLCAF", "TKG3d", "TKXCAF", "TKSTEP", "TKShHealing"]},
                "TKSTL": {"internal": ["TKernel", "TKMath", "TKBRep", "TKG2d", "TKG3d", "TKTopAlgo"]},
                "TKVRML": {"internal": ["TKBRep", "TKTopAlgo", "TKMath", "TKGeomBase", "TKernel", "TKPrim", "TKG2d", "TKG3d",
                           "TKMesh", "TKHLR", "TKService", "TKGeomAlgo", "TKV3d", "TKLCAF", "TKXCAF"]},
                "TKXmlXCAF": {"internal": ["TKXmlL", "TKBRep", "TKCDF", "TKMath", "TKernel", "TKService", "TKG2d", "TKGeomBase",
                              "TKCAF", "TKG3d", "TKLCAF", "TKXCAF", "TKXml"]},
                "TKBinXCAF": {"internal": ["TKBRep", "TKXCAF", "TKMath", "TKService", "TKernel", "TKBinL", "TKG2d", "TKCAF", "TKCDF",
                              "TKG3d", "TKLCAF", "TKBin"]},
                "TKRWMesh": {
                    "internal": ["TKernel", "TKMath", "TKMesh", "TKXCAF", "TKLCAF", "TKV3d", "TKBRep", "TKG3d", "TKService"],
                    "external": _rapidjson(),
                },
            },
            "Draw": {
                "TKDraw": {
                    "internal": ["TKernel", "TKG2d", "TKGeomBase", "TKG3d", "TKMath", "TKBRep", "TKGeomAlgo", "TKTopAlgo",
                                 "TKShHealing", "TKMesh", "TKService", "TKHLR"],
                    "external": ["tcl::tcl", "tk::tk"] + _tbb() + _xorg(),
                    "system_libs": _advapi32() + _gdi32() + _user32() + _shell32(),
                    "frameworks": _appkit() + _iokit(),
                },
                "TKTopTest": {"internal": ["TKBRep", "TKGeomAlgo", "TKTopAlgo", "TKernel", "TKMath", "TKBO", "TKG2d", "TKG3d",
                              "TKDraw", "TKHLR", "TKGeomBase", "TKMesh", "TKService", "TKV3d", "TKFillet", "TKPrim",
                              "TKBool", "TKOffset", "TKFeat", "TKShHealing"]},
                "TKViewerTest": {
                    "internal": ["TKGeomBase", "TKFillet", "TKBRep", "TKTopAlgo", "TKHLR", "TKernel", "TKMath",
                                 "TKService", "TKShHealing", "TKBool", "TKPrim", "TKGeomAlgo", "TKG2d", "TKTopTest",
                                 "TKG3d", "TKOffset", "TKMesh", "TKV3d", "TKDraw", "TKOpenGl"],
                    "external": ["freetype::freetype", "opengl::opengl", "tcl::tcl", "tk::tk"] + _tbb() + _xorg(),
                    "system_libs": _gdi32() + _user32(),
                    "frameworks": _appkit() + _iokit(),
                },
                "TKXSDRAW": {"internal": ["TKBRep", "TKV3d", "TKMath", "TKernel", "TKService", "TKXSBase", "TKMeshVS", "TKG3d",
                             "TKViewerTest", "TKG2d", "TKSTEPBase", "TKTopAlgo", "TKGeomBase", "TKGeomAlgo", "TKMesh",
                             "TKDraw", "TKSTEP", "TKIGES", "TKSTL", "TKVRML", "TKLCAF", "TKDCAF", "TKXCAF", "TKRWMesh"]},
                "TKDCAF": {"internal": ["TKGeomBase", "TKBRep", "TKGeomAlgo", "TKernel", "TKMath", "TKG2d", "TKG3d", "TKDraw",
                           "TKCDF", "TKV3d", "TKService", "TKLCAF", "TKFillet", "TKTopAlgo", "TKPrim", "TKBool",
                           "TKBO", "TKCAF", "TKVCAF", "TKViewerTest", "TKStd", "TKStdL", "TKBin", "TKBinL", "TKXml",
                           "TKXmlL"]},
                "TKXDEDRAW": {"internal": ["TKCDF", "TKBRep", "TKXCAF", "TKernel", "TKIGES", "TKV3d", "TKMath", "TKService",
                              "TKXSBase", "TKG2d", "TKCAF", "TKVCAF", "TKDraw", "TKTopAlgo", "TKLCAF", "TKG3d",
                              "TKSTEPBase", "TKSTEP", "TKMesh", "TKXSDRAW", "TKXDEIGES", "TKXDESTEP", "TKDCAF",
                              "TKViewerTest", "TKBinXCAF", "TKXmlXCAF", "TKVRML"]},
                "TKTObjDRAW": {"internal": ["TKernel", "TKCDF", "TKLCAF", "TKTObj", "TKMath", "TKDraw", "TKDCAF", "TKBinTObj",
                               "TKXmlTObj"]},
                "TKQADraw": {
                    "internal": ["TKBRep", "TKMath", "TKernel", "TKService", "TKG2d", "TKDraw", "TKV3d", "TKGeomBase",
                                 "TKG3d", "TKViewerTest", "TKCDF", "TKDCAF", "TKLCAF", "TKFillet", "TKTopAlgo", "TKHLR",
                                 "TKBool", "TKGeomAlgo", "TKPrim", "TKBO", "TKShHealing", "TKOffset", "TKFeat", "TKCAF",
                                 "TKVCAF", "TKIGES", "TKXSBase", "TKMesh", "TKXCAF", "TKBinXCAF", "TKSTEP", "TKSTEPBase",
                                 "TKXDESTEP", "TKXSDRAW", "TKSTL", "TKXml", "TKTObj", "TKXmlL", "TKBin", "TKBinL", "TKStd",
                                 "TKStdL"],
                    "external": _tbb(),
                    "system_libs": _advapi32() + _gdi32() + _user32(),
                },
            },
        }

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenCASCADE"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenCASCADE"

        def _to_qualified_name(target):
            return "occt_{}".format(target.lower())

        for component, targets in self._occt_components.items():
            conan_component_name = _to_qualified_name(component)
            self.cpp_info.components[conan_component_name].names["cmake_find_package"] = component
            self.cpp_info.components[conan_component_name].names["cmake_find_package_multi"] = component

            for target_lib, target_deps in targets.items():
                conan_component_target_name = _to_qualified_name(target_lib)
                requires = [_to_qualified_name(internal) for internal in target_deps.get("internal", [])] + \
                           target_deps.get("external", [])
                system_libs = target_deps.get("system_libs", [])
                frameworks = target_deps.get("frameworks", [])

                self.cpp_info.components[conan_component_target_name].names["cmake_find_package"] = target_lib
                self.cpp_info.components[conan_component_target_name].names["cmake_find_package_multi"] = target_lib
                self.cpp_info.components[conan_component_target_name].builddirs.append(self._module_subfolder)
                self.cpp_info.components[conan_component_target_name].build_modules["cmake_find_package"] = [self._module_file_rel_path]
                self.cpp_info.components[conan_component_target_name].build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
                self.cpp_info.components[conan_component_target_name].libs = [target_lib]
                self.cpp_info.components[conan_component_target_name].requires = requires
                self.cpp_info.components[conan_component_target_name].system_libs = system_libs
                self.cpp_info.components[conan_component_target_name].frameworks = frameworks
                if self.settings.os == "Windows" and not self.options.shared:
                    self.cpp_info.components[conan_component_target_name].defines.append("OCCT_STATIC_BUILD")

                self.cpp_info.components[conan_component_name].requires.append(conan_component_target_name)

        # DRAWEXE executable is not created if static build
        if self.options.shared:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
