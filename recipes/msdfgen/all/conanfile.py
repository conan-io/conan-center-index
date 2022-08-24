from conans import ConanFile, CMake, tools
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.43.0"


class MsdfgenConan(ConanFile):
    name = "msdfgen"
    description = "Multi-channel signed distance field generator"
    license = "MIT"
    topics = ("msdfgen", "msdf", "shape", "glyph", "font")
    homepage = "https://github.com/Chlumsky/msdfgen"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_openmp": [True, False],
        "with_skia": [True, False],
        "utility": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_openmp": False,
        "with_skia": False,
        "utility": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return str(self.settings.compiler) in ["Visual Studio", "msvc"]

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("freetype/2.11.1")
        self.requires("lodepng/cci.20200615")
        self.requires("tinyxml2/9.0.0")

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)
        if self._is_msvc and self.options.shared:
            raise ConanInvalidConfiguration("msdfgen shared not supported by Visual Studio")
        if self.options.with_skia:
            raise ConanInvalidConfiguration("skia recipe not available yet in CCI")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmakelists = os.path.join(self._source_subfolder, "CMakeLists.txt")
        # unvendor lodepng & tinyxml2
        tools.rmdir(os.path.join(self._source_subfolder, "lib"))
        tools.replace_in_file(cmakelists, "\"lib/*.cpp\"", "")
        tools.replace_in_file(cmakelists,
                              "target_link_libraries(msdfgen-ext PUBLIC msdfgen::msdfgen Freetype::Freetype)",
                              "target_link_libraries(msdfgen-ext PUBLIC msdfgen::msdfgen ${CONAN_LIBS})")
        # very weird but required for Visual Studio when libs are unvendored (at least for Ninja generator)
        if self._is_msvc:
            tools.replace_in_file(cmakelists,
                                  "set_target_properties(msdfgen-standalone PROPERTIES ARCHIVE_OUTPUT_DIRECTORY archive OUTPUT_NAME msdfgen)",
                                  "set_target_properties(msdfgen-standalone PROPERTIES OUTPUT_NAME msdfgen IMPORT_PREFIX foo)")

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["MSDFGEN_BUILD_MSDFGEN_STANDALONE"] = self.options.utility
        self._cmake.definitions["MSDFGEN_USE_OPENMP"] = self.options.with_openmp
        self._cmake.definitions["MSDFGEN_USE_CPP11"] = True
        self._cmake.definitions["MSDFGEN_USE_SKIA"] = self.options.with_skia
        self._cmake.definitions["MSDFGEN_INSTALL"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "msdfgen")
        # Required to avoid some side effect in CMakeDeps generator of downstream recipes
        self.cpp_info.set_property("cmake_target_name", "msdfgen::msdgen-all-unofficial")

        self.cpp_info.names["cmake_find_package"] = "msdfgen"
        self.cpp_info.names["cmake_find_package_multi"] = "msdfgen"

        includedir = os.path.join("include", "msdfgen")

        self.cpp_info.components["_msdfgen"].set_property("cmake_target_name", "msdfgen::msdfgen")
        self.cpp_info.components["_msdfgen"].names["cmake_find_package"] = "msdfgen"
        self.cpp_info.components["_msdfgen"].names["cmake_find_package_multi"] = "msdfgen"
        self.cpp_info.components["_msdfgen"].includedirs.append(includedir)
        self.cpp_info.components["_msdfgen"].libs = ["msdfgen"]
        self.cpp_info.components["_msdfgen"].defines = ["MSDFGEN_USE_CPP11"]

        self.cpp_info.components["msdfgen-ext"].set_property("cmake_target_name", "msdfgen::msdfgen-ext")
        self.cpp_info.components["msdfgen-ext"].names["cmake_find_package"] = "msdfgen-ext"
        self.cpp_info.components["msdfgen-ext"].names["cmake_find_package_multi"] = "msdfgen-ext"
        self.cpp_info.components["msdfgen-ext"].includedirs.append(includedir)
        self.cpp_info.components["msdfgen-ext"].libs = ["msdfgen-ext"]
        self.cpp_info.components["msdfgen-ext"].requires = [
            "_msdfgen", "freetype::freetype",
            "lodepng::lodepng", "tinyxml2::tinyxml2",
        ]
        if self.options.with_skia:
            self.cpp_info.components["msdfgen-ext"].defines.append("MSDFGEN_USE_SKIA")

        if self.options.utility:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
