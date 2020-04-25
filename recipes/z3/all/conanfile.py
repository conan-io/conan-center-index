from conans import CMake, ConanFile, tools
import os


class Z3Conan(ConanFile):
    name = "z3"
    description = "The Z3 Theorem Prover"
    topics = ("conan", "z3", "theorem", "SMT", "satisfiability", "prover", "solver")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Z3Prover/z3"
    exports_sources = "CMakeLists.txt"
    generators = "cmake"
    license = "MIT"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "multithreaded": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "multithreaded": True,
    }

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

    def requirements(self):
        self.requires("mpir/3.0.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("{0}-{0}-{1}".format(self.name, self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["Z3_USE_LIB_GMP"] = True
        self._cmake.definitions["SINGLE_THREADED"] = not self.options.multithreaded
        self._cmake.definitions["Z3_BUILD_LIBZ3_SHARED"] = self.options.shared
        self._cmake.definitions["Z3_INCLUDE_GIT_HASH"] = False
        self._cmake.definitions["Z3_INCLUDE_GIT_DESCRIBE"] = False
        self._cmake.definitions["Z3_ENABLE_EXAMPLE_TARGETS"] = False
        self._cmake.definitions["Z3_BUILD_DOCUMENTATION"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.txt", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.libs = ["libz3" if self.settings.os == "Windows" else "z3"]
        if self.settings.os in ("Linux",):
            self.cpp_info.system_libs.append("pthread")

        # FIXME: name of imported CMake target is z3::libz3 (no capitals)
        self.cpp_info.names["cmake_find_package"] = "Z3"
        self.cpp_info.names["cmake_find_package_multi"] = "Z3"
