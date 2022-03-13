from conans import ConanFile, CMake, tools
from pathlib import Path
import os

# conan create . -e CONAN_SYSREQUIRES_MODE=enabled

class Allegro5Conan(ConanFile):
    name = "allegro5"
    version = "5.2.7"
    license = "<Put the package license here>"
    author = "<Put your name here> <And your email here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Allegro5 here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
                
    def requirements(self):       # Conditional dependencies

        self.requires("libpng/1.6.37")
        self.requires("zlib/1.2.11")
        self.requires("libjpeg/9d")
        self.requires("freetype/2.11.1")
        self.requires("libwebp/1.2.2")
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

            package_tool = tools.SystemPackageTool(conanfile=self, default_mode='verify')
            package_tool.install(update=True, packages="libgl1-mesa-dev")
            package_tool.install(update=True, packages="libgtk-3-dev")
            
        self.options["freetype"].with_png = False
        self.options["freetype"].with_zlib = False
        self.options["freetype"].with_bzip2 = False
        self.options["freetype"].with_brotli = False
        self.options["opusfile"].http = False

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        self.run("git clone https://github.com/liballeg/allegro5.git --depth=1 --single-branch --branch=5.2.7")
        #self.run("git clone https://github.com/liballeg/allegro5.git --depth=1 --single-branch --branch=master")

    def generate(self):

        zlib = self.dependencies["zlib"]
        libpng = self.dependencies["libpng"]
        libjpeg = self.dependencies["libjpeg"]
        freetype = self.dependencies["freetype"]
        libwebp = self.dependencies["libwebp"]
        flac = self.dependencies["flac"]
        ogg = self.dependencies["ogg"]
        vorbis = self.dependencies["vorbis"]
        mp3 = self.dependencies["minimp3"]
        openal = self.dependencies["openal"]
        physfs = self.dependencies["physfs"]
        opus = self.dependencies["opus"]
        opusfile = self.dependencies["opusfile"]
        theora = self.dependencies["theora"]

        if self.settings.os != "Windows":
            alsa = self.dependencies["libalsa"]
            pulseaudio = self.dependencies["pulseaudio"]

        # Configure dependency flags for cmake
        flags = "-Wno-dev"
        flags += " -DSHARED=" + str(self.options.shared).lower()
        flags += " -DWANT_DOCS=false"
        flags += " -DWANT_DOCS_HTML=false"
        flags += " -DWANT_EXAMPLES=false"
        flags += " -DWANT_FONT=true"
        flags += " -DWANT_MONOLITH=true"
        flags += " -DWANT_TESTS=false"
        flags += " -DWANT_DEMO=false"
        flags += " -DWANT_RELEASE_LOGGING=false"
        flags += " -DWANT_VORBIS=true"
        flags += " -DWANT_MP3=true"

        prefix = "lib"
        suffix = ".a"
        if self.settings.compiler == "Visual Studio" or self.settings.compiler == "clang":
            flags += " -DWANT_STATIC_RUNTIME=" + str(self.settings.compiler.runtime == "MT").lower()
            flags += " -DPREFER_STATIC_DEPS=true"
            prefix = ""
            suffix = ".lib"
        else:
            flags += " -DWANT_STATIC_RUNTIME=false"
            flags += " -DPREFER_STATIC_DEPS=false"

        # libpng dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/image/CMakeLists.txt")), 
            "find_package(PNG)",
            '''set(PNG_FOUND 1)
               set(PNG_INCLUDE_DIR {})
               set(PNG_LIBRARIES {})
               message("-- Using PNG from conan package")'''.format(
                   libpng.package_folder.replace("\\","/") + "/include", libpng.package_folder.replace("\\","/") + "/lib/" + prefix + libpng.cpp_info.libs[0] + suffix))

        # libjpeg dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/image/CMakeLists.txt")), 
            "find_package(JPEG)",
            '''set(JPEG_FOUND 1)
               set(JPEG_INCLUDE_DIR {})
               set(JPEG_LIBRARIES {})
               message("-- Using JPEG from conan package")'''.format(
                   libjpeg.package_folder.replace("\\","/") + "/include", libjpeg.package_folder.replace("\\","/") + "/lib/" + prefix + libjpeg.cpp_info.libs[0] + suffix))

        # libwebp dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/image/CMakeLists.txt")), 
            "find_package(WebP)",
            '''set(WEBP_FOUND 1)
               set(WEBP_INCLUDE_DIRS {})
               set(WEBP_LIBRARIES {})
               message("-- Using WebP from conan package")'''.format(
                   libwebp.package_folder.replace("\\","/") + "/include", 
                   libwebp.package_folder.replace("\\","/") + "/lib/" + prefix + libwebp.cpp_info.components["webp"].libs[0] + suffix))

        # FreeType dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/CMakeLists.txt")), 
            "find_package(Freetype)",
            '''set(FREETYPE_FOUND 1)
               set(FREETYPE_INCLUDE_DIRS {} {})
               set(FREETYPE_LIBRARIES {})
               message("-- Using FreeType from conan package")'''.format(
                   freetype.package_folder.replace("\\","/") + "/include/freetype2", 
                   zlib.package_folder.replace("\\","/") + "/include", 
                   freetype.package_folder.replace("\\","/") + "/lib/" + prefix + freetype.cpp_info.libs[0] + suffix))

        # zlib dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/CMakeLists.txt")), 
            "find_package(ZLIB)",
            '''set(ZLIB_FOUND 1)
               set(ZLIB_INCLUDE_DIR {})
               set(ZLIB_LIBRARY {})
               message("-- Using ZLIB from conan package")'''.format(
                   zlib.package_folder.replace("\\","/") + "/include", 
                   zlib.package_folder.replace("\\","/") + "/lib/" + prefix + zlib.cpp_info.libs[0] + suffix))

        # flac dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/acodec/CMakeLists.txt")), 
            "find_package(FLAC)",
            '''set(FLAC_FOUND 1)
               set(FLAC_STATIC 1)
               set(FLAC_INCLUDE_DIR {})
               set(FLAC_LIBRARIES {} {})
               message("-- Using FLAC from conan package")'''.format(
                   flac.package_folder.replace("\\","/") + "/include", 
                   flac.package_folder.replace("\\","/") + "/lib/" + prefix + flac.cpp_info.components["libflac"].libs[0] + suffix,
                   ogg.package_folder.replace("\\","/") + "/lib/" + prefix + ogg.cpp_info.components["ogglib"].libs[0] + suffix))

        # vorbis dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/acodec/CMakeLists.txt")),
            "find_package(Vorbis)",
            '''set(VORBIS_FOUND 1)
               set(OGG_INCLUDE_DIR {})
               set(VORBIS_INCLUDE_DIR {})
               set(OGG_LIBRARIES {})
               set(VORBIS_LIBRARIES {} {} {})
               message("-- Using VORBIS from conan package")'''.format(
                   ogg.package_folder.replace("\\","/") + "/include", vorbis.package_folder.replace("\\","/") + "/include", 
                   ogg.package_folder.replace("\\","/") + "/lib/" + prefix + ogg.cpp_info.components["ogglib"].libs[0] + suffix,
                   vorbis.package_folder.replace("\\","/") + "/lib/" + prefix + vorbis.cpp_info.components["vorbisfile"].libs[0] + suffix,
                   vorbis.package_folder.replace("\\","/") + "/lib/" + prefix + vorbis.cpp_info.components["vorbismain"].libs[0] + suffix,
                   ogg.package_folder.replace("\\","/") + "/lib/" + prefix + ogg.cpp_info.components["ogglib"].libs[0] + suffix))

        # minimp3 dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/acodec/CMakeLists.txt")), 
            "find_package(MiniMP3)",
            '''set(MINIMP3_FOUND 1)
               set(MINIMP3_INCLUDE_DIRS {})
               list(APPEND ACODEC_INCLUDE_DIRECTORIES ${{MINIMP3_INCLUDE_DIRS}})
               message("-- Using MiniMP3 from conan package")'''.format(mp3.package_folder.replace("\\","/") + "/include"))

        # OpenAL dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/audio/CMakeLists.txt")), 
            "find_package(OpenAL)",
            '''set(OPENAL_FOUND 1)
               set(OPENAL_INCLUDE_DIR {} {})
               set(OPENAL_LIBRARY {})
               message("-- Using OpenAL from conan package")'''.format(
                   openal.package_folder.replace("\\","/") + "/include", 
                   openal.package_folder.replace("\\","/") + "/include/AL", 
                   openal.package_folder.replace("\\","/") + "/lib/" + prefix + openal.cpp_info.libs[0] + suffix))

        # PhysFS dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/CMakeLists.txt")), 
            "find_package(PhysFS)",
            '''set(PHYSFS_FOUND 1)
               set(PHYSFS_INCLUDE_DIR {})
               set(PHYSFS_LIBRARY {})
               message("-- Using PhysFS from conan package")'''.format(
                   physfs.package_folder.replace("\\","/") + "/include", 
                   physfs.package_folder.replace("\\","/") + "/lib/" + prefix + physfs.cpp_info.libs[0] + suffix))

        # libopus/opusfile dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/acodec/CMakeLists.txt")), 
            "find_package(Opus)",
            '''set(OPUS_FOUND 1)
               set(OPUS_INCLUDE_DIR {} {} {})
               set(OPUS_LIBRARIES {} {} {})
               message("-- Using OPUS from conan package")'''.format(
                   opusfile.package_folder.replace("\\","/") + "/include", opus.package_folder.replace("\\","/") + "/include", opus.package_folder.replace("\\","/") + "/include/opus", 
                   #opusfile.package_folder.replace("\\","/") + "/lib/" + prefix + opusfile.cpp_info.components["opusurl"].libs[0] + suffix,
                   opusfile.package_folder.replace("\\","/") + "/lib/" + prefix + opusfile.cpp_info.components["libopusfile"].libs[0] + suffix,
                   opus.package_folder.replace("\\","/") + "/lib/" + prefix + opus.cpp_info.components["libopus"].libs[0] + suffix,
                   ogg.package_folder.replace("\\","/") + "/lib/" + prefix + ogg.cpp_info.components["ogglib"].libs[0] + suffix))

        # libtheora dependency
        _static = "_static" if self.settings.compiler == "Visual Studio" else ""
        theoralibs = theora.package_folder.replace("\\","/") + "/lib/" + "libtheora" + _static + suffix
        if not self.settings.compiler == "Visual Studio":
            theoralibs += " " + theora.package_folder.replace("\\","/") + "/lib/" + "libtheoraenc" + _static + suffix
            theoralibs += " " + theora.package_folder.replace("\\","/") + "/lib/" + "libtheoradec" + _static + suffix

        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/video/CMakeLists.txt")), 
            "find_package(Theora)",
            '''set(THEORA_FOUND 1)
               set(THEORA_INCLUDE_DIR {})
               set(THEORA_LIBRARIES {})
               message("-- Using libtheora from conan package")'''.format(
                   theora.package_folder.replace("\\","/") + "/include", theoralibs))

        # vorbis dependency
        tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/video/CMakeLists.txt")), 
            "find_package(Vorbis)",
            '''set(VORBIS_FOUND 1)
               set(OGG_INCLUDE_DIR {})
               set(VORBIS_INCLUDE_DIR {})
               set(OGG_LIBRARIES {})
               set(VORBIS_LIBRARIES {} {} {})
               message("-- Using VORBIS from conan package")'''.format(
                   ogg.package_folder.replace("\\","/") + "/include", vorbis.package_folder.replace("\\","/") + "/include", 
                   ogg.package_folder.replace("\\","/") + "/lib/" + prefix + ogg.cpp_info.components["ogglib"].libs[0] + suffix,
                   vorbis.package_folder.replace("\\","/") + "/lib/" + prefix + vorbis.cpp_info.components["vorbisfile"].libs[0] + suffix,
                   vorbis.package_folder.replace("\\","/") + "/lib/" + prefix + vorbis.cpp_info.components["vorbismain"].libs[0] + suffix,
                   ogg.package_folder.replace("\\","/") + "/lib/" + prefix + ogg.cpp_info.components["ogglib"].libs[0] + suffix))

        if not self.settings.compiler == "Visual Studio":

            # libalsa dependency
            tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/audio/CMakeLists.txt")), 
                "pkg_check_modules(ALSA alsa)",
                '''set(ALSA_FOUND 1)
                   set(ALSA_INCLUDE_DIRS {})
                   set(ALSA_LIBRARIES {})
                   message("-- Using ALSA from conan package")'''.format(
                       alsa.package_folder.replace("\\","/") + "/include", 
                       alsa.package_folder.replace("\\","/") + "/lib/" + prefix + alsa.cpp_info.libs[0] + suffix))

            # PulseAudio dependency
            tools.replace_in_file(str(os.path.join(self.build_folder, "allegro5/addons/audio/CMakeLists.txt")), 
                "pkg_check_modules(PULSEAUDIO libpulse-simple)",
                '''set(PULSEAUDIO_FOUND 1)
                   set(PULSEAUDIO_INCLUDE_DIRS {})
                   set(PULSEAUDIO_LIBRARIES {})
                   set(PULSEAUDIO_LIBRARY_DIRS {})
                   message("-- Using PulseAudio from conan package")'''.format(
                       pulseaudio.package_folder.replace("\\","/") + "/include", 
                       pulseaudio.cpp_info.components["pulse"].libs[0],
                       pulseaudio.package_folder.replace("\\","/") + "/lib/"))

        # Disable specific compiler warnings
        if self.settings.compiler == "Visual Studio":   
            flags += " -DCMAKE_CXX_FLAGS=\"/wd4267\""   # possible loss of data warning
        else:
            flags += " -Wno-unused-variable -Wp,-w"

        # Call cmake generate
        path = Path(self.build_folder + "/allegro5/build")
        path.mkdir(parents=True, exist_ok=True)
        os.chdir(path)
        self.run("cmake .. " + flags)

    def build(self):
        if self.settings.os == "Windows":
            self.run("cd allegro5/build & cmake --build . --config RelWithDebInfo") # Build the project
        else:
            path = Path(self.build_folder + "/allegro5/build")
            path.mkdir(parents=True, exist_ok=True)
            os.chdir(path)
            self.run("make") # Build the project

    def package(self):
        self.copy("*.h", dst="include", src="allegro5/include")
        self.copy("*.inl", dst="include", src="allegro5/include")
        self.copy("*.h", dst="include", src="allegro5/build/include")

        for addon in os.listdir('allegro5/addons'):
            self.copy("*.h", dst="include", src="allegro5/addons/" + addon)

        if self.settings.compiler == "Visual Studio":
            self.copy("*.lib", dst="lib", src="allegro5/build/lib/RelWithDebInfo")
        else:
            self.copy("*.a", dst="lib", src="allegro5/build/lib")

    def package_info(self):
        self.cpp_info.libs = ["allegro_monolith-static"]
        if self.settings.os == "Windows":
            self.cpp_info.system_libs = [ "opengl32", "shlwapi" ]
