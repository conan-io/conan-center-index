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

        "assimpimporter": [True, False],
        "basisimageconverter": [True, False],
        "basisimporter": [True, False],
        "ddsimporter": [True, False],
        "devilimageimporter": [True, False],
        "drflacaudioimporter": [True, False],
        "drmp3audioimporter": [True, False],
        "drwavaudioimporter": [True, False],
        "faad2audioimporter": [True, False],
        "freetypefont": [True, False],
        "harfbuzzfont": [True, False],
        "icoimporter": [True, False],
        "jpegimageconverter": [True, False],
        "jpegimporter": [True, False],
        "meshoptimizersceneconverter": [True, False],
        "miniexrimageconverter": [True, False],
        "opengeximporter": [True, False],
        "pngimageconverter": [True, False],
        "pngimporter": [True, False],
        "primitiveimporter": [True, False],
        "stanfordimporter": [True, False],
        "stanfordsceneconverter": [True, False],
        "stbimageconverter": [True, False],
        "stbimageimporter": [True, False],
        "stbtruetypefont": [True, False],
        "stbvorbisaudioimporter": [True, False],
        "stlimporter": [True, False],
        "tinygltfimporter": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "shared_plugins": True,
        
        "assimpimporter": True,
        "basisimageconverter": False,
        "basisimporter": False,
        "ddsimporter": True,
        "devilimageimporter": False,
        "drflacaudioimporter": True,
        "drmp3audioimporter": True,
        "drwavaudioimporter": True,
        "faad2audioimporter": False,
        "freetypefont": True,
        "harfbuzzfont": True,
        "icoimporter": True,
        "jpegimageconverter": True,
        "jpegimporter": True,
        "meshoptimizersceneconverter": True,
        "miniexrimageconverter": True,
        "opengeximporter": True,
        "pngimageconverter": True,
        "pngimporter": True,
        "primitiveimporter": True,
        "stanfordimporter": True,
        "stanfordsceneconverter": True,
        "stbimageconverter": True,
        "stbimageimporter": True,
        "stbtruetypefont": True,
        "stbvorbisaudioimporter": True,
        "stlimporter": True,
        "tinygltfimporter": True,
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
        if self.options.assimpimporter:
            self.requires("assimp/5.0.1")
        if self.options.harfbuzzfont:
            self.requires("harfbuzz/2.8.2")
        if self.options.jpegimporter or self.options.jpegimageconverter:
            self.requires("libjpeg/9d")
        if self.options.meshoptimizersceneconverter:
            self.requires("meshoptimizer/0.15")
        if self.options.basisimageconverter or self.options.basisimporter:
            raise ConanInvalidConfiguration("Requires 'basisuniversal', not available in ConanCenter yet")
        if self.options.devilimageimporter:
            raise ConanInvalidConfiguration("Requires 'DevIL', not available in ConanCenter yet")
        if self.options.faad2audioimporter:
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

        self._cmake.definitions["WITH_ASSIMPIMPORTER"] = self.options.assimpimporter
        self._cmake.definitions["WITH_BASISIMAGECONVERTER"] = self.options.basisimageconverter
        self._cmake.definitions["WITH_BASISIMPORTER"] = self.options.basisimporter
        self._cmake.definitions["WITH_DDSIMPORTER"] = self.options.ddsimporter
        self._cmake.definitions["WITH_DEVILIMAGEIMPORTER"] = self.options.devilimageimporter
        self._cmake.definitions["WITH_DRFLACAUDIOIMPORTER"] = self.options.drflacaudioimporter
        self._cmake.definitions["WITH_DRMP3AUDIOIMPORTER"] = self.options.drmp3audioimporter
        self._cmake.definitions["WITH_DRWAVAUDIOIMPORTER"] = self.options.drwavaudioimporter
        self._cmake.definitions["WITH_FAAD2AUDIOIMPORTER"] = self.options.faad2audioimporter
        self._cmake.definitions["WITH_FREETYPEFONT"] = self.options.freetypefont
        self._cmake.definitions["WITH_HARFBUZZFONT"] = self.options.harfbuzzfont
        self._cmake.definitions["WITH_ICOIMPORTER"] = self.options.icoimporter
        self._cmake.definitions["WITH_JPEGIMAGECONVERTER"] = self.options.jpegimageconverter
        self._cmake.definitions["WITH_JPEGIMPORTER"] = self.options.jpegimporter
        self._cmake.definitions["WITH_MESHOPTIMIZERSCENECONVERTER"] = self.options.meshoptimizersceneconverter
        self._cmake.definitions["WITH_MINIEXRIMAGECONVERTER"] = self.options.miniexrimageconverter
        self._cmake.definitions["WITH_OPENGEXIMPORTER"] = self.options.opengeximporter
        self._cmake.definitions["WITH_PNGIMAGECONVERTER"] = self.options.pngimageconverter
        self._cmake.definitions["WITH_PNGIMPORTER"] = self.options.pngimporter
        self._cmake.definitions["WITH_PRIMITIVEIMPORTER"] = self.options.primitiveimporter
        self._cmake.definitions["WITH_STANFORDIMPORTER"] = self.options.stanfordimporter
        self._cmake.definitions["WITH_STANFORDSCENECONVERTER"] = self.options.stanfordsceneconverter
        self._cmake.definitions["WITH_STBIMAGECONVERTER"] = self.options.stbimageconverter
        self._cmake.definitions["WITH_STBIMAGEIMPORTER"] = self.options.stbimageimporter
        self._cmake.definitions["WITH_STBTRUETYPEFONT"] = self.options.stbtruetypefont
        self._cmake.definitions["WITH_STBVORBISAUDIOIMPORTER"] = self.options.stbvorbisaudioimporter
        self._cmake.definitions["WITH_STLIMPORTER"] = self.options.stlimporter
        self._cmake.definitions["WITH_TINYGLTFIMPORTER"] = self.options.tinygltfimporter

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
        if self.options.assimpimporter:
            self.cpp_info.components["assimpimporter"].names["cmake_find_package"] = "AssimpImporter"
            self.cpp_info.components["assimpimporter"].names["cmake_find_package_multi"] = "AssimpImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["assimpimporter"].libs = ["AssimpImporter"]
                self.cpp_info.components["assimpimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["assimpimporter"].requires = ["magnum::trade", "assimp::assimp"]

        if self.options.basisimageconverter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.basisimporter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.ddsimporter:
            self.cpp_info.components["ddsimporter"].names["cmake_find_package"] = "DdsImporter"
            self.cpp_info.components["ddsimporter"].names["cmake_find_package_multi"] = "DdsImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["ddsimporter"].libs = ["DdsImporter"]
                self.cpp_info.components["ddsimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["ddsimporter"].requires = ["magnum::trade"]

        if self.options.devilimageimporter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.drflacaudioimporter:
            self.cpp_info.components["drflacaudioimporter"].names["cmake_find_package"] = "DrFlacAudioImporter"
            self.cpp_info.components["drflacaudioimporter"].names["cmake_find_package_multi"] = "DrFlacAudioImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["drflacaudioimporter"].libs = ["DrFlacAudioImporter"]
                self.cpp_info.components["drflacaudioimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "audioimporters")]
            self.cpp_info.components["drflacaudioimporter"].requires = ["magnum::audio"]

        if self.options.drmp3audioimporter:
            self.cpp_info.components["drmp3audioimporter"].names["cmake_find_package"] = "DrMp3AudioImporter"
            self.cpp_info.components["drmp3audioimporter"].names["cmake_find_package_multi"] = "DrMp3AudioImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["drmp3audioimporter"].libs = ["DrMp3AudioImporter"]
                self.cpp_info.components["drmp3audioimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "audioimporters")]
            self.cpp_info.components["drmp3audioimporter"].requires = ["magnum::audio"]

        if self.options.drwavaudioimporter:
            self.cpp_info.components["drwavaudioimporter"].names["cmake_find_package"] = "DrWavAudioImporter"
            self.cpp_info.components["drwavaudioimporter"].names["cmake_find_package_multi"] = "DrWavAudioImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["drwavaudioimporter"].libs = ["DrWavAudioImporter"]
                self.cpp_info.components["drwavaudioimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "audioimporters")]
            self.cpp_info.components["drwavaudioimporter"].requires = ["magnum::audio"]

        if self.options.faad2audioimporter:
            raise ConanException("Component not defined, please contribute it to the Conan recipe")

        if self.options.freetypefont:
            self.cpp_info.components["freetypefont"].names["cmake_find_package"] = "FreeTypeFont"
            self.cpp_info.components["freetypefont"].names["cmake_find_package_multi"] = "FreeTypeFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["freetypefont"].libs = ["FreeTypeFont"]
                self.cpp_info.components["freetypefont"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "fonts")]
            self.cpp_info.components["freetypefont"].requires = ["magnum::text"]

        if self.options.harfbuzzfont:
            self.cpp_info.components["harfbuzzfont"].names["cmake_find_package"] = "HarfBuzzFont"
            self.cpp_info.components["harfbuzzfont"].names["cmake_find_package_multi"] = "HarfBuzzFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["harfbuzzfont"].libs = ["HarfBuzzFont"]
                self.cpp_info.components["harfbuzzfont"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "fonts")]
            self.cpp_info.components["harfbuzzfont"].requires = ["magnum::text", "harfbuzz::harfbuzz"]

        if self.options.jpegimageconverter:
            self.cpp_info.components["jpegimageconverter"].names["cmake_find_package"] = "JpegImageConverter"
            self.cpp_info.components["jpegimageconverter"].names["cmake_find_package_multi"] = "JpegImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["jpegimageconverter"].libs = ["JpegImageConverter"]
                self.cpp_info.components["jpegimageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["jpegimageconverter"].requires = ["magnum::trade", "libjpeg::libjpeg"]

        if self.options.jpegimporter:
            self.cpp_info.components["jpegimporter"].names["cmake_find_package"] = "JpegImporter"
            self.cpp_info.components["jpegimporter"].names["cmake_find_package_multi"] = "JpegImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["jpegimporter"].libs = ["JpegImporter"]
                self.cpp_info.components["jpegimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["jpegimporter"].requires = ["magnum::trade", "libjpeg::libjpeg"]

        if self.options.meshoptimizersceneconverter:
            self.cpp_info.components["meshoptimizersceneconverter"].names["cmake_find_package"] = "MeshOptimizerSceneConverter"
            self.cpp_info.components["meshoptimizersceneconverter"].names["cmake_find_package_multi"] = "MeshOptimizerSceneConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["meshoptimizersceneconverter"].libs = ["MeshOptimizerSceneConverter"]
                self.cpp_info.components["meshoptimizersceneconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "sceneconverters")]
            self.cpp_info.components["meshoptimizersceneconverter"].requires = ["magnum::trade", "magnum::meshtools", "meshoptimizer::meshoptimizer"]

        if self.options.miniexrimageconverter:
            self.cpp_info.components["miniexrimageconverter"].names["cmake_find_package"] = "MiniExrImageConverter"
            self.cpp_info.components["miniexrimageconverter"].names["cmake_find_package_multi"] = "MiniExrImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["miniexrimageconverter"].libs = ["MiniExrImageConverter"]
                self.cpp_info.components["miniexrimageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["miniexrimageconverter"].requires = ["magnum::trade"]

        if self.options.opengeximporter:
            self.cpp_info.components["opengeximporter"].names["cmake_find_package"] = "OpenGexImporter"
            self.cpp_info.components["opengeximporter"].names["cmake_find_package_multi"] = "OpenGexImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["opengeximporter"].libs = ["OpenGexImporter"]
                self.cpp_info.components["opengeximporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["opengeximporter"].requires = ["magnum::trade", "magnumopenddl"]
            if not self.options["magnum"].shared_plugins:
                self.cpp_info.components["opengeximporter"].requires = ["magnum::anyimageimporter"]

        if self.options.pngimporter:
            self.cpp_info.components["pngimporter"].names["cmake_find_package"] = "PngImporter"
            self.cpp_info.components["pngimporter"].names["cmake_find_package_multi"] = "PngImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["pngimporter"].libs = ["PngImporter"]
                self.cpp_info.components["pngimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["pngimporter"].requires = ["magnum::trade"]

        if self.options.pngimageconverter:
            self.cpp_info.components["pngimageconverter"].names["cmake_find_package"] = "PngImageConverter"
            self.cpp_info.components["pngimageconverter"].names["cmake_find_package_multi"] = "PngImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["pngimageconverter"].libs = ["PngImageConverter"]
                self.cpp_info.components["pngimageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["pngimageconverter"].requires = ["magnum::trade"]

        if self.options.primitiveimporter:
            self.cpp_info.components["primitiveimporter"].names["cmake_find_package"] = "PrimitiveImporter"
            self.cpp_info.components["primitiveimporter"].names["cmake_find_package_multi"] = "PrimitiveImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["primitiveimporter"].libs = ["PrimitiveImporter"]
                self.cpp_info.components["primitiveimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["primitiveimporter"].requires = ["magnum::primitives", "magnum::trade"]

        if self.options.stanfordimporter:
            self.cpp_info.components["stanfordimporter"].names["cmake_find_package"] = "StandfordImporter"
            self.cpp_info.components["stanfordimporter"].names["cmake_find_package_multi"] = "StandfordImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stanfordimporter"].libs = ["StandfordImporter"]
                self.cpp_info.components["stanfordimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["stanfordimporter"].requires = ["magnum::meshtools", "magnum::trade"]

        if self.options.stanfordsceneconverter:
            self.cpp_info.components["stanfordsceneconverter"].names["cmake_find_package"] = "StandfordSceneConverter"
            self.cpp_info.components["stanfordsceneconverter"].names["cmake_find_package_multi"] = "StandfordSceneConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stanfordsceneconverter"].libs = ["StandfordSceneConverter"]
                self.cpp_info.components["stanfordsceneconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "sceneconverters")]
            self.cpp_info.components["stanfordsceneconverter"].requires = ["magnum::meshtools", "magnum::trade"]

        if self.options.stbimageconverter:
            self.cpp_info.components["stbimageconverter"].names["cmake_find_package"] = "StbImageConverter"
            self.cpp_info.components["stbimageconverter"].names["cmake_find_package_multi"] = "StbImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stbimageconverter"].libs = ["StbImageConverter"]
                self.cpp_info.components["stbimageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["stbimageconverter"].requires = ["magnum::trade"]

        if self.options.stbimageimporter:
            self.cpp_info.components["stbimageimporter"].names["cmake_find_package"] = "StbImageImporter"
            self.cpp_info.components["stbimageimporter"].names["cmake_find_package_multi"] = "StbImageImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stbimageimporter"].libs = ["StbImageImporter"]
                self.cpp_info.components["stbimageimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["stbimageimporter"].requires = ["magnum::trade"]

        if self.options.stbtruetypefont:
            self.cpp_info.components["stbtruetypefont"].names["cmake_find_package"] = "StbTrueTypeFont"
            self.cpp_info.components["stbtruetypefont"].names["cmake_find_package_multi"] = "StbTrueTypeFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["stbtruetypefont"].libs = ["StbTrueTypeFont"]
                self.cpp_info.components["stbtruetypefont"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "fonts")]
            self.cpp_info.components["stbtruetypefont"].requires = ["magnum::text"]

        if self.options.stlimporter:
            self.cpp_info.components["stlimporter"].names["cmake_find_package"] = "StlImporter"
            self.cpp_info.components["stlimporter"].names["cmake_find_package_multi"] = "StlImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stlimporter"].libs = ["StlImporter"]
                self.cpp_info.components["stlimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["stlimporter"].requires = ["magnum::meshtools", "magnum::trade"]

        if self.options.stbvorbisaudioimporter:
            self.cpp_info.components["stbvorbisaudioimporter"].names["cmake_find_package"] = "StbVorbisAudioImporter"
            self.cpp_info.components["stbvorbisaudioimporter"].names["cmake_find_package_multi"] = "StbVorbisAudioImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stbvorbisaudioimporter"].libs = ["StbVorbisAudioImporter"]
                self.cpp_info.components["stbvorbisaudioimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "audioimporters")]
            self.cpp_info.components["stbvorbisaudioimporter"].requires = ["magnum::audio"]

        if self.options.tinygltfimporter:
            self.cpp_info.components["tinygltfimporter"].names["cmake_find_package"] = "TinyGltfImporter"
            self.cpp_info.components["tinygltfimporter"].names["cmake_find_package_multi"] = "TinyGltfImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["tinygltfimporter"].libs = ["TinyGltfImporter"]
                self.cpp_info.components["tinygltfimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["tinygltfimporter"].requires = ["magnum::trade", "magnum::anyimageimporter"]
