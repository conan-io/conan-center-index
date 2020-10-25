import os
import re

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class VTKConan(ConanFile):
    name = "vtk"
    # version = "9.0.1"  # DO NOT SUBMIT!!! Remove this line in final version of PR to conan-center-index
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://vtk.org/"
    license = "BSD-3-Clause"
    description = "Visualization Toolkit by Kitware"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    topics = ("conan", "VTK", "3D rendering", "2D plotting", "3D interaction", "3D manipulation", 
                "graphics", "image processing", "scientific visualization", "geometry modeling")
    _groups = ["StandAlone", "Rendering", "MPI", "Qt", "Imaging", "Views", "Web"]
    # _modules are taken from CMake GUI
    _modules = [
        "AcceleratorsVTKm"
        "ChartsCore",
        "CommonArchive"
        "CommonColor"
        "CommonComputationalGeometry",
        "CommonCore",
        "CommonDataModel",
        "CommonExecutionModel",
        "CommonMath"
        "CommonMisc",
        "CommonSystem",
        "CommonTransforms",
        "DICOMParser",
        "DomainsChemistry",
        "DomainsChemistryOpenGL2",
        "DomainsMicroscopy",
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
        "FiltersModeling",
        "FiltersOpenTURNS",
        "FiltersParallel",
        "FiltersParallelDIY2",
        "FiltersParallelFlowPaths",
        "FiltersParallelGeometry",
        "FiltersParallelImaging",
        "FiltersParallelMPI",
        "FiltersParallelStatistics",
        "FiltersParallelVerdict",
        "FiltersPoints",
        "FiltersProgrammable",
        "FiltersReebGraph",
        "FiltersSMP",
        "FiltersSelection",
        "FiltersSources",
        "FiltersStatistics",
        "FiltersTexture",
        "FiltersTopology",
        "FiltersVerdict",
        "GeovisCore",
        "GeovisGDAL",
        "GUISupportMFC",
        "GUISupportQt",
        "GUISupportQtSQL",
        "ImagingColor",
        "ImagingCore",
        "ImagingFourier",
        "ImagingGeneral",
        "ImagingHybrid",
        "ImagingMath",
        "ImagingMorphological",
        "ImagingOpenGL2",
        "ImagingSources",
        "ImagingStatistics",
        "ImagingStencil",
        "InfovisBoost",
        "InfovisBoostGraphAlgorithms",
        "InfovisCore",
        "InfovisLayout",
        "InteractionImage",
        "InteractionStyle",
        "InteractionWidgets",
        "IOADIOS2",
        "IOAMR",
        "IOAsynchronous",
        "IOCityGML",
        "IOCore",
        "IOEnSight",
        "IOExodus",
        "IOExport",
        "IOExportGL2PS",
        "IOExportPDF",
        "IOFFMPEG",
        "IOGDAL",
        "IOGeoJSON",
        "IOGeometry",
        "IOH5part",
        "IOImage",
        "IOImport",
        "IOInfovis",
        "IOLAS",
        "IOLSDyna",
        "IOLegacy",
        "IOMINC",
        "IOMPIImage",
        "IOMotionFX",
        "IOMovie",
        "IOMySQL",
        "IONetCDF",
        "IOODBC",
        "IOOggTheora",
        "IOPDAL",
        "IOPIO",
        "IOPLY",
        "IOParallel",
        "IOParallelExodus",
        "IOParallelLSDyna",
        "IOParallelNetCDF",
        "IOParallelXML",
        "IOParallelXdmf3",
        "IOPostgreSQL",
        "IOSQL",
        "IOSegY",
        "IOTRUCHAS",
        "IOTecplotTable",
        "IOVPIC",
        "IOVeraOut",
        "IOVideo",
        "IOXML",
        "IOXMLParser",
        "IOXdmf2",
        "IOXdmf3",
        "MomentInvariants",
        "ParallelCore",
        "ParallelDIY",
        "ParallelMPI",
        "PoissonReconstruction",
        "Powercrust",
        "PythonInterpreter",
        "RenderingAnnotation",
        "RenderingContext2D",
        "RenderingContextOpenGL2",
        "RenderingCore",
        "RenderingExternal",
        "RenderingFreeType",
        "RenderingFreeTypeFontConfig",
        "RenderingGL2PSOpenGL2",
        "RenderingImage",
        "RenderingLabel",
        "RenderingLICOpenGL2",
        "RenderingLOD",
        "RenderingMatplotlib",
        "RenderingOpenGL2",
        "RenderingOpenVR",
        "RenderingParallel",
        "RenderingParallelLIC",
        "RenderingQt",
        "RenderingRayTracing",
        "RenderingSceneGraph",
        "RenderingUI",
        "RenderingVolume",
        "RenderingVolumeAMR",
        "RenderingVolumeOpenGL2",
        "RenderingVtkJS",
        "SignedTensor",
        "SplineDrivenImageSlicer",
        "TestingCore",
        "TestingGenericBridge",
        "TestingIOSQL",
        "TestingRendering",
        "UtilitiesBenchmarks",
        "ViewsContext2D",
        "ViewsCore",
        "ViewsInfovis",
        "ViewsQt",
        "WebCore",
        "WebGLExporter",
        "WrappingPythonCore",
        "WrappingTools",

        "diy2",
        "doubleconversion",
        "eigen",
        "exodusII",
        "expat",
        "freetype",
        "gl2ps",
        "glew",
        "h5part",
        "hdf5",
        "jpeg",
        "jsoncpp",
        "kissfft",
        "kwiml",
        "libharu",
        "libproj",
        "libxml2",
        "loguru",
        "lz4",
        "lzma",
        "metaio",
        "netcdf",
        "octree",
        "ogg",
        "opengl",
        "pegtl",
        "png",
        "pugixml",
        "sqlite",
        "theora",
        "tiff",
        "utf8",
        "verdict",
        "vpic",
        "vtkDICOM",
        "vtkm",
        "vtksys",
        "xdmf2",
        "xdmf3",
        "zfp",
        "zlib",
    ]
    options = dict({"shared": [True, False], "fPIC": [True, False],
    }, **{"group_{}".format(group.lower()): [True, False] for group in _groups},
    **{"module_{}".format(module.lower()): [True, False] for module in _modules}
    )
    # default_options are set to the same values as clean VTK 9.0.1 cmake installation has, except "shared" which Conan require to be "False" by default.
    default_options = dict({
        "shared": False,
        "fPIC": False,
        }, **{"group_{}".format(group.lower()): True for group in _groups if (group in ["StandAlone", "Rendering"])},
        **{"group_{}".format(group.lower()): False for group in _groups if (group not in ["StandAlone", "Rendering"])},
        **{"module_{}".format(module.lower()): False for module in _modules})
    short_paths = True
    _source_subfolder = "source_subfolder"
    _cmake = None


    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name.upper() + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)        

    def requirements(self):
        if self.options.group_rendering:
            self.requires("opengl/system")
        if self.options.module_ioxdmf3:
            self.requires("boost/1.74.0")
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

        # VTK available options for cmake defines are `YES`, `WANT`, `DONT_WANT`, `NO`, or `DEFAULT`. Other values results as cmake configure step failure.
        for group in self._groups:
            self._cmake.definitions["VTK_GROUP_ENABLE_{}".format(group)] = "WANT" if self.options.get_safe("group_{}".format(group.lower()), default=False) else "DEFAULT"
        for module in self._modules:
            # Defines shouldn't be left uninitalized, however VTK has so many _modules, that 
            # it ends up as "The command line is too long." error on Windows.
            if self.options.get_safe("module_{}".format(module.lower()), default=False):
                self._cmake.definitions["VTK_MODULE_ENABLE_VTK_{}".format(module)] = "WANT" if self.options.get_safe("module_{}".format(module.lower()), default=False) else "DEFAULT"

        self._cmake.configure(build_folder='build')
        return self._cmake

    def build(self):
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
    # Below "order" is not necessary correct (couldn't find the correct one), but after few trials, it worked for one configuration.
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
        # Why "vtknetcdf" and "vtknetcdfcpp" are treated exceptionally from all other _modules?
        # There are a lot of other *.h in subfolders, should they be directly exposed too
        # or maybe those two should be removed from below?
        self.cpp_info.includedirs.extend([
            os.path.join("include", "vtk-{}").format(short_version),
            os.path.join("include", "vtk-{}", "vtknetcdf", "include").format(short_version),
            os.path.join("include", "vtk-{}", "vtknetcdfcpp").format(short_version)
        ])
