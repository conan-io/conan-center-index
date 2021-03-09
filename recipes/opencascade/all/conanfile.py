from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class OpenCascadeConan(ConanFile):
    name = "opencascade"
    description = "A software development platform providing services for 3D " \
                  "surface and solid modeling, CAD data exchange, and visualization."
    homepage = "https://github.com/Open-Cascade-SAS/OCCT"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    topics = ("conan", "opencascade", "occt", "3d", "modeling", "cad")

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    '''
    Modules taken from 'adm/MODULES'.
    Each module depends on modules after it.
    '''
    @property
    def _modules(self):
        return ['FoundationClasses', 'ModelingData', 'ModelingAlgorithms',
                'Visualization', 'ApplicationFramework', 'DataExchange',
                'Draw']

    '''
    Toolkits in each module taken from 'adm/MODULES'.
    Each toolkit may depend on toolkits after it but not ones before it.
    '''
    @property
    def _modules_toolkits(self):
        return {
            'FoundationClasses': ['TKernel', 'TKMath'],
            'ModelingData': ['TKG2d', 'TKG3d', 'TKGeomBase', 'TKBRep'],
            'ModelingAlgorithms': [
                'TKGeomAlgo', 'TKTopAlgo', 'TKPrim', 'TKBO', 'TKBool', 'TKHLR',
                'TKFillet', 'TKOffset', 'TKFeat', 'TKMesh', 'TKXMesh',
                'TKShHealing'],
            'Visualization': [
                'TKService', 'TKV3d', 'TKOpenGl', 'TKMeshVS', 'TKIVtk',
                'TKD3DHost'],
            'ApplicationFramework': [
                'TKCDF', 'TKLCAF', 'TKCAF', 'TKBinL', 'TKXmlL', 'TKBin',
                'TKXml', 'TKStdL', 'TKStd', 'TKTObj', 'TKBinTObj', 'TKXmlTObj',
                'TKVCAF'],
            'DataExchange': [
                'TKXSBase', 'TKSTEPBase', 'TKSTEPAttr', 'TKSTEP209', 'TKSTEP',
                'TKIGES', 'TKXCAF', 'TKXDEIGES', 'TKXDESTEP', 'TKSTL',
                'TKVRML', 'TKXmlXCAF', 'TKBinXCAF', 'TKRWMesh'],
            'Draw': [
                'TKDraw', 'TKTopTest', 'TKViewerTest', 'TKXSDRAW', 'TKDCAF',
                'TKXDEDRAW', 'TKTObjDRAW', 'TKQADraw', 'TKIVtkDraw']}

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        self.requires("tcl/8.6.10")
        self.requires("tk/8.6.10")
        self.requires("freetype/2.10.4")
        self.requires("opengl/system")

    def validate(self):
        if self.settings.compiler == "clang" and self.settings.compiler.version == "6.0":
            raise ConanInvalidConfiguration("Clang 6.0 is not supported.")
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.version == "14":
            raise ConanInvalidConfiguration("Visual Studio 14 is not supported.")
        if self.settings.compiler == "Visual Studio" and self.settings.compiler.version == "15":
            raise ConanInvalidConfiguration("Visual Studio 15 is not supported.")
        if self.settings.compiler == "Visual Studio" and \
           "MT" in str(self.settings.compiler.runtime) and self.options.shared:
            raise ConanInvalidConfiguration("Visual Studio and Runtime MT is not supported for shared library.")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "OCCT-" + self.version.replace(".", "_")
        tools.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "project (OCCT)",
            '''project (OCCT)
                include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                conan_basic_setup(TARGETS)''')

        tools.replace_in_file(
            os.path.join(self._source_subfolder, "CMakeLists.txt"),
            "${3RDPARTY_INCLUDE_DIRS}",
            "${CONAN_INCLUDE_DIRS}")

        tools.replace_in_file(
            os.path.join(self._source_subfolder,
                         "adm/cmake/occt_toolkit.cmake"),
            "${USED_EXTERNAL_LIBS_BY_CURRENT_PROJECT}",
            """${USED_EXTERNAL_LIBS_BY_CURRENT_PROJECT}
            CONAN_PKG::tcl CONAN_PKG::tk CONAN_PKG::freetype""")

        tools.replace_in_file(
            os.path.join(self._source_subfolder,
                         "adm/cmake/occt_toolkit.cmake"),
            """    install (FILES  ${CMAKE_BINARY_DIR}/${OS_WITH_BIT}/${COMPILER}/bin\\${OCCT_INSTALL_BIN_LETTER}/${PROJECT_NAME}.pdb
             CONFIGURATIONS Debug RelWithDebInfo
             DESTINATION "${INSTALL_DIR_BIN}\\${OCCT_INSTALL_BIN_LETTER}")""",
            "")

        tools.replace_in_file(
            os.path.join(self._source_subfolder,
                         "src/Font/Font_FontMgr.cxx"),
            "#pragma comment (lib, \"freetype.lib\")",
            "")

        tcl_libs = self.deps_cpp_info["tcl"].libs
        tcl_lib = next(filter(lambda lib: "tcl8" in lib, tcl_libs))
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "adm/cmake/tcl.cmake"),
            "${CSF_TclLibs}",
            tcl_lib)

        tk_libs = self.deps_cpp_info["tk"].libs
        tk_lib = next(filter(lambda lib: "tk8" in lib, tk_libs))
        tools.replace_in_file(
            os.path.join(self._source_subfolder, "adm/cmake/tk.cmake"),
            "${CSF_TclTkLibs}",
            tk_lib)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["3RDPARTY_TCL_LIBRARY_DIR"] = \
            os.path.join(self.deps_cpp_info["tcl"].rootpath, "lib")
        self._cmake.definitions["3RDPARTY_TCL_INCLUDE_DIR"] = \
            self.deps_cpp_info["tcl"].include_paths[0]
        self._cmake.definitions["3RDPARTY_TK_LIBRARY_DIR"] = \
            os.path.join(self.deps_cpp_info["tk"].rootpath, "lib")
        self._cmake.definitions["3RDPARTY_TK_INCLUDE_DIR"] = \
            self.deps_cpp_info["tk"].include_paths[0]
        if not self.options.shared:
            self._cmake.definitions["BUILD_LIBRARY_TYPE"] = "Static"

        self._cmake.definitions["INSTALL_DIR_BIN"] = "bin"
        self._cmake.definitions["INSTALL_DIR_INCLUDE"] = "include"
        self._cmake.definitions["INSTALL_DIR_LIB"] = "lib"
        self._cmake.definitions["INSTALL_DIR_RESOURCE"] = "res/resource"
        self._cmake.definitions["INSTALL_DIR_DATA"] = "res/data"
        self._cmake.definitions["INSTALL_DIR_SAMPLES"] = "res/samples"
        self._cmake.definitions["INSTALL_DIR_DOC"] = "res/doc"
        self._cmake.definitions["INSTALL_DIR_LAYOUT"] = "Unix"

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
        tools.rmdir(os.path.join(self.package_folder, "lib/cmake"))
        if self.settings.build_type == "Debug":
            self._replace_package_folder("libd", "lib")
            self._replace_package_folder("bind", "bin")
        elif self.settings.build_type == "RelWithDebInfo":
            self._replace_package_folder("libi", "lib")
            self._replace_package_folder("bini", "bin")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "OpenCASCADE"
        self.cpp_info.names["cmake_find_package_multi"] = "OpenCASCADE"
        libs = set(tools.collect_libs(self))
        modules = self._modules
        modules_tks = self._modules_toolkits
        for (index, module) in enumerate(modules):
            self.cpp_info.components[module].libs = [
                tk for tk in reversed(modules_tks[module])
                if tk in libs]
            if index > 0:
                self.cpp_info.components[module].requires = list(modules[:index])

        # 3rd-party requirements taken from https://dev.opencascade.org/doc/overview/html/index.html#intro_req_libs
        self.cpp_info.components["Draw"].requires.extend(
            ["tcl::tcl", "tk::tk"])
        self.cpp_info.components["Visualization"].requires.extend(
            ["freetype::freetype", "opengl::opengl"])
