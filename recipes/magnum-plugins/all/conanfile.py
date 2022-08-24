from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration, ConanException
import os
import textwrap

required_conan_version = ">=1.33.0"


class MagnumConan(ConanFile):
    name = "magnum-plugins"
    description = "Plugins for the Magnum C++11/C++14 graphics engine"
    license = "MIT"
    topics = ("magnum", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "shared_plugins": [True, False],

        "assimp_importer": [True, False],
        "basis_imageconverter": [True, False],
        "basis_importer": [True, False],
        "dds_importer": [True, False],
        "devil_imageimporter": [True, False],
        "drflac_audioimporter": [True, False],
        "drmp3_audioimporter": [True, False],
        "drwav_audioimporter": [True, False],
        "faad2_audioimporter": [True, False],
        "freetype_font": [True, False],
        "harfbuzz_font": [True, False],
        "ico_importer": [True, False],
        "jpeg_imageconverter": [True, False],
        "jpeg_importer": [True, False],
        "meshoptimizer_sceneconverter": [True, False],
        "miniexr_imageconverter": [True, False],
        "opengex_importer": [True, False],
        "png_imageconverter": [True, False],
        "png_importer": [True, False],
        "primitive_importer": [True, False],
        "stanford_importer": [True, False],
        "stanford_sceneconverter": [True, False],
        "stb_imageconverter": [True, False],
        "stb_imageimporter": [True, False],
        "stbtruetype_font": [True, False],
        "stbvorbis_audioimporter": [True, False],
        "stl_importer": [True, False],
        "tinygltf_importer": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "shared_plugins": True,
        
        "assimp_importer": True,
        "basis_imageconverter": False,
        "basis_importer": False,
        "dds_importer": True,
        "devil_imageimporter": False,
        "drflac_audioimporter": True,
        "drmp3_audioimporter": True,
        "drwav_audioimporter": True,
        "faad2_audioimporter": False,
        "freetype_font": True,
        "harfbuzz_font": True,
        "ico_importer": True,
        "jpeg_imageconverter": True,
        "jpeg_importer": True,
        "meshoptimizer_sceneconverter": True,
        "miniexr_imageconverter": True,
        "opengex_importer": True,
        "png_imageconverter": True,
        "png_importer": True,
        "primitive_importer": True,
        "stanford_importer": True,
        "stanford_sceneconverter": True,
        "stb_imageconverter": True,
        "stb_imageimporter": True,
        "stbtruetype_font": True,
        "stbvorbis_audioimporter": True,
        "stl_importer": True,
        "tinygltf_importer": True,
    }
    generators = "cmake", "cmake_find_package", "cmake_find_package_multi"
    exports_sources = ["CMakeLists.txt", "cmake/*", "patches/*"]

    _cmake = None
    short_paths = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)
        tools.replace_in_file(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                              'set(CMAKE_MODULE_PATH "${PROJECT_SOURCE_DIR}/modules/" ${CMAKE_MODULE_PATH})',
                              "")
        assimp_importer_cmake_file = os.path.join(self._source_subfolder, "src", "MagnumPlugins", "AssimpImporter", "CMakeLists.txt")
        tools.replace_in_file(assimp_importer_cmake_file,
                              "find_package(Assimp REQUIRED)",
                              "find_package(assimp REQUIRED)")
        tools.replace_in_file(assimp_importer_cmake_file,
                              "Assimp::Assimp",
                              "assimp::assimp")

        harfbuzz_cmake_file = os.path.join(self._source_subfolder, "src", "MagnumPlugins", "HarfBuzzFont", "CMakeLists.txt")
        tools.replace_in_file(harfbuzz_cmake_file,
                              "find_package(HarfBuzz REQUIRED)",
                              "find_package(harfbuzz REQUIRED)")
        tools.replace_in_file(harfbuzz_cmake_file,
                              "HarfBuzz::HarfBuzz",
                              "harfbuzz::harfbuzz")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

        if self.settings.os == "Emscripten":
            self.options.shared_plugins = False
            # FIXME: Transitive dep 'glib' is not prepared for Emscripten (https://github.com/emscripten-core/emscripten/issues/11066)
            self.options.harfbuzz_font = False
            # Audio is not provided by Magnum
            self.options.drflac_audioimporter = False
            self.options.drmp3_audioimporter = False
            self.options.drwav_audioimporter = False
            self.options.faad2_audioimporter = False
            self.options.stbvorbis_audioimporter = False
            # FIXME: Conan package fails for 'brotli'
            self.options.freetype_font = False

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
    
    def requirements(self):
        self.requires("magnum/{}".format(self.version))
        if self.options.assimp_importer:
            self.requires("assimp/5.0.1")
        if self.options.harfbuzz_font:
            self.requires("harfbuzz/2.8.2")
        if self.options.freetype_font:
            self.requires("freetype/2.11.0")
        if self.options.jpeg_importer or self.options.jpeg_imageconverter:
            self.requires("libjpeg/9d")
        if self.options.meshoptimizer_sceneconverter:
            self.requires("meshoptimizer/0.15")
        if self.options.png_imageconverter:
            self.requires("libpng/1.6.37")
        if self.options.basis_imageconverter or self.options.basis_importer:
            raise ConanInvalidConfiguration("Requires 'basisuniversal', not available in ConanCenter yet")
        if self.options.devil_imageimporter:
            raise ConanInvalidConfiguration("Requires 'DevIL', not available in ConanCenter yet")
        if self.options.faad2_audioimporter:
            raise ConanInvalidConfiguration("Requires 'faad2', not available in ConanCenter yet")

    def build_requirements(self):
        self.build_requires("corrade/{}".format(self.version))

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

        if not self.options["magnum"].trade:
            raise ConanInvalidConfiguration("Magnum Trade is required")

        # TODO: There are lot of things to check here: 'magnum::audio' required for audio plugins...

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_STATIC"] = not self.options.shared
        self._cmake.definitions["BUILD_STATIC_PIC"] = self.options.get_safe("fPIC", False)
        self._cmake.definitions["BUILD_PLUGINS_STATIC"] = not self.options.shared_plugins
        self._cmake.definitions["LIB_SUFFIX"] = ""
        self._cmake.definitions["BUILD_TESTS"] = False

        self._cmake.definitions["WITH_ASSIMPIMPORTER"] = self.options.assimp_importer
        self._cmake.definitions["WITH_BASISIMAGECONVERTER"] = self.options.basis_imageconverter
        self._cmake.definitions["WITH_BASISIMPORTER"] = self.options.basis_importer
        self._cmake.definitions["WITH_DDSIMPORTER"] = self.options.dds_importer
        self._cmake.definitions["WITH_DEVILIMAGEIMPORTER"] = self.options.devil_imageimporter
        self._cmake.definitions["WITH_DRFLACAUDIOIMPORTER"] = self.options.drflac_audioimporter
        self._cmake.definitions["WITH_DRMP3AUDIOIMPORTER"] = self.options.drmp3_audioimporter
        self._cmake.definitions["WITH_DRWAVAUDIOIMPORTER"] = self.options.drwav_audioimporter
        self._cmake.definitions["WITH_FAAD2AUDIOIMPORTER"] = self.options.faad2_audioimporter
        self._cmake.definitions["WITH_FREETYPEFONT"] = self.options.freetype_font
        self._cmake.definitions["WITH_HARFBUZZFONT"] = self.options.harfbuzz_font
        self._cmake.definitions["WITH_ICOIMPORTER"] = self.options.ico_importer
        self._cmake.definitions["WITH_JPEGIMAGECONVERTER"] = self.options.jpeg_imageconverter
        self._cmake.definitions["WITH_JPEGIMPORTER"] = self.options.jpeg_importer
        self._cmake.definitions["WITH_MESHOPTIMIZERSCENECONVERTER"] = self.options.meshoptimizer_sceneconverter
        self._cmake.definitions["WITH_MINIEXRIMAGECONVERTER"] = self.options.miniexr_imageconverter
        self._cmake.definitions["WITH_OPENGEXIMPORTER"] = self.options.opengex_importer
        self._cmake.definitions["WITH_PNGIMAGECONVERTER"] = self.options.png_imageconverter
        self._cmake.definitions["WITH_PNGIMPORTER"] = self.options.png_importer
        self._cmake.definitions["WITH_PRIMITIVEIMPORTER"] = self.options.primitive_importer
        self._cmake.definitions["WITH_STANFORDIMPORTER"] = self.options.stanford_importer
        self._cmake.definitions["WITH_STANFORDSCENECONVERTER"] = self.options.stanford_sceneconverter
        self._cmake.definitions["WITH_STBIMAGECONVERTER"] = self.options.stb_imageconverter
        self._cmake.definitions["WITH_STBIMAGEIMPORTER"] = self.options.stb_imageimporter
        self._cmake.definitions["WITH_STBTRUETYPEFONT"] = self.options.stbtruetype_font
        self._cmake.definitions["WITH_STBVORBISAUDIOIMPORTER"] = self.options.stbvorbis_audioimporter
        self._cmake.definitions["WITH_STLIMPORTER"] = self.options.stl_importer
        self._cmake.definitions["WITH_TINYGLTFIMPORTER"] = self.options.tinygltf_importer

        self._cmake.configure()
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()

        cm = self._configure_cmake()
        cm.build()

    def package(self):
        cm = self._configure_cmake()
        cm.install()

        if not self.options.shared_plugins:
            build_modules_folder = os.path.join(self.package_folder, "lib", "cmake")
            os.makedirs(build_modules_folder)
            for component, target, library, folder, deps in self._plugins:
                build_module_path = os.path.join(build_modules_folder, "conan-magnum-plugins-{}.cmake".format(component))
                with open(build_module_path, "w+") as f:
                    f.write(textwrap.dedent("""\
                        if(NOT ${{CMAKE_VERSION}} VERSION_LESS "3.0")
                            if(TARGET MagnumPlugins::{target})
                                set_target_properties(MagnumPlugins::{target} PROPERTIES INTERFACE_SOURCES 
                                                    "${{CMAKE_CURRENT_LIST_DIR}}/../../include/MagnumPlugins/{library}/importStaticPlugin.cpp")
                            endif()
                        endif()
                    """.format(target=target, library=library)))

        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy("*.cmake", src=os.path.join(self.source_folder, "cmake"), dst=os.path.join("lib", "cmake"))
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "MagnumPlugins"
        self.cpp_info.names["cmake_find_package_multi"] = "MagnumPlugins"

        magnum_plugin_libdir = "magnum-d" if self.settings.build_type == "Debug" and self.options.shared_plugins else "magnum"
        plugin_lib_suffix = "-d" if self.settings.build_type == "Debug" and not self.options.shared_plugins else ""
        lib_suffix = "-d" if self.settings.build_type == "Debug" else ""

        self.cpp_info.components["magnumopenddl"].names["cmake_find_package"] = "MagnumOpenDdl"
        self.cpp_info.components["magnumopenddl"].names["cmake_find_package_multi"] = "MagnumOpenDdl"
        self.cpp_info.components["magnumopenddl"].libs = ["MagnumOpenDdl{}".format(lib_suffix)]
        self.cpp_info.components["magnumopenddl"].requires = ["magnum::magnum"]

        # Plugins
        if self.options.basis_imageconverter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.basis_importer:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.devil_imageimporter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.faad2_audioimporter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        # The global target doesn't provide anything in this package. Null it.
        self.cpp_info.components["_global_target"].names["cmake_find_package"] = "MagnumPlugins"
        self.cpp_info.components["_global_target"].names["cmake_find_package_multi"] = "MagnumPlugins"
        self.cpp_info.components["_global_target"].build_modules["cmake_find_package"].append(os.path.join("lib", "cmake", "conan-bugfix-global-target.cmake"))

        # Add all the plugins
        for component, target, library, folder, deps in self._plugins:
            self.cpp_info.components[component].names["cmake_find_package"] = target
            self.cpp_info.components[component].names["cmake_find_package_multi"] = target
            self.cpp_info.components[component].libs = ["{}{}".format(library, plugin_lib_suffix)]
            self.cpp_info.components[component].libdirs = [os.path.join(self.package_folder, "lib", magnum_plugin_libdir, folder)]
            self.cpp_info.components[component].requires = deps
            if not self.options.shared_plugins:
                self.cpp_info.components[component].build_modules.append(os.path.join("lib", "cmake", "conan-magnum-plugins-{}.cmake".format(component)))
        plugin_dir = "bin" if self.settings.os == "Windows" else "lib"
        self.user_info.plugins_basepath = os.path.join(self.package_folder, plugin_dir, magnum_plugin_libdir)

    @property
    def _plugins(self):
        #   (opt_name, (component, target, library, folder, deps))
        all_plugins = (
            ("assimp_importer", ("assimp_importer", "AssimpImporter", "AssimpImporter", "importers", ["magnum::trade", "assimp::assimp"])), 
            ("basis_imageconverter", ("basis_imageconverter", "--", "--", "--", [])), 
            ("basis_importer", ("basis_importer", "--", "--", "--", [])), 
            ("dds_importer", ("dds_importer", "DdsImporter", "DdsImporter", "importers", ["magnum::trade"])), 
            ("devil_imageimporter", ("devil_imageimporter", "--", "--", "--", [])), 
            ("drflac_audioimporter", ("drflac_audioimporter", "DrFlacAudioImporter", "DrFlacAudioImporter", "audioimporters", ["magnum::audio"])), 
            ("drmp3_audioimporter", ("drmp3_audioimporter", "DrMp3AudioImporter", "DrMp3AudioImporter", "audioimporters", ["magnum::audio"])), 
            ("drwav_audioimporter", ("drwav_audioimporter", "DrWavAudioImporter", "DrWavAudioImporter", "audioimporters", ["magnum::audio"])), 
            ("faad2_audioimporter", ("faad2_audioimporter", "--", "--", "--", [])), 
            ("freetype_font", ("freetype_font", "FreeTypeFont", "FreeTypeFont", "fonts", ["magnum::text", "freetype::freetype"])), 
            ("harfbuzz_font", ("harfbuzz_font", "HarfBuzzFont", "HarfBuzzFont", "fonts", ["magnum::text", "harfbuzz::harfbuzz"])), 
            ("jpeg_imageconverter", ("jpeg_imageconverter", "JpegImageConverter", "JpegImageConverter", "imageconverters", ["magnum::trade", "libjpeg::libjpeg"])), 
            ("jpeg_importer", ("jpeg_importer", "JpegImporter", "JpegImporter", "importers", ["magnum::trade", "libjpeg::libjpeg"])), 
            ("meshoptimizer_sceneconverter", ("meshoptimizer_sceneconverter", "MeshOptimizerSceneConverter", "MeshOptimizerSceneConverter", "sceneconverters", ["magnum::trade", "magnum::mesh_tools", "meshoptimizer::meshoptimizer"])), 
            ("miniexr_imageconverter", ("miniexr_imageconverter", "MiniExrImageConverter", "MiniExrImageConverter", "imageconverters", ["magnum::trade"])), 
            ("opengex_importer", ("opengex_importer", "OpenGexImporter", "OpenGexImporter", "importers", ["magnum::trade", "magnumopenddl", "magnum::any_image_importer"])), 
            ("png_importer", ("png_importer", "PngImporter", "PngImporter", "importers", ["magnum::trade", "libpng::libpng"])), 
            ("png_imageconverter", ("png_imageconverter", "PngImageConverter", "PngImageConverter", "imageconverters", ["magnum::trade"])), 
            ("primitive_importer", ("primitive_importer", "PrimitiveImporter", "PrimitiveImporter", "importers", ["magnum::primitives", "magnum::trade"])), 
            ("stanford_importer", ("stanford_importer", "StanfordImporter", "StanfordImporter", "importers", ["magnum::mesh_tools", "magnum::trade"])), 
            ("stanford_sceneconverter", ("stanford_sceneconverter", "StanfordSceneConverter", "StanfordSceneConverter", "sceneconverters", ["magnum::mesh_tools", "magnum::trade"])), 
            ("stb_imageconverter", ("stb_imageconverter", "StbImageConverter", "StbImageConverter", "imageconverters", ["magnum::trade"])), 
            ("stb_imageimporter", ("stb_imageimporter", "StbImageImporter", "StbImageImporter", "importers", ["magnum::trade"])), 
            ("stbtruetype_font", ("stbtruetype_font", "StbTrueTypeFont", "StbTrueTypeFont", "fonts", ["magnum::text"])), 
            ("stbvorbis_audioimporter", ("stbvorbis_audioimporter", "StbVorbisAudioImporter", "StbVorbisAudioImporter", "audioimporters", ["magnum::audio"])), 
            ("tinygltf_importer", ("tinygltf_importer", "TinyGltfImporter", "TinyGltfImporter", "importers", ["magnum::trade", "magnum::any_image_importer"])), 
            ("stl_importer", ("stl_importer", "StlImporter", "StlImporter", "importers", ["magnum::mesh_tools", "magnum::trade"])), 
            )
        return [plugin for opt_name, plugin in all_plugins if self.options.get_safe(opt_name)]
