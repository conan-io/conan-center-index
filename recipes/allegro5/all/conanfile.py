from conans import ConanFile, CMake, tools
from pathlib import Path
import os

required_conan_version = ">=1.33.0"

class Allegro5Conan(ConanFile):
    name = "allegro5"
    license = ("ZLib", "BSD", "SDL", "Dejavu-fonts", "Creative Commons BY Attribution", "CBString")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/liballeg/allegro5"
    description = "Cross-platform graphics framework for basic game development and desktop applications"
    topics = ("allegro5", "gamedev", "gui", "framework", "graphics")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False], 
        "fPIC": [True, False]
    }
    default_options = {
        "shared": False, 
        "fPIC": True
    }
    
    generators = "cmake", "cmake_find_package"
    _cmake = None

    def requirements(self):       # Conditional dependencies
        self.requires("freeimage/3.18.0")
        self.requires("freetype/2.11.1")
        self.requires("flac/1.3.3")
        self.requires("ogg/1.3.5")
        self.requires("vorbis/1.3.7")
        self.requires("minimp3/20200304")
        self.requires("openal/1.21.1")
        self.requires("physfs/3.0.2")
        self.requires("opus/1.3.1")
        self.requires("opusfile/0.12")
        self.requires("theora/1.1.1")
        self.requires("opengl/system")

        if self.settings.os != "Windows":
            self.requires("xorg/system")
            self.requires("libalsa/1.2.5.1")
            self.requires("pulseaudio/14.2")
            self.requires("gtk/system")
            self.requires("openssl/1.1.1m")

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
            
    #def set_version(self):
    #    self.version = "5.2.7"

    def _patch_addon(self, addon, find, replace):
        path = None
        if (addon == None):
            path = os.path.join(self._source_subfolder, "CMakeLists.txt")
        elif (addon == "addons"):
            path = os.path.join(self._source_subfolder, "addons", "CMakeLists.txt")
        else:
            path = os.path.join(self._source_subfolder, "addons", addon, "CMakeLists.txt")
        tools.replace_in_file(path, find, replace, strict=False)
        
    def _patch_sources(self):
        self._patch_addon("image", "${FREEIMAGE_INCLUDE_PATH}", "${FreeImage_INCLUDE_DIR}")
        self._patch_addon("image", "${PNG_INCLUDE_DIR}", "${PNG_INCLUDE_DIR} ${ZLIB_INCLUDE_DIR}")
        self._patch_addon("image", "${WEBP_INCLUDE_DIRS}", "${WebP_INCLUDE_DIRS}")
        self._patch_addon("acodec", "find_package(FLAC)", "find_package(flac REQUIRED)\nset(FLAC_STATIC 1)\n")

        self._patch_addon("acodec", "${VORBIS_INCLUDE_DIR}", "${Vorbis_INCLUDE_DIR}")
        self._patch_addon("video", "${VORBIS_INCLUDE_DIR}", "${Vorbis_INCLUDE_DIR}")
        self._patch_addon("acodec", "${VORBIS_LIBRARIES}", "${Vorbis_LIBRARIES}")
        self._patch_addon("video", "${VORBIS_LIBRARIES}", "${Vorbis_LIBRARIES}")

        self._patch_addon("acodec", "${OGG_INCLUDE_DIR}", "${Ogg_INCLUDE_DIR}")
        self._patch_addon("video", "${OGG_INCLUDE_DIR}", "${Ogg_INCLUDE_DIR}")

        self._patch_addon("acodec", "find_package(Opus)", "find_package(Opus REQUIRED)\nfind_package(opusfile)")
        self._patch_addon("acodec", "${OPUS_INCLUDE_DIR}", "${Opus_INCLUDE_DIR} ${opusfile_INCLUDE_DIR}")
        self._patch_addon("acodec", "${OPUS_LIBRARIES}", "${Opus_LIBRARIES} ${opusfile_LIBRARIES}")

        self._patch_addon("acodec", "find_package(MiniMP3)", "find_package(minimp3 REQUIRED)")
        self._patch_addon("acodec", "${MINIMP3_INCLUDE_DIRS}", "${minimp3_INCLUDE_DIRS}")
        self._patch_addon("acodec", "list(APPEND ACODEC_SOURCES mp3.c)", 
            "list(APPEND ACODEC_SOURCES mp3.c)\nlist(APPEND ACODEC_INCLUDE_DIRECTORIES ${minimp3_INCLUDE_DIRS})")

        self._patch_addon("video", "find_package(Theora)", "find_package(theora REQUIRED)")
        self._patch_addon("video", "${THEORA_INCLUDE_DIR}", "${theora_INCLUDE_DIR}")
        self._patch_addon("video", "${THEORA_LIBRARIES}", "${theora_LIBRARIES}")

        self._patch_addon("addons", "find_package(PhysFS)", "find_package(PhysFS REQUIRED)")
        self._patch_addon("addons", "if(PHYSFS_FOUND)", "if(PhysFS_FOUND)")
        self._patch_addon("addons", "${PHYSFS_INCLUDE_DIR}", "${physfs_INCLUDE_DIR}")
        self._patch_addon("addons", "${PHYSFS_LIBRARY}", "${physfs_LIBRARY}")
        self._patch_addon("physfs", "${PHYSFS_INCLUDE_DIR}", "${physfs_INCLUDE_DIR}")
        self._patch_addon("physfs", "${PHYSFS_INCLUDE_FILES}", "${physfs_INCLUDE_FILES}")
        self._patch_addon("addons", "find_package_handle_standard_args(PHYSFS DEFAULT_MSG\n        PHYSFS_LIBRARY PHYSFS_INCLUDE_DIR)", "")

        self._patch_addon(None, "find_package(X11)", "find_package(X11 REQUIRED)\nset(X11_LIBRARIES ${X11_LIBRARIES} xcb dl)")
        self._patch_addon("addons", "run_c_compile_test(\"${FREETYPE_TEST_SOURCE}\" TTF_COMPILES)", "")
        self._patch_addon("addons", "run_c_compile_test(\"${FREETYPE_TEST_SOURCE}\" TTF_COMPILES_WITH_EXTRA_DEPS)", 
            '''find_package(Brotli REQUIRED)
               list(APPEND FREETYPE_STATIC_LIBRARIES "${Brotli_LIBRARIES}")
               run_c_compile_test("${FREETYPE_TEST_SOURCE}" TTF_COMPILES_WITH_EXTRA_DEPS)''')
        
            

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["SHARED"] = self.options.shared
        self._cmake.definitions["WANT_STATIC_RUNTIME"] = self.settings.compiler.runtime == "MT" if self._is_msvc else False
        self._cmake.definitions["CMAKE_BUILD_TYPE"] = self.settings.build_type
        self._cmake.definitions["PREFER_STATIC_DEPS"] = True
        self._cmake.definitions["WANT_DOCS"] = False
        self._cmake.definitions["WANT_DOCS_HTML"] = False
        self._cmake.definitions["WANT_EXAMPLES"] = False
        self._cmake.definitions["WANT_FONT"] = True
        self._cmake.definitions["WANT_MONOLITH"] = True
        self._cmake.definitions["WANT_TESTS"] = False
        self._cmake.definitions["WANT_DEMO"] = False
        self._cmake.definitions["WANT_RELEASE_LOGGING"] = False
        self._cmake.definitions["WANT_VORBIS"] = True
        self._cmake.definitions["WANT_MP3"] = True
        self._cmake.definitions["WANT_OGG_VIDEO"] = True

        self._cmake.definitions["FREETYPE_ZLIB"] = True
        self._cmake.definitions["FREETYPE_BZIP2"] = True
        self._cmake.definitions["FREETYPE_PNG"] = True
        self._cmake.definitions["FREETYPE_HARFBUZZ"] = False
            
        self._cmake.definitions["CMAKE_CXX_FLAGS"] = "/wd4267 /wd4018" if self._is_msvc else "-Wno-unused-variable -w"
        
        self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["allegro_monolith-static"]

        if not self.options.shared:
            self.cpp_info.defines = ["ALLEGRO_STATICLINK"]

        if self.settings.os == "Windows":
            self.cpp_info.system_libs = [ "opengl32", "shlwapi" ]
