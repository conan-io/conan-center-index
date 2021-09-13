from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

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
    exports_sources = ["CMakeLists.txt", "patches/*"]

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
    
    def requirements(self):
        self.requires("magnum/{}".format(self.version))
        if self.options.assimp_importer:
            self.requires("assimp/5.0.1")
        if self.options.harfbuzz_font:
            self.requires("harfbuzz/2.8.2")
        if self.options.jpeg_importer or self.options.jpeg_imageconverter:
            self.requires("libjpeg/9d")
        if self.options.meshoptimizer_sceneconverter:
            self.requires("meshoptimizer/0.15")
        if self.options.basis_imageconverter or self.options.basis_importer:
            raise ConanInvalidConfiguration("Requires 'basisuniversal', not available in ConanCenter yet")
        if self.options.devil_imageimporter:
            raise ConanInvalidConfiguration("Requires 'DevIL', not available in ConanCenter yet")
        if self.options.faad2_audioimporter:
            raise ConanInvalidConfiguration("Requires 'faad2', not available in ConanCenter yet")

    #def build_requirements(self):
    #    self.build_requires("corrade/{}".format(self.version))

    def validate(self):
        if not self.options["magnum"].trade:
            raise ConanInvalidConfiguration("Magnum Trade is required")

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

        tools.rmdir(os.path.join(self.package_folder, "share"))
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "MagnumPlugins"
        self.cpp_info.names["cmake_find_package_multi"] = "MagnumPlugins"

        self.cpp_info.components["magnumopenddl"].names["cmake_find_package"] = "MagnumOpenDdl"
        self.cpp_info.components["magnumopenddl"].names["cmake_find_package_multi"] = "MagnumOpenDdl"
        self.cpp_info.components["magnumopenddl"].libs = ["MagnumOpenDdl"]
        self.cpp_info.components["magnumopenddl"].requires = ["magnum::magnum"]

        # Plugins
        if self.options.assimp_importer:
            self.cpp_info.components["assimp_importer"].names["cmake_find_package"] = "AssimpImporter"
            self.cpp_info.components["assimp_importer"].names["cmake_find_package_multi"] = "AssimpImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["assimp_importer"].libs = ["AssimpImporter"]
                self.cpp_info.components["assimp_importer"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["assimp_importer"].requires = ["magnum::trade", "assimp::assimp"]

        if self.options.basis_imageconverter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.basis_importer:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.dds_importer:
            self.cpp_info.components["dds_importer"].names["cmake_find_package"] = "DdsImporter"
            self.cpp_info.components["dds_importer"].names["cmake_find_package_multi"] = "DdsImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["dds_importer"].libs = ["DdsImporter"]
                self.cpp_info.components["dds_importer"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["dds_importer"].requires = ["magnum::trade"]

        if self.options.devil_imageimporter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.drflac_audioimporter:
            self.cpp_info.components["drflac_audioimporter"].names["cmake_find_package"] = "DrFlacAudioImporter"
            self.cpp_info.components["drflac_audioimporter"].names["cmake_find_package_multi"] = "DrFlacAudioImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["drflac_audioimporter"].libs = ["DrFlacAudioImporter"]
                self.cpp_info.components["drflac_audioimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "audioimporters")]
            self.cpp_info.components["drflac_audioimporter"].requires = ["magnum::audio"]

        if self.options.drmp3_audioimporter:
            self.cpp_info.components["drmp3_audioimporter"].names["cmake_find_package"] = "DrMp3AudioImporter"
            self.cpp_info.components["drmp3_audioimporter"].names["cmake_find_package_multi"] = "DrMp3AudioImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["drmp3_audioimporter"].libs = ["DrMp3AudioImporter"]
                self.cpp_info.components["drmp3_audioimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "audioimporters")]
            self.cpp_info.components["drmp3_audioimporter"].requires = ["magnum::audio"]

        if self.options.drwav_audioimporter:
            self.cpp_info.components["drwav_audioimporter"].names["cmake_find_package"] = "DrWavAudioImporter"
            self.cpp_info.components["drwav_audioimporter"].names["cmake_find_package_multi"] = "DrWavAudioImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["drwav_audioimporter"].libs = ["DrWavAudioImporter"]
                self.cpp_info.components["drwav_audioimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "audioimporters")]
            self.cpp_info.components["drwav_audioimporter"].requires = ["magnum::audio"]

        if self.options.faad2_audioimporter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.freetype_font:
            self.cpp_info.components["freetype_font"].names["cmake_find_package"] = "FreeTypeFont"
            self.cpp_info.components["freetype_font"].names["cmake_find_package_multi"] = "FreeTypeFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["freetype_font"].libs = ["FreeTypeFont"]
                self.cpp_info.components["freetype_font"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "fonts")]
            self.cpp_info.components["freetype_font"].requires = ["magnum::text"]

        if self.options.harfbuzz_font:
            self.cpp_info.components["harfbuzz_font"].names["cmake_find_package"] = "HarfBuzzFont"
            self.cpp_info.components["harfbuzz_font"].names["cmake_find_package_multi"] = "HarfBuzzFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["harfbuzz_font"].libs = ["HarfBuzzFont"]
                self.cpp_info.components["harfbuzz_font"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "fonts")]
            self.cpp_info.components["harfbuzz_font"].requires = ["magnum::text", "harfbuzz::harfbuzz"]

        if self.options.jpeg_imageconverter:
            self.cpp_info.components["jpeg_imageconverter"].names["cmake_find_package"] = "JpegImageConverter"
            self.cpp_info.components["jpeg_imageconverter"].names["cmake_find_package_multi"] = "JpegImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["jpeg_imageconverter"].libs = ["JpegImageConverter"]
                self.cpp_info.components["jpeg_imageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["jpeg_imageconverter"].requires = ["magnum::trade", "libjpeg::libjpeg"]

        if self.options.jpeg_importer:
            self.cpp_info.components["jpeg_importer"].names["cmake_find_package"] = "JpegImporter"
            self.cpp_info.components["jpeg_importer"].names["cmake_find_package_multi"] = "JpegImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["jpeg_importer"].libs = ["JpegImporter"]
                self.cpp_info.components["jpeg_importer"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["jpeg_importer"].requires = ["magnum::trade", "libjpeg::libjpeg"]

        if self.options.meshoptimizer_sceneconverter:
            self.cpp_info.components["meshoptimizer_sceneconverter"].names["cmake_find_package"] = "MeshOptimizerSceneConverter"
            self.cpp_info.components["meshoptimizer_sceneconverter"].names["cmake_find_package_multi"] = "MeshOptimizerSceneConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["meshoptimizer_sceneconverter"].libs = ["MeshOptimizerSceneConverter"]
                self.cpp_info.components["meshoptimizer_sceneconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "sceneconverters")]
            self.cpp_info.components["meshoptimizer_sceneconverter"].requires = ["magnum::trade", "magnum::meshtools", "meshoptimizer::meshoptimizer"]

        if self.options.miniexr_imageconverter:
            self.cpp_info.components["miniexr_imageconverter"].names["cmake_find_package"] = "MiniExrImageConverter"
            self.cpp_info.components["miniexr_imageconverter"].names["cmake_find_package_multi"] = "MiniExrImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["miniexr_imageconverter"].libs = ["MiniExrImageConverter"]
                self.cpp_info.components["miniexr_imageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["miniexr_imageconverter"].requires = ["magnum::trade"]

        if self.options.opengex_importer:
            self.cpp_info.components["opengex_importer"].names["cmake_find_package"] = "OpenGexImporter"
            self.cpp_info.components["opengex_importer"].names["cmake_find_package_multi"] = "OpenGexImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["opengex_importer"].libs = ["OpenGexImporter"]
                self.cpp_info.components["opengex_importer"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["opengex_importer"].requires = ["magnum::trade", "magnumopenddl"]
            if not self.options["magnum"].shared_plugins:
                self.cpp_info.components["opengex_importer"].requires = ["magnum::anyimageimporter"]

        if self.options.png_importer:
            self.cpp_info.components["png_importer"].names["cmake_find_package"] = "PngImporter"
            self.cpp_info.components["png_importer"].names["cmake_find_package_multi"] = "PngImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["png_importer"].libs = ["PngImporter"]
                self.cpp_info.components["png_importer"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["png_importer"].requires = ["magnum::trade"]

        if self.options.png_imageconverter:
            self.cpp_info.components["png_imageconverter"].names["cmake_find_package"] = "PngImageConverter"
            self.cpp_info.components["png_imageconverter"].names["cmake_find_package_multi"] = "PngImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["png_imageconverter"].libs = ["PngImageConverter"]
                self.cpp_info.components["png_imageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["png_imageconverter"].requires = ["magnum::trade"]

        if self.options.primitive_importer:
            self.cpp_info.components["primitive_importer"].names["cmake_find_package"] = "PrimitiveImporter"
            self.cpp_info.components["primitive_importer"].names["cmake_find_package_multi"] = "PrimitiveImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["primitive_importer"].libs = ["PrimitiveImporter"]
                self.cpp_info.components["primitive_importer"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["primitive_importer"].requires = ["magnum::primitives", "magnum::trade"]

        if self.options.stanford_importer:
            self.cpp_info.components["stanford_importer"].names["cmake_find_package"] = "StandfordImporter"
            self.cpp_info.components["stanford_importer"].names["cmake_find_package_multi"] = "StandfordImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stanford_importer"].libs = ["StandfordImporter"]
                self.cpp_info.components["stanford_importer"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["stanford_importer"].requires = ["magnum::meshtools", "magnum::trade"]

        if self.options.stanford_sceneconverter:
            self.cpp_info.components["stanford_sceneconverter"].names["cmake_find_package"] = "StandfordSceneConverter"
            self.cpp_info.components["stanford_sceneconverter"].names["cmake_find_package_multi"] = "StandfordSceneConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stanford_sceneconverter"].libs = ["StandfordSceneConverter"]
                self.cpp_info.components["stanford_sceneconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "sceneconverters")]
            self.cpp_info.components["stanford_sceneconverter"].requires = ["magnum::meshtools", "magnum::trade"]

        if self.options.stb_imageconverter:
            self.cpp_info.components["stb_imageconverter"].names["cmake_find_package"] = "StbImageConverter"
            self.cpp_info.components["stb_imageconverter"].names["cmake_find_package_multi"] = "StbImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stb_imageconverter"].libs = ["StbImageConverter"]
                self.cpp_info.components["stb_imageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["stb_imageconverter"].requires = ["magnum::trade"]

        if self.options.stb_imageimporter:
            self.cpp_info.components["stb_imageimporter"].names["cmake_find_package"] = "StbImageImporter"
            self.cpp_info.components["stb_imageimporter"].names["cmake_find_package_multi"] = "StbImageImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stb_imageimporter"].libs = ["StbImageImporter"]
                self.cpp_info.components["stb_imageimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["stb_imageimporter"].requires = ["magnum::trade"]

        if self.options.stbtruetype_font:
            self.cpp_info.components["stbtruetype_font"].names["cmake_find_package"] = "StbTrueTypeFont"
            self.cpp_info.components["stbtruetype_font"].names["cmake_find_package_multi"] = "StbTrueTypeFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["stbtruetype_font"].libs = ["StbTrueTypeFont"]
                self.cpp_info.components["stbtruetype_font"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "fonts")]
            self.cpp_info.components["stbtruetype_font"].requires = ["magnum::text"]

        if self.options.stl_importer:
            self.cpp_info.components["stl_importer"].names["cmake_find_package"] = "StlImporter"
            self.cpp_info.components["stl_importer"].names["cmake_find_package_multi"] = "StlImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stl_importer"].libs = ["StlImporter"]
                self.cpp_info.components["stl_importer"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["stl_importer"].requires = ["magnum::meshtools", "magnum::trade"]

        if self.options.stbvorbis_audioimporter:
            self.cpp_info.components["stbvorbis_audioimporter"].names["cmake_find_package"] = "StbVorbisAudioImporter"
            self.cpp_info.components["stbvorbis_audioimporter"].names["cmake_find_package_multi"] = "StbVorbisAudioImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stbvorbis_audioimporter"].libs = ["StbVorbisAudioImporter"]
                self.cpp_info.components["stbvorbis_audioimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "audioimporters")]
            self.cpp_info.components["stbvorbis_audioimporter"].requires = ["magnum::audio"]

        if self.options.tinygltf_importer:
            self.cpp_info.components["tinygltf_importer"].names["cmake_find_package"] = "TinyGltfImporter"
            self.cpp_info.components["tinygltf_importer"].names["cmake_find_package_multi"] = "TinyGltfImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["tinygltf_importer"].libs = ["TinyGltfImporter"]
                self.cpp_info.components["tinygltf_importer"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["tinygltf_importer"].requires = ["magnum::trade", "magnum::anyimageimporter"]
