import os
import re

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class VTKConan(ConanFile):
    name = "vtk"
    # version = "9.0.1"  # DO NOT SUBMIT!!! Remove this line in final version of PR to conan-center-index
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://vtk.org/"
    license = "BSD license"
    description = "Visualization Toolkit by Kitware"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    source_subfolder = "source_subfolder"
    topics = ("conan", "VTK", "3D rendering", "2D plotting", "3D interaction", "3D manipulation", 
                "graphics", "image processing", "scientific visualization", "geometry modeling")
    groups = ["StandAlone", "Rendering", "MPI", "Qt", "Imaging", "Tk", "Views", "Web"]
    modules = [
        "ChartsCore",
        "CommonComputationalGeometry",
        "CommonCore",
        "CommonDataModel",
        "CommonExecutionModel",
        "CommonMisc",
        "CommonSystem",
        "CommonTransforms",
        "diy2",
        "DomainsChemistry",
        "DomainsChemistryOpenGL2",
        "DomainsParallelChemistry",
        "FiltersAMR",
        "FiltersCore",
        "FiltersExtraction",
        "FiltersFlowPaths",
        "FiltersGeneral",
        "FiltersGeneric",
        "FiltersGeometry",
        "FiltersHybrid",
        "FiltersHyperTree",
        "FiltersImaging",
        "FiltersImaging",
        "FiltersModeling",
        "FiltersParallel",
        "FiltersParallelDIY2",
        "FiltersParallelGeometry",
        "FiltersParallelImaging",
        "FiltersParallelMPI",
        "FiltersParallelVerdict",
        "FiltersPoints",
        "FiltersProgrammable",
        "FiltersSelection",
        "FiltersSMP",
        "FiltersSources",
        "FiltersStatistics",
        "FiltersTexture",
        "FiltersTopology",
        "FiltersVerdict",
        "GeovisCore",
        "GUISupportQt",
        "GUISupportQtSQL",
        "ImagingColor",
        "ImagingColor",
        "ImagingCore",
        "ImagingFourier",
        "ImagingFourier",
        "ImagingGeneral",
        "ImagingGeneral",
        "ImagingHybrid",
        "ImagingHybrid",
        "ImagingMath",
        "ImagingMath",
        "ImagingMorphological",
        "ImagingMorphological",
        "ImagingOpenGL2",
        "ImagingSources",
        "ImagingSources",
        "ImagingStatistics",
        "ImagingStatistics",
        "ImagingStencil",
        "ImagingStencil",
        "InfovisCore",
        "InfovisLayout",
        "InteractionImage",
        "InteractionImage",
        "InteractionStyle",
        "InteractionWidgets",
        "IOAMR",
        "IOAsynchronous",
        "IOCityGML",
        "IOCore",
        "IOEnSight",
        "IOExodus",
        "IOExport",
        "IOExportOpenGL2",
        "IOExportPDF",
        "IOGeometry",
        "IOImage",
        "IOImport",
        "IOInfovis",
        "IOLegacy",
        "IOLSDyna",
        "IOMINC",
        "IOMovie",
        "IOMPIImage",
        "IOMPIParallel",
        "IONetCDF",
        "IOParallel",
        "IOParallelNetCDF",
        "IOParallelXML",
        "IOPLY",
        "IOSegY",
        "IOSQL",
        "IOTecplotTable",
        "IOVeraOut",
        "IOVideo",
        "IOXdmf3",
        "IOXML",
        "IOXMLParser",
        "ParallelCore",
        "ParallelMPI",
        "RenderingAnnotation",
        "RenderingContext2D",
        "RenderingContextOpenGL2",
        "RenderingCore",
        "RenderingFreeType",
        "RenderingGL2PSOpenGL2",
        "RenderingImage",
        "RenderingImage",
        "RenderingLabel",
        "RenderingLICOpenGL2",
        "RenderingLOD",
        "RenderingOpenGL2",
        "RenderingOpenVR",
        "RenderingQt",
        "RenderingTk",
        "RenderingVolume",
        "RenderingVolumeOpenGL2",
        "ViewsContext2D",
        "ViewsContext2D",
        "ViewsCore",
        "ViewsGeovis",
        "ViewsInfovis",
        "ViewsQt",
        "WebCore",
        "WebGLExporter",
        "WebPython",
    ]
    options = dict({"shared": [True, False], "fPIC": [True, False],
    }, **{"group_{}".format(group.lower()): [True, False] for group in groups},
    **{"module_{}".format(module.lower()): [True, False] for module in modules}
    )
    # default_options are set to the same values as clean VTK 9.0.1 cmake installation has, except "shared" which Conan require to be "False" by default.
    default_options = dict({
        "shared": False,
        "fPIC": False,
        }, **{"group_{}".format(group.lower()): True for group in groups if (group in ["StandAlone", "Rendering"])},
        **{"group_{}".format(group.lower()): False for group in groups if (group not in ["StandAlone", "Rendering"])},
        **{"module_{}".format(module.lower()): False for module in modules})
    # options = {"shared": [True, False], "with_qt": [True, False], "mpi": [True, False],
    #             "fPIC": [True, False], "minimal": [True, False], "ioxml": [True, False],
    #             "ioexport": [True, False], "mpi_minimal": [True, False]}
    # default_options = {"shared": False, "with_qt": False, "mpi": False, "fPIC": False,
    #             "minimal": False, "ioxml": False, "ioexport": False, "mpi_minimal": False}
    short_paths = True
    _cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.os == "Linux":
            raise ConanInvalidConfiguration("VTK Conan package do not support Linux yet. Any help appreciated!")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{}-{}".format(self.name, self.version), self.source_subfolder)

    # Below code is inncorrect and should be removed after successful Lnx package build.
    # Until then, keeping it for reference. 
    # def _system_package_architecture(self):
    #     if tools.os_info.with_apt:
    #         if self.settings.arch == "x86":
    #             return ':i386'
    #         elif self.settings.arch == "x86_64":
    #             return ':amd64'
    #
    #     if tools.os_info.with_yum:
    #         if self.settings.arch == "x86":
    #             return '.i686'
    #         elif self.settings.arch == 'x86_64':
    #             return '.x86_64'
    #     return ""
    #
    # def build_requirements(self):
    #     pack_names = None
    #     if not self.options.minimal and tools.os_info.is_linux:
    #         if tools.os_info.with_apt:
    #             pack_names = [
    #                 "freeglut3-dev",
    #                 "mesa-common-dev",
    #                 "mesa-utils-extra",
    #                 "libgl1-mesa-dev",
    #                 "libglapi-mesa",
    #                 "libsm-dev",
    #                 "libx11-dev",
    #                 "libxext-dev",
    #                 "libxt-dev",
    #                 "libglu1-mesa-dev"]
    #
    #     if pack_names:
    #         installer = tools.SystemPackageTool()
    #         for item in pack_names:
    #             installer.install(item + self._system_package_architecture())
    
    def requirements(self):
        if self.options.group_rendering:
            # 1) Is it correct that "opengl/system" is required for every OS?
            # 2) Is it correct that "opengl/system" is required even when compiled without Qt? Probably this question was answered itself due to above "if"
            self.requires("opengl/system")
        if self.settings.os == "Linux":
            if self.options.x11:
                # Do we need "xorg/system"?
                self.requires("xorg/system")
        if self.options.module_ioxdmf3:
            self.requires("boost/1.74.0") # DO NOT SUBMIT! Was "boost/1.66.0@conan/stable" foe VTK 8.2.0. What should be for VTK 9.0.1?
        # if self.options.with_qt:
        if self.options.group_qt:
            # FIXME: Missing qt recipe. Qt recipe PR: https://github.com/conan-io/conan-center-index/pull/1759
            # When qt available, "self.requires("qt/5.15.1")" should replace below line.
            raise ConanInvalidConfiguration("qt is not (yet) available on conan-center-index")
        
                
    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_TESTING"] = "OFF"
        self._cmake.definitions["BUILD_EXAMPLES"] = "OFF"
        self._cmake.definitions["BUILD_SHARED_LIBS"] = "ON" if self.options.shared else "OFF"

        for group in self.groups:
            self._cmake.definitions["VTK_GROUP_ENABLE_{}".format(group)] = self.options.get_safe("group_{}".format(group.lower()), default="NO")
        for module in self.modules:
            self._cmake.definitions["VTK_MODULE_ENABLE_VTK_{}".format(module)] = self.options.get_safe("module_{}".format(module.lower()), default="NO")

        # Should we add below defines depending on "group_qt"? Or rather that should be driven by package consumer "vtk:module_guisupportqt=True" and "vtk:module_renderingqt=True"?
        self._cmake.definitions["VTK_MODULE_ENABLE_VTK_GUISupportQt"] = "YES" if self.options.group_qt else "NO"
        self._cmake.definitions["VTK_MODULE_ENABLE_VTK_RenderingQt"] = "YES" if self.options.group_qt else "NO"
        # Looks like "VTK_MODULE_ENABLE_VTK_GUISupportQtOpenGL" doesn't exist in VTK 9.0.1
        # self._cmake.definitions["VTK_MODULE_ENABLE_VTK_GUISupportQtOpenGL"] = "YES" if self.options.group_qt else "NO"

        # Introducing groups and modules
        # self._cmake.definitions["VTK_Group_StandAlone"] = "OFF" if self.options.minimal else "ON"
        # self._cmake.definitions["VTK_Group_Rendering"] = "OFF" if self.options.minimal else "ON"
        #
        # self._cmake.definitions["Module_vtkIOXML"] = "ON" if self.options.ioxml else "OFF"
        #
        # self._cmake.definitions["Module_vtkIOExport"] = "ON" if self.options.ioexport else "OFF"
        #
        # self._cmake.definitions["VTK_Group_Qt"] = "ON" if self.options.with_qt else "OFF"
        # self._cmake.definitions["VTK_MODULE_ENABLE_VTK_GUISupportQt"] = "YES" if self.options.with_qt else "NO"
        # self._cmake.definitions["VTK_MODULE_ENABLE_VTK_GUISupportQtOpenGL"] = "YES" if self.options.with_qt else "NO"
        # self._cmake.definitions["VTK_MODULE_ENABLE_VTK_RenderingQt"] = "YES" if self.options.with_qt else "NO"
        #
        # self._cmake.definitions["VTK_Group_MPI"] = "ON" if self.options.mpi else "OFF"
        # self._cmake.definitions["Module_vtkIOParallelXML"] = "ON" if self.options.mpi else "OFF"
        #
        # self._cmake.definitions["Module_vtkIOParallelXML"] = "ON" if self.options.mpi_minimal else "OFF"
        # self._cmake.definitions["Module_vtkParallelMPI"] = "ON" if self.options.mpi_minimal else "OFF"

        # if self.settings.os == 'Macos':
        #     self.env['DYLD_LIBRARY_PATH'] = os.path.join(self.build_folder, 'lib')
        #     self.output.info("cmake build: %s" % self.build_folder)

        self._cmake.configure(build_folder='build')
        return self._cmake

    def build(self):
        # if self.options.with_qt:
        if self.options.group_qt:
            if self.options["qt"].shared == False:
                raise ConanInvalidConfiguration("VTK option 'group_qt' requires 'qt:shared=True'")
            if self.settings.os == "Linux":
                if self.options["qt"].qtx11extras == False:
                    raise ConanInvalidConfiguration("VTK option 'group_qt' requires 'qt:qtx11extras=True'")
                
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

        # "$\package\lib\vtk" contains "hierarchy\conanvtk\" and a lot of *.txt files in it. I believe they are not needed. Remove them.
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'vtk'))
        # "$\package\lib\cmake" contains a lot of *.cmake files. conan-center HOOK disallow *.cmake files in package. Remove them.
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'cmake'))
        # Licenses are created in "$\package\share\licenses\conanvtk\" while their must be in "$\package\licenses\". Move them from former to latter.
        os.rename(os.path.join(self.package_folder, 'share', 'licenses', 'conanvtk'), os.path.join(self.package_folder, 'licenses'))
        tools.rmdir(os.path.join(self.package_folder, 'share'))

    # GCC static linking require providing libraries in appropriate order.
    # Below "order" is not necessary is correct (couldn't find the correct one), but it is used as good starting point.
    def _sort_libs(self, libs):
        if self.settings.compiler != "gcc":
            return libs
        libs_ordered = []
        print('VTK libs before sort: ' + (';'.join(libs)))
        order = ['vtkViewsCore', 'vtkViewsContext2D', 'vtkRenderingVolumeOpenGL2', 'vtkRenderingContextOpenGL2', 'vtkRenderingContext2D', 'vtkRenderingVolume', 'vtkfreetype', 'vtkRenderingFreeType', 'vtkRenderingAnnotation', 'vtkInteractionWidgets', 'vtkInteractionStyle', 'vtkImagingMath', 'vtkImagingHybrid', 'vtkImagingGeneral', 'vtkImagingColor', 'vtkexpat', 'vtkIOXMLParser', 'vtkIOXML', 'vtkIOLegacy', 'vtkIOGeometry', 'vtkgl2ps', 'vtkglew', 'vtkRenderingOpenGL2', 'vtkRenderingGL2PSOpenGL2', 'vtktiff', 'vtkpng', 'vtkjpeg', 'vtkmetaio', 'vtkIOImage', 'vtkIOExport', 'vtkzlib', 'vtkIOCore', 'vtkFiltersModeling', 'vtkFiltersSources', 'vtkRenderingCore', 'vtkImagingSources', 'vtkFiltersHybrid', 'vtkFiltersGeometry', 'vtkalglib', 'vtkImagingCore', 'vtkImagingFourier', 'vtkFiltersStatistics', 'vtkFiltersGeneral', 'vtkFiltersExtraction', 'vtkFiltersCore', 'vtkDICOMParser', 'vtkCommonExecutionModel', 'vtkCommonComputationalGeometry', 'vtkCommonDataModel', 'vtkCommonSystem', 'vtkCommonTransforms', 'vtkCommonMath', 'vtkCommonMisc', 'vtkCommonCore', 'vtkCommonColor', 'vtksys']
        for item in order:
            for idx in range(len(libs)): 
                if item.lower() in libs[idx].lower():
                    value = libs.pop(idx)
                    libs_ordered.append(value)
                    break
        libs_ordered = libs + libs_ordered # add unordered elements, if any
        print('VTK libs ordered: ' + (';'.join(libs_ordered)))
        return libs_ordered

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "VTK"
        self.cpp_info.names["cmake_find_package_multi"] = "VTK"
        libs = tools.collect_libs(self)
        self.cpp_info.libs = self._sort_libs(libs)

        # Adding system libs without 'lib' prefix and '.so' or '.so.X' suffix.
        if self.settings.os == 'Linux':
            self.cpp_info.system_libs.append('pthread')
            self.cpp_info.system_libs.append('dl')            # 'libvtksys-7.1.a' require 'dlclose', 'dlopen', 'dlsym' and 'dlerror' which on CentOS are in 'dl' library
            
        # if not self.options.shared and self.options.with_qt:
        if not self.options.shared and self.options.group_qt:
            if self.settings.os == 'Windows':
                self.cpp_info.system_libs.append('Ws2_32')    # 'vtksys-9.0d.lib' require 'gethostbyname', 'gethostname', 'WSAStartup' and 'WSACleanup' which are in 'Ws2_32.lib' library
                self.cpp_info.system_libs.append('Psapi')     # 'vtksys-9.0d.lib' require 'GetProcessMemoryInfo' which is in 'Psapi.lib' library
                self.cpp_info.system_libs.append('dbghelp')   # 'vtksys-9.0d.lib' require '__imp_SymGetLineFromAddr64', '__imp_SymInitialize' and '__imp_SymFromAddr' which are in 'dbghelp.lib' library

            if self.settings.os == 'Macos':
                self.cpp_info.frameworks.extend(["CoreFoundation"]) # 'libvtkRenderingOpenGL2-9.0.a' require '_CFRelease', '_CFRetain', '_objc_msgSend' and much more which are in 'CoreFoundation' library
                self.cpp_info.frameworks.extend(["Cocoa"])          # 'libvtkRenderingOpenGL2-9.0.a' require '_CGWarpMouseCursorPosition' and more, 'libvtkRenderingUI-9.0.a' require '_OBJC_CLASS_$_NSApplication' and more, which are in 'Cocoa' library

        version_split = self.version.split('.')
        short_version = "{}.{}".format(version_split[0], version_split[1])
        # Why "vtknetcdf" and "vtknetcdfcpp" are treated exceptionally from all other modules?
        # There are a lot of other *.h in subfolders, should they be directly exposed too
        # or maybe those two should be removed from below?
        self.cpp_info.includedirs.extend([
            os.path.join("include", "vtk-{}").format(short_version),
            os.path.join("include", "vtk-{}", "vtknetcdf", "include").format(short_version),
            os.path.join("include", "vtk-{}", "vtknetcdfcpp").format(short_version)
        ])
