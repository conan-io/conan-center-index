import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import is_apple_os
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, replace_in_file, rmdir, rm
from conan.tools.gnu import PkgConfigDeps
from conan.tools.microsoft import is_msvc_static_runtime
from conan.tools.scm import Version

required_conan_version = ">=1.53.0"


class PangolinConan(ConanFile):
    name = "pangolin"
    description = "Pangolin is a lightweight portable rapid development library for managing OpenGL display / interaction and abstracting video input."
    license = "MIT"
    homepage = "https://github.com/stevenlovegrove/Pangolin"
    url = "https://github.com/conan-io/conan-center-index"
    topics = "computer-vision", "video", "camera", "3d", "visualization", "gui"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "python_bindings": [True, False],
        "tools": [True, False],
        "with_dc1394": [True, False],
        "with_ffmpeg": [True, False],
        "with_jpeg": [True, False],
        "with_lz4": [True, False],
        "with_openexr": [True, False],
        "with_png": [True, False],
        "with_raw": [True, False],
        "with_realsense": [True, False],
        "with_tiff": [True, False],
        "with_toon": [True, False],
        "with_uvc": [True, False],
        "with_v4l": [True, False],
        "with_wayland": [True, False],
        "with_x11": [True, False],
        "with_zstd": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "python_bindings": False,
        "tools": False,
        "with_dc1394": False,
        "with_ffmpeg": True,
        "with_jpeg": True,
        "with_lz4": False,
        "with_openexr": False,
        "with_png": True,
        "with_raw": False,
        "with_realsense": False,
        "with_tiff": False,
        "with_toon": False,
        "with_uvc": False,
        "with_v4l": False,
        "with_wayland": False,
        "with_x11": True,
        "with_zstd": False,
    }
    options_description = {
        "python_bindings": "Support Pangolin Interactive Console",
        "with_dc1394": "Support DC1394 video input",
        # "with_depthsense": "Support DepthSense video input",
        "with_ffmpeg": "Support FFMPEG video input",
        "with_jpeg": "Support JPEG image input",
        "with_lz4": "Support LZ4 compression",
        "with_openexr": "Support EXR image input",
        # "with_openni2": "Support OpenNI2 video input",
        # "with_pleora": "Support Pleora video input",
        "with_png": "Support PNG image input",
        "with_raw": "Support raw images",
        "with_realsense": "Support RealSense video input",
        # "with_telicam": "Support TeliCam video input",
        "with_tiff": "Support TIFF image input",
        "with_toon": "Support TooN numerics library",
        "with_uvc": "Support USB Video Devices input",
        # "with_uvc_mediafoundation": "Support MediaFoundation UVC input",
        "with_v4l": "Support Video4Linux input",
        "with_wayland": "Support Wayland windowing system",
        "with_x11": "Support X11 windowing system",
        "with_zstd": "Support Zstd compression",
    }

    @property
    def _min_cppstd(self):
        return 17

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "7",
            "clang": "5",
            "apple-clang": "10",
            "Visual Studio": "15",
            "msvc": "191",
        }

    def export_sources(self):
        copy(self, "conan_deps.cmake", self.recipe_folder, os.path.join(self.export_sources_folder, "src"))

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        if self.settings.os not in ["Linux", "FreeBSD"]:
            del self.options.with_x11
        if self.settings.os != "Linux":
            del self.options.with_wayland
            del self.options.with_v4l

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.options["ffmpeg"].avdevice = True
        self.options["ffmpeg"].avformat = True

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("eigen/3.4.0", transitive_headers=True, transitive_libs=True)
        self.requires("glew/2.2.0", transitive_headers=True, transitive_libs=True)
        self.requires("opengl/system", transitive_headers=True, transitive_libs=True)
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.requires("egl/system", transitive_headers=True, transitive_libs=True)
        if self.options.get_safe("with_wayland"):
            # Wayland 1.20+ is not compatible as of v0.9.1
            self.requires("wayland/1.19.0")
            self.requires("wayland-protocols/1.33")
            self.requires("xkbcommon/1.6.0")
        if self.options.get_safe("with_x11"):
            # https://github.com/stevenlovegrove/Pangolin/blob/v0.9.1/components/pango_windowing/include/pangolin/windowing/X11Window.h#L35
            self.requires("xorg/system", transitive_headers=True, transitive_libs=True)
        if self.options.with_dc1394:
            # https://github.com/stevenlovegrove/Pangolin/blob/v0.9.1/components/pango_video/include/pangolin/video/drivers/firewire.h#L32
            self.requires("libdc1394/2.2.7", transitive_headers=True, transitive_libs=True)
        if self.options.with_ffmpeg:
            # https://github.com/stevenlovegrove/Pangolin/blob/v0.9.1/components/pango_video/include/pangolin/video/drivers/ffmpeg_common.h#L15-L19
            self.requires("ffmpeg/6.1", transitive_headers=True, transitive_libs=True)
        if self.options.with_jpeg:
            self.requires("libjpeg/9e")
        if self.options.with_lz4:
            self.requires("lz4/1.9.4")
        if self.options.with_openexr:
            self.requires("openexr/2.5.7")
        if self.options.with_png:
            self.requires("libpng/[>=1.6 <2]")
        if self.options.python_bindings:
            self.requires("cpython/3.12.2")
            self.requires("pybind11/2.12.0")
        if self.options.with_raw:
            self.requires("libraw/0.21.2")
        if self.options.with_realsense:
            self.requires("librealsense/2.53.1")
        if self.options.with_tiff:
            self.requires("libtiff/4.6.0")
        if self.options.with_toon:
            # https://github.com/stevenlovegrove/Pangolin/blob/v0.9.1/components/pango_opengl/include/pangolin/gl/cg.h#L40
            self.requires("toon/3.2", transitive_headers=True, transitive_libs=True)
        if self.options.with_uvc:
            # https://github.com/stevenlovegrove/Pangolin/blob/v0.9.1/components/pango_video/include/pangolin/video/drivers/uvc.h#L41
            self.requires("libuvc/0.0.7", transitive_headers=True, transitive_libs=True)
            self.requires("libusb/1.0.26")
        if self.options.with_zstd:
            self.requires("zstd/1.5.5")

        # Unvendored
        # https://github.com/stevenlovegrove/Pangolin/blob/v0.9.1/components/pango_core/include/pangolin/utils/signal_slot.h
        self.requires("sigslot/1.2.2", transitive_headers=True, transitive_libs=True)
        self.requires("tinyobjloader/2.0.0-rc10")
        # TODO: dynalo, NaturalSort

    def validate(self):
        if self.settings.compiler.cppstd:
            check_min_cppstd(self, self._min_cppstd)
        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and Version(self.settings.compiler.version) < minimum_version:
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support."
            )

        if self.options.with_ffmpeg:
            ffmpeg_opts = self.dependencies["ffmpeg"].options
            if not ffmpeg_opts.avdevice or not ffmpeg_opts.avformat:
                raise ConanInvalidConfiguration("Ffmpeg with avdevice and avformat options enabled is required")

    def build_requirements(self):
        if self.options.get_safe("with_wayland"):
            if not self.conf.get("tools.gnu:pkg_config", check_type=str):
                self.tool_requires("pkgconf/2.2.0")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_PANGOLIN_DEPTHSENSE"] = False
        tc.variables["BUILD_PANGOLIN_FFMPEG"] = self.options.with_ffmpeg
        tc.variables["BUILD_PANGOLIN_LIBDC1394"] = self.options.with_dc1394
        tc.variables["BUILD_PANGOLIN_LIBJPEG"] = self.options.with_jpeg
        tc.variables["BUILD_PANGOLIN_LIBOPENEXR"] = self.options.with_openexr
        tc.variables["BUILD_PANGOLIN_LIBPNG"] = self.options.with_png
        tc.variables["BUILD_PANGOLIN_LIBRAW"] = self.options.with_raw
        tc.variables["BUILD_PANGOLIN_LIBTIFF"] = self.options.with_tiff
        tc.variables["BUILD_PANGOLIN_LIBUVC"] = self.options.with_uvc
        tc.variables["BUILD_PANGOLIN_LZ4"] = self.options.with_lz4
        tc.variables["BUILD_PANGOLIN_OPENNI"] = False
        tc.variables["BUILD_PANGOLIN_OPENNI2"] = False
        tc.variables["BUILD_PANGOLIN_PLEORA"] = False
        tc.variables["BUILD_PANGOLIN_PYTHON"] = self.options.python_bindings
        tc.variables["BUILD_PANGOLIN_REALSENSE"] = False
        tc.variables["BUILD_PANGOLIN_REALSENSE2"] = self.options.with_realsense
        tc.variables["BUILD_PANGOLIN_TELICAM"] = False
        tc.variables["BUILD_PANGOLIN_UVC_MEDIAFOUNDATION"] = False
        tc.variables["BUILD_PANGOLIN_V4L"] = self.options.get_safe("with_v4l", False)
        tc.variables["BUILD_PANGOLIN_ZSTD"] = self.options.with_zstd
        tc.variables["BUILD_TESTS"] = False
        tc.variables["BUILD_TOOLS"] = self.options.tools
        tc.variables["MSVC_USE_STATIC_CRT"] = is_msvc_static_runtime(self)
        tc.variables["CMAKE_DISABLE_FIND_PACKAGE_X11"] = not self.options.get_safe("with_x11", False)
        tc.cache_variables["CMAKE_PROJECT_Pangolin_INCLUDE"] = "conan_deps.cmake"
        tc.cache_variables["CMAKE_POLICY_DEFAULT_CMP0077"] = "NEW"
        tc.generate()

        deps = CMakeDeps(self)
        deps.set_property("ffmpeg", "cmake_file_name", "FFMPEG")
        deps.set_property("libdc1394", "cmake_file_name", "DC1394")
        deps.set_property("librealsense", "cmake_file_name", "RealSense2")
        deps.set_property("libusb", "cmake_file_name", "libusb1")
        deps.set_property("libuvc", "cmake_file_name", "uvc")
        deps.set_property("lz4", "cmake_file_name", "Lz4")
        deps.set_property("tinyobjloader", "cmake_target_name", "tinyobj")
        # deps.set_property("depthsense", "cmake_file_name", "DepthSense")
        # deps.set_property("mediafoundation", "cmake_file_name", "MediaFoundation")
        # deps.set_property("openni2", "cmake_file_name", "OpenNI2")
        # deps.set_property("pleora", "cmake_file_name", "Pleora")
        # deps.set_property("telicam", "cmake_file_name", "TeliCam")
        deps.generate()

        if self.options.get_safe("with_wayland"):
            deps = PkgConfigDeps(self)
            deps.generate()
            venv = VirtualBuildEnv(self)
            venv.generate()

    def _patch_sources(self):
        rm(self, "Find*.cmake", os.path.join(self.source_folder, "cmake"))

        # Unvendor sigslot
        rmdir(self, os.path.join(self.source_folder, "components", "pango_core", "include", "sigslot"))

        # Unvendor tinyobjloader
        rmdir(self, os.path.join(self.source_folder, "components", "tinyobj"))
        replace_in_file(self, os.path.join(self.source_folder, "components", "pango_geometry", "src", "geometry_obj.cpp"),
                        "#include <tinyobj/tiny_obj_loader.h>", "#include <tiny_obj_loader.h>")

        # Disable Wayland if not enabled
        if not self.options.get_safe("with_wayland"):
            replace_in_file(self, os.path.join(self.source_folder, "components", "pango_windowing", "CMakeLists.txt"),
                            "WAYLAND_CLIENT_FOUND", "FALSE")

        # Fix a buggy application of a macro when TooN is enabled
        # TODO: submit a patch upstream
        replace_in_file(self, os.path.join(self.source_folder, "components", "pango_opengl", "include", "pangolin", "gl", "opengl_render_state.h"),
                        "PANGOLIN_DEPRECATED\n", 'PANGOLIN_DEPRECATED("")\n')

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENCE", self.source_folder, os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rm(self, "*.pdb", self.package_folder, recursive=True)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Pangolin")

        def _add_component(name, requires):
            self.cpp_info.components[name].set_property("cmake_target_name", name)
            self.cpp_info.components[name].libs = [name]
            self.cpp_info.components[name].requires = requires
            return self.cpp_info.components[name]

        pango_core = _add_component("pango_core", requires=["eigen::eigen", "sigslot::sigslot"])
        pango_core.defines = ["HAVE_EIGEN", "HAVE_GLEW"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            pango_core.system_libs.extend(["pthread", "rt", "dl"])

        _add_component("pango_display", requires=["pango_core", "pango_opengl", "pango_windowing", "pango_vars"])
        _add_component("pango_geometry", requires=["pango_core", "pango_image", "tinyobjloader::tinyobjloader"])
        _add_component("pango_glgeometry", requires=["pango_geometry", "pango_opengl"])
        _add_component("pango_packetstream", requires=["pango_core"])
        _add_component("pango_plot", requires=["pango_display"])
        _add_component("pango_scene", requires=["pango_opengl"])
        _add_component("pango_tools", requires=["pango_display", "pango_video"])
        _add_component("pango_vars", requires=["pango_core"])

        pango_opengl = _add_component("pango_opengl", requires=["pango_core", "pango_image", "opengl::opengl", "glew::glew"])
        if self.options.with_toon:
            pango_opengl.requires.append("toon::toon")
            pango_opengl.defines.append("HAVE_TOON")

        if self.options.python_bindings:
            _add_component("pango_python", requires=["pybind11::pybind11", "cpython::cpython"])

        pango_image = _add_component("pango_image", requires=["pango_core"])
        if self.options.with_jpeg:
            pango_image.requires.append("libjpeg::libjpeg")
        if self.options.with_lz4:
            pango_image.requires.append("lz4::lz4")
        if self.options.with_openexr:
            pango_image.requires.append("openexr::openexr")
        if self.options.with_png:
            pango_image.requires.append("libpng::libpng")
        if self.options.with_raw:
            pango_image.requires.append("libraw::libraw")
        if self.options.with_tiff:
            pango_image.requires.append("libtiff::libtiff")
        if self.options.with_zstd:
            self.cpp_info.requires.append("zstd::zstd")

        pango_video = _add_component("pango_video", requires=["pango_core", "pango_image", "pango_packetstream"])
        if self.options.with_dc1394:
            pango_video.requires.append("libdc1394::libdc1394")
        if self.options.with_ffmpeg:
            pango_video.requires.extend(["ffmpeg::avcodec", "ffmpeg::avdevice", "ffmpeg::avformat", "ffmpeg::avutil"])
        if self.options.with_realsense:
            pango_video.requires.append("librealsense::librealsense")
        if self.options.with_uvc:
            pango_video.requires.extend(["libuvc::libuvc", "libusb::libusb"])

        pango_windowing = _add_component("pango_windowing", requires=["pango_core", "pango_opengl"])
        if self.settings.os in ["Linux", "FreeBSD"]:
            pango_windowing.requires.append("egl::egl")
        if is_apple_os(self):
            pango_windowing.frameworks.append("Cocoa")
        if self.options.get_safe("with_wayland"):
            pango_windowing.requires.extend([
                "wayland::wayland-client",
                "wayland::wayland-cursor",
                "wayland::wayland-egl",
                "wayland-protocols::wayland-protocols",
                "xkbcommon::xkbcommon",
            ])
        if self.options.get_safe("with_x11"):
            pango_windowing.requires.append("xorg::x11")
