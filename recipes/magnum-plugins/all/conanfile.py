from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class MagnumConan(ConanFile):
    name = "magnum-plugins"
    description = "Plugins for the Magnum C++11/C++14 graphics engine"
    license = "MIT"
    topics = ("conan", "magnum", "graphics", "rendering", "3d", "2d", "opengl")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://magnum.graphics"

    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "shared_plugins": [True, False],

        "with_assimpimporter": [True, False],
        "with_basisimageconverter": [True, False],
        "with_basisimporter": [True, False],
        "with_ddsimporter": [True, False],
        "with_devilimageimporter": [True, False],
        "with_drflacaudioimporter": [True, False],
        "with_drmp3audioimporter": [True, False],
        "with_drwavaudioimporter": [True, False],
        "with_faad2audioimporter": [True, False],
        "with_freetypefont": [True, False],
        "with_harfbuzzfont": [True, False],
        "with_icoimporter": [True, False],
        "with_jpegimageconverter": [True, False],
        "with_jpegimporter": [True, False],
        "with_meshoptimizersceneconverter": [True, False],
        "with_miniexrimageconverter": [True, False],
        "with_opengeximporter": [True, False],
        "with_pngimageconverter": [True, False],
        "with_pngimporter": [True, False],
        "with_primitiveimporter": [True, False],
        "with_stanfordimporter": [True, False],
        "with_stanfordsceneconverter": [True, False],
        "with_stbimageconverter": [True, False],
        "with_stbimageimporter": [True, False],
        "with_stbtruetypefont": [True, False],
        "with_stbvorbisaudioimporter": [True, False],
        "with_stlimporter": [True, False],
        "with_tinygltfimporter": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "shared_plugins": True,
        
        "with_assimpimporter": True,
        "with_basisimageconverter": False,
        "with_basisimporter": False,
        "with_ddsimporter": True,
        "with_devilimageimporter": False,
        "with_drflacaudioimporter": False,
        "with_drmp3audioimporter": False,
        "with_drwavaudioimporter": False,
        "with_faad2audioimporter": False,
        "with_freetypefont": True,
        "with_harfbuzzfont": True,
        "with_icoimporter": True,
        "with_jpegimageconverter": True,
        "with_jpegimporter": True,
        "with_meshoptimizersceneconverter": True,
        "with_miniexrimageconverter": True,
        "with_opengeximporter": True,
        "with_pngimageconverter": True,
        "with_pngimporter": True,
        "with_primitiveimporter": True,
        "with_stanfordimporter": True,
        "with_stanfordsceneconverter": True,
        "with_stbimageconverter": True,
        "with_stbimageimporter": True,
        "with_stbtruetypefont": True,
        "with_stbvorbisaudioimporter": False,
        "with_stlimporter": True,
        "with_tinygltfimporter": True,
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
        if self.options.with_assimpimporter:
            self.requires("assimp/5.0.1")
        if self.options.with_harfbuzzfont:
            self.requires("harfbuzz/2.8.2")
        if self.options.with_jpegimporter or self.options.with_jpegimageconverter:
            self.requires("libjpeg/9d")
        if self.options.with_meshoptimizersceneconverter:
            self.requires("meshoptimizer/0.15")

    #def build_requirements(self):
    #    self.build_requires("corrade/{}".format(self.version))

    def validate(self):
        if not self.options["magnum"].with_trade:
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

        self._cmake.definitions["WITH_ASSIMPIMPORTER"] = self.options.with_assimpimporter
        self._cmake.definitions["WITH_BASISIMAGECONVERTER"] = self.options.with_basisimageconverter
        self._cmake.definitions["WITH_BASISIMPORTER"] = self.options.with_basisimporter
        self._cmake.definitions["WITH_DDSIMPORTER"] = self.options.with_ddsimporter
        self._cmake.definitions["WITH_DEVILIMAGEIMPORTER"] = self.options.with_devilimageimporter
        self._cmake.definitions["WITH_DRFLACAUDIOIMPORTER"] = self.options.with_drflacaudioimporter
        self._cmake.definitions["WITH_DRMP3AUDIOIMPORTER"] = self.options.with_drmp3audioimporter
        self._cmake.definitions["WITH_DRWAVAUDIOIMPORTER"] = self.options.with_drwavaudioimporter
        self._cmake.definitions["WITH_FAAD2AUDIOIMPORTER"] = self.options.with_faad2audioimporter
        self._cmake.definitions["WITH_FREETYPEFONT"] = self.options.with_freetypefont
        self._cmake.definitions["WITH_HARFBUZZFONT"] = self.options.with_harfbuzzfont
        self._cmake.definitions["WITH_ICOIMPORTER"] = self.options.with_icoimporter
        self._cmake.definitions["WITH_JPEGIMAGECONVERTER"] = self.options.with_jpegimageconverter
        self._cmake.definitions["WITH_JPEGIMPORTER"] = self.options.with_jpegimporter
        self._cmake.definitions["WITH_MESHOPTIMIZERSCENECONVERTER"] = self.options.with_meshoptimizersceneconverter
        self._cmake.definitions["WITH_MINIEXRIMAGECONVERTER"] = self.options.with_miniexrimageconverter
        self._cmake.definitions["WITH_OPENGEXIMPORTER"] = self.options.with_opengeximporter
        self._cmake.definitions["WITH_PNGIMAGECONVERTER"] = self.options.with_pngimageconverter
        self._cmake.definitions["WITH_PNGIMPORTER"] = self.options.with_pngimporter
        self._cmake.definitions["WITH_PRIMITIVEIMPORTER"] = self.options.with_primitiveimporter
        self._cmake.definitions["WITH_STANFORDIMPORTER"] = self.options.with_stanfordimporter
        self._cmake.definitions["WITH_STANFORDSCENECONVERTER"] = self.options.with_stanfordsceneconverter
        self._cmake.definitions["WITH_STBIMAGECONVERTER"] = self.options.with_stbimageconverter
        self._cmake.definitions["WITH_STBIMAGEIMPORTER"] = self.options.with_stbimageimporter
        self._cmake.definitions["WITH_STBTRUETYPEFONT"] = self.options.with_stbtruetypefont
        self._cmake.definitions["WITH_STBVORBISAUDIOIMPORTER"] = self.options.with_stbvorbisaudioimporter
        self._cmake.definitions["WITH_STLIMPORTER"] = self.options.with_stlimporter
        self._cmake.definitions["WITH_TINYGLTFIMPORTER"] = self.options.with_tinygltfimporter

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

        #tools.rmdir(os.path.join(self.package_folder, "cmake"))
        #tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        #tools.rmdir(os.path.join(self.package_folder, "share"))

        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "MagnumPlugins"
        self.cpp_info.names["cmake_find_package_multi"] = "MagnumPlugins"

        self.cpp_info.components["magnumopenddl"].names["cmake_find_package"] = "MagnumOpenDdl"
        self.cpp_info.components["magnumopenddl"].names["cmake_find_package_multi"] = "MagnumOpenDdl"
        self.cpp_info.components["magnumopenddl"].libs = ["MagnumOpenDdl"]
        self.cpp_info.components["magnumopenddl"].requires = ["magnum::magnum"]

        # Plugins
        if self.options.with_assimpimporter:
            self.cpp_info.components["assimpimporter"].names["cmake_find_package"] = "AssimpImporter"
            self.cpp_info.components["assimpimporter"].names["cmake_find_package_multi"] = "AssimpImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["assimpimporter"].libs = ["AssimpImporter"]
                self.cpp_info.components["assimpimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["assimpimporter"].requires = ["magnum::trade", "assimp::assimp"]

        if self.options.with_ddsimporter:
            self.cpp_info.components["ddsimporter"].names["cmake_find_package"] = "DdsImporter"
            self.cpp_info.components["ddsimporter"].names["cmake_find_package_multi"] = "DdsImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["ddsimporter"].libs = ["DdsImporter"]
                self.cpp_info.components["ddsimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["ddsimporter"].requires = ["magnum::trade"]

        if self.options.with_freetypefont:
            self.cpp_info.components["freetypefont"].names["cmake_find_package"] = "FreeTypeFont"
            self.cpp_info.components["freetypefont"].names["cmake_find_package_multi"] = "FreeTypeFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["freetypefont"].libs = ["FreeTypeFont"]
                self.cpp_info.components["freetypefont"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "fonts")]
            self.cpp_info.components["freetypefont"].requires = ["magnum::text"]

        if self.options.with_harfbuzzfont:
            self.cpp_info.components["harfbuzzfont"].names["cmake_find_package"] = "HarfBuzzFont"
            self.cpp_info.components["harfbuzzfont"].names["cmake_find_package_multi"] = "HarfBuzzFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["harfbuzzfont"].libs = ["HarfBuzzFont"]
                self.cpp_info.components["harfbuzzfont"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "fonts")]
            self.cpp_info.components["harfbuzzfont"].requires = ["magnum::text", "harfbuzz::harfbuzz"]

        if self.options.with_jpegimageconverter:
            self.cpp_info.components["jpegimageconverter"].names["cmake_find_package"] = "JpegImageConverter"
            self.cpp_info.components["jpegimageconverter"].names["cmake_find_package_multi"] = "JpegImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["jpegimageconverter"].libs = ["JpegImageConverter"]
                self.cpp_info.components["jpegimageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["jpegimageconverter"].requires = ["magnum::trade", "libjpeg::libjpeg"]

        if self.options.with_jpegimporter:
            self.cpp_info.components["jpegimporter"].names["cmake_find_package"] = "JpegImporter"
            self.cpp_info.components["jpegimporter"].names["cmake_find_package_multi"] = "JpegImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["jpegimporter"].libs = ["JpegImporter"]
                self.cpp_info.components["jpegimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["jpegimporter"].requires = ["magnum::trade", "libjpeg::libjpeg"]

        if self.options.with_meshoptimizersceneconverter:
            self.cpp_info.components["meshoptimizersceneconverter"].names["cmake_find_package"] = "MeshOptimizerSceneConverter"
            self.cpp_info.components["meshoptimizersceneconverter"].names["cmake_find_package_multi"] = "MeshOptimizerSceneConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["meshoptimizersceneconverter"].libs = ["MeshOptimizerSceneConverter"]
                self.cpp_info.components["meshoptimizersceneconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "sceneconverters")]
            self.cpp_info.components["meshoptimizersceneconverter"].requires = ["magnum::trade", "magnum::meshtools", "meshoptimizer::meshoptimizer"]

        if self.options.with_miniexrimageconverter:
            self.cpp_info.components["miniexrimageconverter"].names["cmake_find_package"] = "MiniExrImageConverter"
            self.cpp_info.components["miniexrimageconverter"].names["cmake_find_package_multi"] = "MiniExrImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["miniexrimageconverter"].libs = ["MiniExrImageConverter"]
                self.cpp_info.components["miniexrimageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["miniexrimageconverter"].requires = ["magnum::trade"]

        if self.options.with_opengeximporter:
            self.cpp_info.components["opengeximporter"].names["cmake_find_package"] = "OpenGexImporter"
            self.cpp_info.components["opengeximporter"].names["cmake_find_package_multi"] = "OpenGexImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["opengeximporter"].libs = ["OpenGexImporter"]
                self.cpp_info.components["opengeximporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["opengeximporter"].requires = ["magnum::trade", "magnumopenddl"]
            if not self.options["magnum"].shared_plugins:
                self.cpp_info.components["opengeximporter"].requires = ["magnum::anyimageimporter"]

        if self.options.with_pngimporter:
            self.cpp_info.components["pngimporter"].names["cmake_find_package"] = "PngImporter"
            self.cpp_info.components["pngimporter"].names["cmake_find_package_multi"] = "PngImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["pngimporter"].libs = ["PngImporter"]
                self.cpp_info.components["pngimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["pngimporter"].requires = ["magnum::trade"]

        if self.options.with_pngimageconverter:
            self.cpp_info.components["pngimageconverter"].names["cmake_find_package"] = "PngImageConverter"
            self.cpp_info.components["pngimageconverter"].names["cmake_find_package_multi"] = "PngImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["pngimageconverter"].libs = ["PngImageConverter"]
                self.cpp_info.components["pngimageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["pngimageconverter"].requires = ["magnum::trade"]

        if self.options.with_primitiveimporter:
            self.cpp_info.components["primitiveimporter"].names["cmake_find_package"] = "PrimitiveImporter"
            self.cpp_info.components["primitiveimporter"].names["cmake_find_package_multi"] = "PrimitiveImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["primitiveimporter"].libs = ["PrimitiveImporter"]
                self.cpp_info.components["primitiveimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["primitiveimporter"].requires = ["magnum::primitives", "magnum::trade"]

        if self.options.with_stanfordimporter:
            self.cpp_info.components["stanfordimporter"].names["cmake_find_package"] = "StandfordImporter"
            self.cpp_info.components["stanfordimporter"].names["cmake_find_package_multi"] = "StandfordImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stanfordimporter"].libs = ["StandfordImporter"]
                self.cpp_info.components["stanfordimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["stanfordimporter"].requires = ["magnum::meshtools", "magnum::trade"]

        if self.options.with_stanfordsceneconverter:
            self.cpp_info.components["stanfordsceneconverter"].names["cmake_find_package"] = "StandfordSceneConverter"
            self.cpp_info.components["stanfordsceneconverter"].names["cmake_find_package_multi"] = "StandfordSceneConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stanfordsceneconverter"].libs = ["StandfordSceneConverter"]
                self.cpp_info.components["stanfordsceneconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "sceneconverters")]
            self.cpp_info.components["stanfordsceneconverter"].requires = ["magnum::meshtools", "magnum::trade"]

        if self.options.with_stbimageconverter:
            self.cpp_info.components["stbimageconverter"].names["cmake_find_package"] = "StbImageConverter"
            self.cpp_info.components["stbimageconverter"].names["cmake_find_package_multi"] = "StbImageConverter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stbimageconverter"].libs = ["StbImageConverter"]
                self.cpp_info.components["stbimageconverter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "imageconverters")]
            self.cpp_info.components["stbimageconverter"].requires = ["magnum::trade"]

        if self.options.with_stbimageimporter:
            self.cpp_info.components["stbimageimporter"].names["cmake_find_package"] = "StbImageImporter"
            self.cpp_info.components["stbimageimporter"].names["cmake_find_package_multi"] = "StbImageImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stbimageimporter"].libs = ["StbImageImporter"]
                self.cpp_info.components["stbimageimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["stbimageimporter"].requires = ["magnum::trade"]

        if self.options.with_stbtruetypefont:
            self.cpp_info.components["stbtruetypefont"].names["cmake_find_package"] = "StbTrueTypeFont"
            self.cpp_info.components["stbtruetypefont"].names["cmake_find_package_multi"] = "StbTrueTypeFont"
            if not self.options.shared_plugins:
                self.cpp_info.components["stbtruetypefont"].libs = ["StbTrueTypeFont"]
                self.cpp_info.components["stbtruetypefont"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "fonts")]
            self.cpp_info.components["stbtruetypefont"].requires = ["magnum::text"]

        if self.options.with_stlimporter:
            self.cpp_info.components["stlimporter"].names["cmake_find_package"] = "StlImporter"
            self.cpp_info.components["stlimporter"].names["cmake_find_package_multi"] = "StlImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["stlimporter"].libs = ["StlImporter"]
                self.cpp_info.components["stlimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["stlimporter"].requires = ["magnum::meshtools", "magnum::trade"]

        if self.options.with_tinygltfimporter:
            self.cpp_info.components["tinygltfimporter"].names["cmake_find_package"] = "TinyGltfImporter"
            self.cpp_info.components["tinygltfimporter"].names["cmake_find_package_multi"] = "TinyGltfImporter"
            if not self.options.shared_plugins:
                self.cpp_info.components["tinygltfimporter"].libs = ["TinyGltfImporter"]
                self.cpp_info.components["tinygltfimporter"].libdirs = [os.path.join(self.package_folder, "lib", "magnum", "importers")]
            self.cpp_info.components["tinygltfimporter"].requires = ["magnum::trade", "magnum::anyimageimporter"]
