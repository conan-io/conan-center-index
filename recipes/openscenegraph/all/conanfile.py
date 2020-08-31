from conans import CMake, ConanFile, tools
import glob, os


class ConanFile(ConanFile):
    name = "openscenegraph"
    description = "OpenSceneGraph is an open source high performance 3D graphics toolkit"
    topics = "conan", "openscenegraph", "graphics"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.openscenegraph.org"
    license = "LGPL-2.1-only", "WxWindows-exception-3.1"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_applications": [True, False],
        "build_examples": [True, False],
        "enable_notify": [True, False],
        "enable_deprecated_api": [True, False],
        "enable_readfile": [True, False],
        "enable_ref_ptr_implicit_output_conversion": [True, False],
        "enable_ref_ptr_safe_dereference": [True, False],
        "enable_envvar_support": [True, False],
        "enable_windowing_system": [True, False],
        "enable_deprecated_serializers": [True, False],
        "use_fontconfig": [True, False],
        # "with_asio": [True, False], # osg seems to not work with recent versions of asio
        # "with_collada": [True, False],
        "with_curl": [True, False],
        "with_dcmtk": [True, False],
        "with_freetype": [True, False],
        "with_gdal": [True, False],
        "with_gif": [True, False],
        # "with_gstreamer": [True, False],
        "with_gta": [True, False],
        "with_jasper": [True, False],
        "with_jpeg": [True, False],
        "with_openexr": [True, False],
        "with_png": [True, False],
        "with_tiff": [True, False],
        "with_zlib": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_applications": False,
        "build_examples": False,
        "enable_notify": True,
        "enable_deprecated_api": False,
        "enable_readfile": True,
        "enable_ref_ptr_implicit_output_conversion": True,
        "enable_ref_ptr_safe_dereference": True,
        "enable_envvar_support": True,
        "enable_windowing_system": True,
        "enable_deprecated_serializers": False,
        "use_fontconfig": True,
        # "with_asio": False,
        # "with_collada": False,
        "with_curl": False,
        "with_dcmtk": False,
        "with_freetype": True,
        "with_gdal": False,
        "with_gif": True,
        # "with_gstreamer": False,
        "with_gta": False,
        "with_jasper": False,
        "with_jpeg": True,
        "with_openexr": False,
        "with_png": True,
        "with_tiff": True,
        "with_zlib": True,
    }

    short_paths = True
    no_copy_source = True
    exports_sources = "CMakeLists.txt",
    generators = "cmake", "cmake_find_package_multi"

    _source_subfolder = "source_subfolder"

    @property
    def _apple(self):
        return self.settings.os.value in ("Macos", "iOS", "watchOS", "tvOS")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            # del self.options.with_asio

            # Default to false with fontconfig until it is supported on Windows
            self.options.use_fontconfig = False

        if self._apple:
            # osg uses native apis on Apple platforms
            del self.options.with_gif
            del self.options.with_jpeg
            del self.options.with_png

    def configure(self):
        if self.options.with_openexr:
            self.options.with_zlib = True

        if self.options.get_safe("with_png"):
            self.options.with_zlib = True

        if self.options.with_dcmtk:
            self.options.with_zlib = True
            # These are due to limitations in osg's plugin configuration, which can only be
            # controlled via completely disabling cmake's find package mechanism per package
            if not self.options.with_png:
                self.options["dcmtk"].with_libpng = False
            if not self.options.with_tiff:
                self.options["dcmtk"].with_libtiff = False

        if self.options.shared and self.settings.compiler == "Visual Studio":
            # osg expects its dependencies to be shared libraries if it is being built as one
            # this only really matters with msvc due to dllimport/export

            # This could probably be fixed with minimal patching and the cmake_find_package
            # generator, however that is currently horribly broken due to #2311
            self.options["*"].shared = True

    def requirements(self):
        if self.options.enable_windowing_system and self.settings.os == "Linux":
            self.requires("xorg/system")
        self.requires("opengl/system")

        if self.options.use_fontconfig:
            self.requires("fontconfig/2.13.91")

        # if self.options.get_safe("with_asio"):
        # Should these be private requires?
        #     self.requires("asio/1.17.0")
        #     self.requires("boost/1.74.0")
        # if self.options.with_collada:
        #     self.requires("libxml2/2.9.10")
        if self.options.with_curl:
            self.requires("libcurl/7.71.1")
        if self.options.with_dcmtk:
            self.requires("dcmtk/3.6.5")
        if self.options.with_freetype:
            self.requires("freetype/2.10.2")
        if self.options.with_gdal:
            self.requires("gdal/3.1.0")
        if self.options.get_safe("with_gif"):
            self.requires("giflib/5.2.1")
        # if self.options.with_gstreamer:
        #     self.requires("glib/2.65.1")
        if self.options.with_gta:
            self.requires("libgta/1.2.1")
        if self.options.with_jasper:
            self.requires("jasper/2.0.16")
        if self.options.get_safe("with_jpeg"):
            self.requires("libjpeg/9d")
        if self.options.with_openexr:
            self.requires("openexr/2.5.2")
        if self.options.get_safe("with_png"):
            self.requires("libpng/1.6.37")
        if self.options.with_tiff:
            self.requires("libtiff/4.1.0")
        if self.options.with_zlib:
            self.requires("zlib/1.2.11")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("OpenSceneGraph-OpenSceneGraph-" + self.version, self._source_subfolder)

    def build(self):
        cmake = CMake(self)

        cmake.definitions["DYNAMIC_OPENSCENEGRAPH"] = self.options.shared
        cmake.definitions["DYNAMIC_OPENTHREADS"] = self.options.shared

        cmake.definitions["BUILD_OSG_APPLICATIONS"] = self.options.build_applications
        cmake.definitions["BUILD_OSG_EXAMPLES"] = self.options.build_examples

        cmake.definitions["OSG_NOTIFY_DISABLED"] = not self.options.enable_notify
        cmake.definitions["OSG_USE_DEPRECATED_API"] = self.options.enable_deprecated_api
        cmake.definitions["OSG_PROVIDE_READFILE"] = self.options.enable_readfile
        cmake.definitions["OSG_USE_REF_PTR_IMPLICIT_OUTPUT_CONVERSION"] = self.options.enable_ref_ptr_implicit_output_conversion
        cmake.definitions["OSG_USE_REF_PTR_SAFE_DEREFERENCE"] = self.options.enable_ref_ptr_safe_dereference
        cmake.definitions["OSG_ENVVAR_SUPPORTED"] = self.options.enable_envvar_support

        if not self.options.enable_windowing_system:
            cmake.definitions["OSG_WINDOWING_SYSTEM"] = None

        cmake.definitions["BUILD_OSG_DEPRECATED_SERIALIZERS"] = self.options.enable_deprecated_serializers

        cmake.definitions["OSG_TEXT_USE_FONTCONFIG"] = self.options.use_fontconfig

        # Disable option dependencies unless we have a package for them
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Freetype"] = not self.options.with_freetype
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_ilmbase"] = not self.options.with_openexr
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Inventor"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Jasper"] = not self.options.with_jasper
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_OpenEXR"] = not self.options.with_openexr
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_OpenCascade"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_COLLADA"] = True  # not self.options.with_collada
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_FBX"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_ZLIB"] = not self.options.with_zlib
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_GDAL"] = not self.options.with_gdal
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_GTA"] = not self.options.with_gta
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_CURL"] = not self.options.with_curl
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_LibVNCServer"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_DCMTK"] = not self.options.with_dcmtk
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_FFmpeg"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_GStreamer"] = True  # not self.options.with_gstreamer
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_GLIB"] = True  # not self.options.with_gstreamer
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_DirectShow"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_SDL2"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_SDL"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Poppler-glib"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_RSVG"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_GtkGl"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_DirectInput"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_NVTT"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_Asio"] = True  # not self.options.get_safe("with_asio")
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_ZeroConf"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_LIBLAS"] = True
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_GIFLIB"] = not self.options.get_safe("with_gif")
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_JPEG"] = not self.options.get_safe("with_jpeg")
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_PNG"] = not self.options.get_safe("with_png")
        cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_TIFF"] = not self.options.with_tiff

        if self.settings.os == "Windows":
            # osg has optional quicktime support on Windows
            cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_QuickTime"] = True

        cmake.definitions["OSG_MSVC_VERSIONED_DLL"] = False

        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FindOpenSceneGraph is shipped with cmake and is a traditional cmake script
        # It doesn't setup targets and only provides a few variables:
        #  - OPENSCENEGRAPH_FOUND
        #  - OPENSCENEGRAPH_VERSION
        #  - OPENSCENEGRAPH_INCLUDE_DIRS
        #  - OPENSCENEGRAPH_LIBRARIES
        # Unfortunately, the cmake_find_package generators don't currently allow directly setting variables,
        # but it will set the last three of these if the name of the package is OPENSCENEGRAPH (it uses
        # the filename for the first, so OpenSceneGraph_FOUND gets set, not OPENSCENEGRAPH_FOUND)
        self.cpp_info.filenames["cmake_find_package"] = "OpenSceneGraph"
        self.cpp_info.filenames["cmake_find_package_multi"] = "OpenSceneGraph"
        self.cpp_info.names["cmake_find_package"] = "OPENSCENEGRAPH"
        self.cpp_info.names["cmake_find_package_multi"] = "OPENSCENEGRAPH"

        if self.settings.build_type == "Debug":
            postfix = "d"
        elif self.settings.build_type == "RelWithDebInfo":
            postfix = "rd"
        elif self.settings.build_type == "MinSizeRel":
            postfix = "s"
        else:
            postfix = ""

        def setup_plugin(plugin):
            lib = "osgdb_" + plugin
            self.cpp_info.components[lib].libs = [] if self.options.shared else [lib + postfix]
            self.cpp_info.components[lib].requires = ["OpenThreads", "osg", "osgDB", "osgUtil"]
            if not self.options.shared:
                self.cpp_info.components[lib].libdirs = [os.path.join("lib", "osgPlugins-{}".format(self.version))]
            return lib

        def setup_serializers(lib):
            plugins = []
            if lib not in ("osgDB", "osgWidget", "osgPresentation"):
                plugins.append("serializers_{}".format(lib.lower()))
            if self.options.enable_deprecated_serializers:
                if lib not in ("osgUtil", "osgDB", "osgGA", "osgManipulator", "osgUI", "osgPresentation"):
                    plugins.append("deprecated_{}".format(lib.lower()))
            for plugin in plugins:
                plugin_lib = setup_plugin(plugin)
                self.cpp_info.components[plugin_lib].requires.append(lib)

        def setup_library(lib):
            self.cpp_info.components[lib].libs = [lib + postfix]
            self.cpp_info.components[lib].names["cmake_find_package"] = lib
            self.cpp_info.components[lib].filenames["cmake_find_package"] = lib
            setup_serializers(lib)

        # Core libraries
        # requires obtained from osg's source code
        self.cpp_info.components["OpenThreads"].libs = ["OpenThreads" + postfix]
        self.cpp_info.components["OpenThreads"].names["cmake_find_package"] = "OpenThreads"
        self.cpp_info.components["OpenThreads"].names["pkg_config"] = "openthreads"
        if self.settings.os == "Linux":
            self.cpp_info.components["OpenThreads"].system_libs = ["pthread"]

        setup_library("osg")
        self.cpp_info.components["osg"].requires = ["OpenThreads", "opengl::opengl"]
        if self.settings.os == "Linux":
            self.cpp_info.components["osg"].system_libs = ["m", "rt", "dl"]
        if not self.options.shared:
            self.cpp_info.components["osg"].defines.append("OSG_LIBRARY_STATIC")

        setup_library("osgDB")
        self.cpp_info.components["osgDB"].requires = ["osg", "osgUtil", "OpenThreads"]
        if self.settings.os == "Linux":
            self.cpp_info.components["osgDB"].system_libs = ["dl"]
        elif self._apple:
            self.cpp_info.components["osgDB"].system_libs = ["Cocoa"]
        if self.options.with_zlib:
            self.cpp_info.components["osgDB"].requires.append("zlib::zlib")

        setup_library("osgUtil")
        self.cpp_info.components["osgUtil"].requires = ["osg", "OpenThreads"]

        setup_library("osgGA")
        self.cpp_info.components["osgGA"].requires = ["osgDB", "osgUtil", "osg", "OpenThreads"]

        setup_library("osgText")
        self.cpp_info.components["osgText"].requires = ["osgDB", "osg", "osgUtil", "OpenThreads"]
        if self.options.use_fontconfig:
            self.cpp_info.components["osgText"].requires.append("fontconfig::fontconfig")

        setup_library("osgViewer")
        self.cpp_info.components["osgViewer"].requires = ["osgGA", "osgText", "osgDB", "osgUtil", "osg"]
        if self.options.enable_windowing_system:
            if self.settings.os == "Linux":
                self.cpp_info.components["osgViewer"].requires.append("xorg::xorg")
            elif self._apple:
                self.cpp_info.components["osgViewer"].system_libraries = ["Cocoa"]
        if self.settings.os == "Windows":
            self.cpp_info.components["osgViewer"].system_libraries = ["gdi32"]

        setup_library("osgAnimation")
        self.cpp_info.components["osgAnimation"].requires = ["osg", "osgText", "osgGA", "osgViewer", "OpenThreads"]

        setup_library("osgFX")
        self.cpp_info.components["osgFX"].requires = ["osgUtil", "osgDB", "osg", "OpenThreads"]

        setup_library("osgManipulator")
        self.cpp_info.components["osgManipulator"].requires = ["osgViewer", "osgGA", "osgUtil", "osg", "OpenThreads"]

        setup_library("osgParticle")
        self.cpp_info.components["osgParticle"].requires = ["osgUtil", "osgDB", "osg", "OpenThreads"]

        setup_library("osgUI")
        self.cpp_info.components["osgUI"].requires = ["osgDB", "osgGA", "osgUtil", "osgText", "osgViewer", "osg", "OpenThreads"]

        setup_library("osgVolume")
        self.cpp_info.components["osgVolume"].requires = ["osgGA", "osgDB", "osgUtil", "osg", "OpenThreads"]

        setup_library("osgShadow")
        self.cpp_info.components["osgShadow"].requires = ["osgUtil", "osgDB", "osg", "OpenThreads"]

        setup_library("osgSim")
        self.cpp_info.components["osgSim"].requires = ["osgText", "osgUtil", "osgDB", "osg", "OpenThreads"]

        setup_library("osgTerrain")
        self.cpp_info.components["osgTerrain"].requires = ["osgUtil", "osgDB", "osg", "OpenThreads"]

        setup_library("osgWidget")
        self.cpp_info.components["osgWidget"].requires = ["osgText", "osgViewer", "osgDB", "osg", "OpenThreads"]

        setup_library("osgPresentation")
        self.cpp_info.components["osgPresentation"].requires = ["osgViewer", "osgUI", "osgWidget", "osgManipulator", "osgVolume", "osgFX", "osgText", "osgGA", "osgUtil", "osgDB", "osg", "OpenThreads"]

        # NodeKit/Psudo loader plugins
        setup_plugin("osga")
        setup_plugin("rot")
        setup_plugin("scale")
        setup_plugin("trans")
        setup_plugin("normals")
        setup_plugin("revisions")

        plugin = setup_plugin("osgviewer")
        self.cpp_info.components[plugin].requires.append("osgViewer")

        plugin = setup_plugin("osgshadow")
        self.cpp_info.components[plugin].requires.append("osgShadow")

        plugin = setup_plugin("osgterrain")
        self.cpp_info.components[plugin].requires.append("osgTerrain")

        # Main native plugins
        setup_plugin("osg")

        plugin = setup_plugin("ive")
        self.cpp_info.components[plugin].requires.extend(("osgSim", "osgFX", "osgText", "osgTerrain", "osgVolume"))
        if self.options.with_zlib:
            self.cpp_info.components[plugin].requires.append("zlib::zlib")

        # Viewer plugins
        plugin = setup_plugin("cfg")
        self.cpp_info.components[plugin].requires.append("osgViewer")

        # Shader plugins
        setup_plugin("glsl")

        # Image plugins
        setup_plugin("rgb")
        setup_plugin("bmp")
        setup_plugin("pnm")
        setup_plugin("dds")
        setup_plugin("tga")
        setup_plugin("hdr")
        setup_plugin("dot")
        setup_plugin("vtf")
        setup_plugin("ktx")

        if self.options.get_safe("with_jpeg"):
            plugin = setup_plugin("jpeg")
            self.cpp_info.components[plugin].requires.append("libjpeg::libjpeg")

        if self.options.with_jasper:
            plugin = setup_plugin("jp2")
            self.cpp_info.components[plugin].requires.append("jasper::jasper")

        if self.options.with_openexr:
            plugin = setup_plugin("exr")
            self.cpp_info.components[plugin].requires.append("openexr::openexr")

        if self.options.get_safe("with_gif"):
            plugin = setup_plugin("gif")
            self.cpp_info.components[plugin].requires.append("giflib::giflib")

        if self.options.get_safe("with_png"):
            plugin = setup_plugin("png")
            self.cpp_info.components[plugin].requires.extend(("libpng::libpng", "zlib::zlib"))

        if self.options.with_tiff:
            plugin = setup_plugin("tiff")
            self.cpp_info.components[plugin].requires.append("libtiff::libtiff")

        if self.options.with_gdal:
            plugin = setup_plugin("gdal")
            self.cpp_info.components[plugin].requires.extend(("osgTerrain", "gdal::gdal"))
            plugin = setup_plugin("ogr")
            self.cpp_info.components[plugin].requires.append("gdal::gdal")

        if self.options.with_gta:
            plugin = setup_plugin("gta")
            self.cpp_info.components[plugin].requires.append("libgta::libgta")

        # 3D Image plugins
        if self.options.with_dcmtk:
            plugin = setup_plugin("dicom")
            self.cpp_info.components[plugin].requires.extend(("osgVolume", "dcmtk::dcmtk"))
            if self.settings.os == "Windows":
                self.cpp_info.components[plugin].system_libs = ["wsock32", "ws2_32"]

        # 3rd party 3d plugins
        setup_plugin("3dc")

        plugin = setup_plugin("p3d")
        self.cpp_info.components[plugin].requires.extend(("osgGA", "osgText", "osgVolume", "osgFX", "osgViewer", "osgPresentation"))

        if self.options.with_curl:
            plugin = setup_plugin("curl")
            self.cpp_info.components[plugin].requires.append("libcurl::libcurl")
            if self.options.with_zlib:
                self.cpp_info.components[plugin].requires.append("zlib::zlib")

        if self.options.with_zlib:
            plugin = setup_plugin("gz")
            self.cpp_info.components[plugin].requires.append("zlib::zlib")

        # with_inventor
        # setup_plugin("iv")

        # with_collada
        # setup_plugin("dae")

        # with_fbx
        # setup_plugin("fbx")

        # with_opencascade
        # setup_plugin("opencascade")

        plugin = setup_plugin("bvh")
        self.cpp_info.components[plugin].requires.append("osgAnimation")

        setup_plugin("x")

        plugin = setup_plugin("dxf")
        self.cpp_info.components[plugin].requires.append("osgText")

        plugin = setup_plugin("openflight")
        self.cpp_info.components[plugin].requires.append("osgSim")

        setup_plugin("obj")
        setup_plugin("pic")
        setup_plugin("stl")
        setup_plugin("3ds")
        setup_plugin("ac")
        setup_plugin("pov")
        setup_plugin("logo")
        setup_plugin("lws")
        setup_plugin("md2")
        setup_plugin("osgtgz")
        setup_plugin("tgz")

        plugin = setup_plugin("shp")
        self.cpp_info.components[plugin].requires.extend(("osgSim", "osgTerrain"))

        plugin = setup_plugin("txf")
        self.cpp_info.components[plugin].requires.append("osgText")

        setup_plugin("bsp")
        setup_plugin("mdl")

        plugin = setup_plugin("gles")
        self.cpp_info.components[plugin].requires.extend(("osgUtil", "osgAnimation"))

        plugin = setup_plugin("osgjs")
        self.cpp_info.components[plugin].requires.extend(("osgAnimation", "osgSim"))

        plugin = setup_plugin("lwo")
        self.cpp_info.components[plugin].requires.append("osgFX")

        setup_plugin("ply")

        plugin = setup_plugin("txp")
        self.cpp_info.components[plugin].requires.extend(("osgSim", "osgText"))

        # with_ffmpeg
        # setup_plugin("ffmpeg")

        # with_gstreamer
        # setup_plugin("gstreamer")

        # with_directshow
        # setup_plugin("directshow")

        if self._apple:
            setup_plugin("imageio")

        if self._apple:
            plugin = setup_plugin("avfoundation")
            self.cpp_info.components[plugin].requires.append("osgViewer")
            self.cpp_info.components[plugin].system_libs = ["AVFoundation", "Cocoa", "CoreVideo", "CoreMedia", "QuartzCore"]

        if self._apple:
            plugin = setup_plugin("qt")
            self.cpp_info.components[plugin].system_libs = ["QuickTime"]

        if self._apple:
            plugin = setup_plugin("QTKit")
            self.cpp_info.components[plugin].requires.append("osgViewer")
            self.cpp_info.components[plugin].system_libs = ["QTKit", "Cocoa", "QuickTime", "CoreVideo"]

        # with_nvtt
        # setup_plugin("nvtt")

        if self.options.with_freetype:
            plugin = setup_plugin("freetype")
            self.cpp_info.components[plugin].requires.extend(("osgText", "freetype::freetype"))

        if self.options.with_zlib:
            setup_plugin("zip")

        # with_svg
        # setup_plugin("svg")

        # with_pdf/poppler
        # setup_plugin("pdf")

        # with_vnc
        # setup_plugin("vnc")

        setup_plugin("pvr")

        plugin = setup_plugin("osc")
        self.cpp_info.components[plugin].requires.append("osgGA")
        if self.settings.os == "Windows":
            self.cpp_info.components[plugin].system_libs = ["ws2_32", "winmm"]

        setup_plugin("trk")
        setup_plugin("tf")

        # with_blas
        # setup_plugin("las")

        setup_plugin("lua")

        # with_sdl
        # setup_plugin("sdl")

        # if self.options.get_safe("with_asio"):
        #     plugin = setup_plugin("resthttp")
        #     self.cpp_info.components[plugin].requires.extend(("osgPresentation", "asio::asio", "boost::boost"))

        # with_zeroconf
        # setup_plugin("zeroconf")
