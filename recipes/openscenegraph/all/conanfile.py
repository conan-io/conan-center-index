from from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import functools

required_conan_version = ">=1.29.1"


class OpenSceneGraphConanFile(ConanFile):
    name = "openscenegraph"
    description = "OpenSceneGraph is an open source high performance 3D graphics toolkit"
    topics = ("openscenegraph", "graphics")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.openscenegraph.org"
    license = "LGPL-2.1-only", "WxWindows-exception-3.1"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_applications": [True, False],
        "enable_notify": [True, False],
        "enable_deprecated_api": [True, False],
        "enable_readfile": [True, False],
        "enable_ref_ptr_implicit_output_conversion": [True, False],
        "enable_ref_ptr_safe_dereference": [True, False],
        "enable_envvar_support": [True, False],
        "enable_windowing_system": [True, False],
        "enable_deprecated_serializers": [True, False],
        "use_fontconfig": [True, False],
        "with_asio": [True, False],
        "with_curl": [True, False],
        "with_dcmtk": [True, False],
        "with_freetype": [True, False],
        "with_gdal": [True, False],
        "with_gif": [True, False],
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
        "enable_notify": True,
        "enable_deprecated_api": False,
        "enable_readfile": True,
        "enable_ref_ptr_implicit_output_conversion": True,
        "enable_ref_ptr_safe_dereference": True,
        "enable_envvar_support": True,
        "enable_windowing_system": True,
        "enable_deprecated_serializers": False,
        "use_fontconfig": True,
        "with_asio": False,
        "with_curl": False,
        "with_dcmtk": False,
        "with_freetype": True,
        "with_gdal": False,
        "with_gif": True,
        "with_gta": False,
        "with_jasper": False,
        "with_jpeg": True,
        "with_openexr": False,
        "with_png": True,
        "with_tiff": True,
        "with_zlib": True,
    }

    short_paths = True
    exports_sources = "CMakeLists.txt", "patches/*.patch"
    generators = "cmake", "cmake_find_package"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            del self.options.with_asio

            # Default to false with fontconfig until it is supported on Windows
            self.options.use_fontconfig = False

        if tools.apple.is_apple_os(self, self.settings.os):
            # osg uses imageio on Apple platforms
            del self.options.with_gif
            del self.options.with_jpeg
            del self.options.with_png

            # imageio supports tiff files so the tiff plugin isn't needed on Apple platforms
            self.options.with_tiff = False

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if not self.options.with_zlib:
            # These require zlib support
            del self.options.with_openexr
            del self.options.with_png
            del self.options.with_dcmtk

    def validate(self):
        if self.options.get_safe("with_asio", False):
            raise ConanInvalidConfiguration("ASIO support in OSG is broken, see https://github.com/openscenegraph/OpenSceneGraph/issues/921")
        if hasattr(self, "settings_build") and tools.build.cross_building(self, self):
            raise ConanInvalidConfiguration("openscenegraph recipe cannot be cross-built yet. Contributions are welcome.")

    def requirements(self):
        if self.options.enable_windowing_system and self.settings.os == "Linux":
            self.requires("xorg/system")
        self.requires("opengl/system")

        if self.options.use_fontconfig:
            self.requires("fontconfig/2.13.93")

        if self.options.get_safe("with_asio", False):
            # Should these be private requires?
            self.requires("asio/1.22.1")
            self.requires("boost/1.79.0")
        if self.options.with_curl:
            self.requires("libcurl/7.83.1")
        if self.options.get_safe("with_dcmtk"):
            self.requires("dcmtk/3.6.6")
        if self.options.with_freetype:
            self.requires("freetype/2.12.1")
        if self.options.with_gdal:
            self.requires("gdal/3.4.3")
        if self.options.get_safe("with_gif"):
            self.requires("giflib/5.2.1")
        if self.options.with_gta:
            self.requires("libgta/1.2.1")
        if self.options.with_jasper:
            self.requires("jasper/2.0.33")
        if self.options.get_safe("with_jpeg"):
            self.requires("libjpeg/9d")
        if self.options.get_safe("with_openexr"):
            self.requires("openexr/3.1.5")
        if self.options.get_safe("with_png"):
            self.requires("libpng/1.6.37")
        if self.options.with_tiff:
            self.requires("libtiff/4.3.0")
        if self.options.with_zlib:
            self.requires("zlib/1.2.12")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  strip_root=True, destination=self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"].get(self.version, []):
            tools.files.patch(self, **patch)

        for package in ("Fontconfig", "Freetype", "GDAL", "GIFLIB", "GTA", "Jasper", "OpenEXR"):
            # Prefer conan's find package scripts over osg's
            os.unlink(os.path.join(self._source_subfolder, "CMakeModules", "Find{}.cmake".format(package)))

    @functools.lru_cache(1)
    def _configured_cmake(self):
        cmake = CMake(self)

        cmake.definitions["USE_3RDPARTY_BIN"] = False

        cmake.definitions["DYNAMIC_OPENSCENEGRAPH"] = self.options.shared
        cmake.definitions["DYNAMIC_OPENTHREADS"] = self.options.shared

        cmake.definitions["BUILD_OSG_APPLICATIONS"] = self.options.build_applications
        cmake.definitions["BUILD_OSG_EXAMPLES"] = False

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
        cmake.definitions["OSG_WITH_FREETYPE"] = self.options.with_freetype
        cmake.definitions["OSG_WITH_OPENEXR"] = self.options.get_safe("with_openexr", False)
        cmake.definitions["OSG_WITH_INVENTOR"] = False
        cmake.definitions["OSG_WITH_JASPER"] = self.options.with_jasper
        cmake.definitions["OSG_WITH_OPENCASCADE"] = False
        cmake.definitions["OSG_WITH_FBX"] = False
        cmake.definitions["OSG_WITH_ZLIB"] = self.options.with_zlib
        cmake.definitions["OSG_WITH_GDAL"] = self.options.with_gdal
        cmake.definitions["OSG_WITH_GTA"] = self.options.with_gta
        cmake.definitions["OSG_WITH_CURL"] = self.options.with_curl
        cmake.definitions["OSG_WITH_LIBVNCSERVER"] = False
        cmake.definitions["OSG_WITH_DCMTK"] = self.options.get_safe("with_dcmtk", False)
        cmake.definitions["OSG_WITH_FFMPEG"] = False
        cmake.definitions["OSG_WITH_DIRECTSHOW"] = False
        cmake.definitions["OSG_WITH_SDL"] = False
        cmake.definitions["OSG_WITH_POPPLER"] = False
        cmake.definitions["OSG_WITH_RSVG"] = False
        cmake.definitions["OSG_WITH_NVTT"] = False
        cmake.definitions["OSG_WITH_ASIO"] = self.options.get_safe("with_asio", False)
        cmake.definitions["OSG_WITH_ZEROCONF"] = False
        cmake.definitions["OSG_WITH_LIBLAS"] = False
        cmake.definitions["OSG_WITH_GIF"] = self.options.get_safe("with_gif", False)
        cmake.definitions["OSG_WITH_JPEG"] = self.options.get_safe("with_jpeg", False)
        cmake.definitions["OSG_WITH_PNG"] = self.options.get_safe("with_png", False)
        cmake.definitions["OSG_WITH_TIFF"] = self.options.with_tiff

        if self.settings.os == "Windows":
            # osg has optional quicktime support on Windows
            cmake.definitions["CMAKE_DISABLE_FIND_PACKAGE_QuickTime"] = True

        cmake.definitions["OSG_MSVC_VERSIONED_DLL"] = False

        cmake.configure()

        return cmake

    def build(self):
        self._patch_sources()

        self._configured_cmake().build()

    def package(self):
        self._configured_cmake().install()

        self.copy(pattern="LICENSE.txt", dst="licenses", src=self._source_subfolder)

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.files.rm(self, self.package_folder, "*.pdb")

    def package_info(self):
        # FindOpenSceneGraph.cmake is shipped with cmake and is a traditional cmake script
        # It doesn't setup targets and only provides a few variables:
        #  - OPENSCENEGRAPH_FOUND
        #  - OPENSCENEGRAPH_VERSION
        #  - OPENSCENEGRAPH_INCLUDE_DIRS
        #  - OPENSCENEGRAPH_LIBRARIES
        # Unfortunately, the cmake_find_package generators don't currently allow directly setting variables,
        # but it will set the last three of these if the name of the package is OPENSCENEGRAPH (it uses
        # the filename for the first, so OpenSceneGraph_FOUND gets set, not OPENSCENEGRAPH_FOUND)
        # TODO: set OPENSCENEGRAPH_FOUND in cmake_find_package and cmake_find_package_multi
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
            plugin_library = self.cpp_info.components[lib]
            plugin_library.libs = [] if self.options.shared else [lib + postfix]
            plugin_library.requires = ["OpenThreads", "osg", "osgDB", "osgUtil"]
            if not self.options.shared:
                plugin_library.libdirs = [os.path.join("lib", "osgPlugins-{}".format(self.version))]
            return plugin_library

        def setup_serializers(lib):
            plugins = []
            if lib not in ("osgDB", "osgWidget", "osgPresentation"):
                plugins.append("serializers_{}".format(lib.lower()))
            if self.options.enable_deprecated_serializers:
                if lib not in ("osgUtil", "osgDB", "osgGA", "osgManipulator", "osgUI", "osgPresentation"):
                    plugins.append("deprecated_{}".format(lib.lower()))
            for plugin in plugins:
                setup_plugin(plugin).requires.append(lib)

        def setup_library(lib):
            library = self.cpp_info.components[lib]
            library.libs = [lib + postfix]
            library.names["pkg_config"] = "openscenegraph-{}".format(lib)
            setup_serializers(lib)
            return library

        # Core libraries
        # requires obtained from osg's source code

        # TODO: FindOpenThreads.cmake is shipped with CMake, so we should generate separate
        # files for it with cmake_find_package and cmake_find_package_multi
        library = self.cpp_info.components["OpenThreads"]
        library.libs = ["OpenThreads" + postfix]
        library.names["pkg_config"] = "openthreads"
        if self.settings.os == "Linux":
            library.system_libs = ["pthread"]

        library = setup_library("osg")
        library.requires = ["OpenThreads", "opengl::opengl"]
        if self.settings.os == "Linux":
            library.system_libs = ["m", "rt", "dl"]
        if not self.options.shared:
            library.defines.append("OSG_LIBRARY_STATIC")

        library = setup_library("osgDB")
        library.requires = ["osg", "osgUtil", "OpenThreads"]
        if self.settings.os == "Linux":
            library.system_libs = ["dl"]
        elif self.settings.os == "Macos":
            library.frameworks = ["Carbon", "Cocoa"]
        if self.options.with_zlib:
            library.requires.append("zlib::zlib")

        setup_library("osgUtil").requires = ["osg", "OpenThreads"]
        setup_library("osgGA").requires = ["osgDB", "osgUtil", "osg", "OpenThreads"]

        library = setup_library("osgText")
        library.requires = ["osgDB", "osg", "osgUtil", "OpenThreads"]
        if self.options.use_fontconfig:
            library.requires.append("fontconfig::fontconfig")

        library = setup_library("osgViewer")
        library.requires = ["osgGA", "osgText", "osgDB", "osgUtil", "osg"]
        if self.options.enable_windowing_system:
            if self.settings.os == "Linux":
                library.requires.append("xorg::xorg")
            elif tools.apple.is_apple_os(self, self.settings.os):
                library.frameworks = ["Cocoa"]
        if self.settings.os == "Windows":
            library.system_libs = ["gdi32"]

        setup_library("osgAnimation").requires = ["osg", "osgText", "osgGA", "osgViewer", "OpenThreads"]
        setup_library("osgFX").requires = ["osgUtil", "osgDB", "osg", "OpenThreads"]
        setup_library("osgManipulator").requires = ["osgViewer", "osgGA", "osgUtil", "osg", "OpenThreads"]
        setup_library("osgParticle").requires = ["osgUtil", "osgDB", "osg", "OpenThreads"]
        setup_library("osgUI").requires = ["osgDB", "osgGA", "osgUtil", "osgText", "osgViewer", "osg", "OpenThreads"]
        setup_library("osgVolume").requires = ["osgGA", "osgDB", "osgUtil", "osg", "OpenThreads"]
        setup_library("osgShadow").requires = ["osgUtil", "osgDB", "osg", "OpenThreads"]
        setup_library("osgSim").requires = ["osgText", "osgUtil", "osgDB", "osg", "OpenThreads"]
        setup_library("osgTerrain").requires = ["osgUtil", "osgDB", "osg", "OpenThreads"]
        setup_library("osgWidget").requires = ["osgText", "osgViewer", "osgDB", "osg", "OpenThreads"]
        setup_library("osgPresentation").requires = ["osgViewer", "osgUI", "osgWidget", "osgManipulator", "osgVolume", "osgFX", "osgText", "osgGA", "osgUtil", "osgDB", "osg", "OpenThreads"]

        # Start of plugins

        # NodeKit/Psudo loader plugins
        setup_plugin("osga")
        setup_plugin("rot")
        setup_plugin("scale")
        setup_plugin("trans")
        setup_plugin("normals")
        setup_plugin("revisions")
        setup_plugin("osgviewer").requires.append("osgViewer")
        setup_plugin("osgshadow").requires.append("osgShadow")
        setup_plugin("osgterrain").requires.append("osgTerrain")

        # Main native plugins
        setup_plugin("osg")

        plugin = setup_plugin("ive")
        plugin.requires.extend(("osgSim", "osgFX", "osgText", "osgTerrain", "osgVolume"))
        if self.options.with_zlib:
            plugin.requires.append("zlib::zlib")

        # Viewer plugins
        setup_plugin("cfg").requires.append("osgViewer")

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
            setup_plugin("jpeg").requires.append("libjpeg::libjpeg")

        if self.options.with_jasper:
            setup_plugin("jp2").requires.append("jasper::jasper")

        if self.options.get_safe("with_openexr"):
            setup_plugin("exr").requires.append("openexr::openexr")

        if self.options.get_safe("with_gif"):
            setup_plugin("gif").requires.append("giflib::giflib")

        if self.options.get_safe("with_png"):
            setup_plugin("png").requires.extend(("libpng::libpng", "zlib::zlib"))

        if self.options.with_tiff:
            setup_plugin("tiff").requires.append("libtiff::libtiff")

        if self.options.with_gdal:
            setup_plugin("gdal").requires.extend(("osgTerrain", "gdal::gdal"))
            setup_plugin("ogr").requires.append("gdal::gdal")

        if self.options.with_gta:
            setup_plugin("gta").requires.append("libgta::libgta")

        # 3D Image plugins
        if self.options.get_safe("with_dcmtk"):
            plugin = setup_plugin("dicom")
            plugin.requires.extend(("osgVolume", "dcmtk::dcmtk"))
            if self.settings.os == "Windows":
                plugin.system_libs = ["wsock32", "ws2_32"]

        # 3rd party 3d plugins
        setup_plugin("3dc")
        setup_plugin("p3d").requires.extend(("osgGA", "osgText", "osgVolume", "osgFX", "osgViewer", "osgPresentation"))

        if self.options.with_curl:
            plugin = setup_plugin("curl")
            plugin.requires.append("libcurl::libcurl")
            if self.options.with_zlib:
                plugin.requires.append("zlib::zlib")

        if self.options.with_zlib:
            setup_plugin("gz").requires.append("zlib::zlib")

        # with_inventor
        # setup_plugin("iv")

        # with_collada
        # setup_plugin("dae")

        # with_fbx
        # setup_plugin("fbx")

        # with_opencascade
        # setup_plugin("opencascade")

        setup_plugin("bvh").requires.append("osgAnimation")
        setup_plugin("x")
        setup_plugin("dxf").requires.append("osgText")
        setup_plugin("openflight").requires.append("osgSim")
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
        setup_plugin("shp").requires.extend(("osgSim", "osgTerrain"))
        setup_plugin("txf").requires.append("osgText")
        setup_plugin("bsp")
        setup_plugin("mdl")
        setup_plugin("gles").requires.extend(("osgUtil", "osgAnimation"))
        setup_plugin("osgjs").requires.extend(("osgAnimation", "osgSim"))
        setup_plugin("lwo").requires.append("osgFX")
        setup_plugin("ply")
        setup_plugin("txp").requires.extend(("osgSim", "osgText"))

        # with_ffmpeg
        # setup_plugin("ffmpeg")

        # with_gstreamer
        # setup_plugin("gstreamer")

        # with_directshow
        # setup_plugin("directshow")

        if tools.apple.is_apple_os(self, self.settings.os):
            setup_plugin("imageio").frameworks = ["Accelerate"]

        if ((self.settings.os == "Macos" and self.settings.os.version and tools.scm.Version(self, self.settings.os.version) >= "10.8")
                or (self.settings.os == "iOS" and tools.scm.Version(self, self.settings.os.version) >= "6.0")):
            plugin = setup_plugin("avfoundation")
            plugin.requires.append("osgViewer")
            plugin.frameworks = ["AVFoundation", "Cocoa", "CoreVideo", "CoreMedia", "QuartzCore"]

        if self.settings.os == "Macos" and self.settings.os.version and tools.scm.Version(self, self.settings.os.version) <= "10.6" and self.settings.arch == "x86":
            setup_plugin("qt").frameworks = ["QuickTime"]

        if self.settings.os == "Macos" and self.settings.arch == "x86":
            plugin = setup_plugin("QTKit")
            plugin.requires.append("osgViewer")
            plugin.frameworks = ["QTKit", "Cocoa", "QuickTime", "CoreVideo"]

        # with_nvtt
        # setup_plugin("nvtt")

        if self.options.with_freetype:
            setup_plugin("freetype").requires.extend(("osgText", "freetype::freetype"))

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
        plugin.requires.append("osgGA")
        if self.settings.os == "Windows":
            plugin.system_libs = ["ws2_32", "winmm"]

        setup_plugin("trk")
        setup_plugin("tf")

        # with_blas
        # setup_plugin("las")

        setup_plugin("lua")

        # with_sdl
        # setup_plugin("sdl")

        if self.options.get_safe("with_asio", False):
            setup_plugin("resthttp").requires.extend(("osgPresentation", "asio::asio", "boost::boost"))

        # with_zeroconf
        # setup_plugin("zeroconf")
