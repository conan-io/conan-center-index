from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class OcctConan(ConanFile):
    name = "occt"
    description = """a software development platform providing services for 3D
        surface and solid modeling, CAD data exchange, and visualization."""
    homepage = "https://github.com/Open-Cascade-SAS/OCCT"
    url = "https://github.com/conan-io/conan-center-index"
    license = "LGPL-2.1-or-later"
    topics = ("3D", "modeling")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    requires = [("tcl/8.6.10"),
                ("tk/8.6.10"),
                ("freetype/2.10.4"),
                ("opengl/system")]
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

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.upper() + "-" + \
            self.version.replace(".", "_")
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
             DESTINATION "${INSTALL_DIR_BIN}\${OCCT_INSTALL_BIN_LETTER}")""",
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
            if os.path.isdir(os.path.join(self.package_folder, "libd")):
                tools.rmdir(os.path.join(self.package_folder, "lib"))
                tools.rename(
                    os.path.join(self.package_folder, "libd"),
                    os.path.join(self.package_folder, "lib"))

    def package_info(self):
        libs = set(tools.collect_libs(self))
        modules = self._modules
        modules_tks = self._modules_toolkits
        tks = [tk
               for module in reversed(modules)
               for tk in reversed(modules_tks[module])
               if tk in libs]
        self.cpp_info.libs = tks
