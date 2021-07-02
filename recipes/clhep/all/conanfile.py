import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class ClhepConan(ConanFile):
    name = "clhep"
    description = "Class Library for High Energy Physics."
    license = "LGPL-3.0-only"
    topics = ("conan", "clhep", "cern", "hep", "high energy", "physics", "geometry", "algebra")
    homepage = "http://proj-clhep.web.cern.ch/proj-clhep"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    short_paths = True
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)
        if self.settings.compiler == "Visual Studio" and self.options.shared:
            raise ConanInvalidConfiguration("CLHEP doesn't properly build its shared libs with Visual Studio")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.version, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CLHEP_SINGLE_THREAD"] = False
        self._cmake.definitions["CLHEP_BUILD_DOCS"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy(pattern="COPYING*", dst="licenses", src=os.path.join(self._source_subfolder, "CLHEP"))
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "CLHEP"
        self.cpp_info.names["cmake_find_package_multi"] = "CLHEP"
        self.cpp_info.names["pkg_config"] = "clhep"
        # Vector
        vector_cmake = "Vector" if self.options.shared else "VectorS"
        self.cpp_info.components["vector"].names["cmake_find_package"] = vector_cmake
        self.cpp_info.components["vector"].names["cmake_find_package_multi"] = vector_cmake
        self.cpp_info.components["vector"].names["pkg_config"] = "clhep-vector"
        self.cpp_info.components["vector"].libs = ["CLHEP-Vector-" + self.version]
        if self.settings.os == "Linux":
            self.cpp_info.components["vector"].system_libs = ["m", "pthread"]
        # Evaluator
        evaluator_cmake = "Evaluator" if self.options.shared else "EvaluatorS"
        self.cpp_info.components["evaluator"].names["cmake_find_package"] = evaluator_cmake
        self.cpp_info.components["evaluator"].names["cmake_find_package_multi"] = evaluator_cmake
        self.cpp_info.components["evaluator"].names["pkg_config"] = "clhep-evaluator"
        self.cpp_info.components["evaluator"].libs = ["CLHEP-Evaluator-" + self.version]
        if self.settings.os == "Linux":
            self.cpp_info.components["evaluator"].system_libs = ["m", "pthread"]
        # GenericFunctions
        genericfunctions_cmake = "GenericFunctions" if self.options.shared else "GenericFunctionsS"
        self.cpp_info.components["genericfunctions"].names["cmake_find_package"] = genericfunctions_cmake
        self.cpp_info.components["genericfunctions"].names["cmake_find_package_multi"] = genericfunctions_cmake
        self.cpp_info.components["genericfunctions"].names["pkg_config"] = "clhep-genericfunctions"
        self.cpp_info.components["genericfunctions"].libs = ["CLHEP-GenericFunctions-" + self.version]
        if self.settings.os == "Linux":
            self.cpp_info.components["genericfunctions"].system_libs = ["m", "pthread"]
        # Geometry
        geometry_cmake = "Geometry" if self.options.shared else "GeometryS"
        self.cpp_info.components["geometry"].names["cmake_find_package"] = geometry_cmake
        self.cpp_info.components["geometry"].names["cmake_find_package_multi"] = geometry_cmake
        self.cpp_info.components["geometry"].names["pkg_config"] = "clhep-geometry"
        self.cpp_info.components["geometry"].libs = ["CLHEP-Geometry-" + self.version]
        if self.settings.os == "Linux":
            self.cpp_info.components["geometry"].system_libs = ["m", "pthread"]
        self.cpp_info.components["geometry"].requires = ["vector"]
        # Random
        random_cmake = "Random" if self.options.shared else "RandomS"
        self.cpp_info.components["random"].names["cmake_find_package"] = random_cmake
        self.cpp_info.components["random"].names["cmake_find_package_multi"] = random_cmake
        self.cpp_info.components["random"].names["pkg_config"] = "clhep-random"
        self.cpp_info.components["random"].libs = ["CLHEP-Random-" + self.version]
        if self.settings.os == "Linux":
            self.cpp_info.components["random"].system_libs = ["m", "pthread"]
        # Matrix
        matrix_cmake = "Matrix" if self.options.shared else "MatrixS"
        self.cpp_info.components["matrix"].names["cmake_find_package"] = matrix_cmake
        self.cpp_info.components["matrix"].names["cmake_find_package_multi"] = matrix_cmake
        self.cpp_info.components["matrix"].names["pkg_config"] = "clhep-matrix"
        self.cpp_info.components["matrix"].libs = ["CLHEP-Matrix-" + self.version]
        if self.settings.os == "Linux":
            self.cpp_info.components["matrix"].system_libs = ["m", "pthread"]
        self.cpp_info.components["matrix"].requires = ["random", "vector"]
        # RandomObjects
        randomobjects_cmake = "RandomObjects" if self.options.shared else "RandomObjectsS"
        self.cpp_info.components["randomobjects"].names["cmake_find_package"] = randomobjects_cmake
        self.cpp_info.components["randomobjects"].names["cmake_find_package_multi"] = randomobjects_cmake
        self.cpp_info.components["randomobjects"].names["pkg_config"] = "clhep-randomobjects"
        self.cpp_info.components["randomobjects"].libs = ["CLHEP-RandomObjects-" + self.version]
        if self.settings.os == "Linux":
            self.cpp_info.components["randomobjects"].system_libs = ["m"]
        self.cpp_info.components["randomobjects"].requires = ["random", "matrix", "vector"]
        # Cast
        cast_cmake = "Cast" if self.options.shared else "CastS"
        self.cpp_info.components["cast"].names["cmake_find_package"] = cast_cmake
        self.cpp_info.components["cast"].names["cmake_find_package_multi"] = cast_cmake
        self.cpp_info.components["cast"].names["pkg_config"] = "clhep-cast"
        self.cpp_info.components["cast"].libs = ["CLHEP-Cast-" + self.version]
        if self.settings.os == "Linux":
            self.cpp_info.components["cast"].system_libs = ["pthread"]
        # RefCount
        refcount_cmake = "RefCount" if self.options.shared else "RefCountS"
        self.cpp_info.components["refcount"].names["cmake_find_package"] = refcount_cmake
        self.cpp_info.components["refcount"].names["cmake_find_package_multi"] = refcount_cmake
        self.cpp_info.components["refcount"].names["pkg_config"] = "clhep-refcount"
        self.cpp_info.components["refcount"].libs = ["CLHEP-RefCount-" + self.version]
        if self.settings.os == "Linux":
            self.cpp_info.components["refcount"].system_libs = ["pthread"]
        # Exceptions
        exceptions_cmake = "Exceptions" if self.options.shared else "ExceptionsS"
        self.cpp_info.components["exceptions"].names["cmake_find_package"] = exceptions_cmake
        self.cpp_info.components["exceptions"].names["cmake_find_package_multi"] = exceptions_cmake
        self.cpp_info.components["exceptions"].names["pkg_config"] = "clhep-exceptions"
        self.cpp_info.components["exceptions"].libs = ["CLHEP-Exceptions-" + self.version]
        self.cpp_info.components["exceptions"].requires = ["cast", "refcount"]
        # CLHEP (global imported target including all CLHEP components)
        global_cmake = "CLHEP" if self.options.shared else "CLHEPS"
        self.cpp_info.components["clheplib"].names["cmake_find_package"] = global_cmake
        self.cpp_info.components["clheplib"].names["cmake_find_package_multi"] = global_cmake
        self.cpp_info.components["clheplib"].requires = [
            "vector", "evaluator", "genericfunctions", "geometry", "random",
            "matrix", "randomobjects", "cast", "refcount", "exceptions"
        ]
