from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os


class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mongocxx.org"
    description = "C++ Driver for MongoDB"
    topics = ("conan", "libbsoncxx", "libmongocxx", "mongo", "mongodb", "database", "db")
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**", "Find*.cmake"]
    generators = ("cmake", "cmake_find_package")
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "polyfill": ["std", "boost", "mnmlstc", "experimental"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "polyfill": "boost"
    }
    requires = "mongo-c-driver/1.17.2"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def configure(self):
        if self.settings.compiler == "Visual Studio" and self.options.polyfill != "boost":
            raise ConanInvalidConfiguration("For MSVC, best to use the boost polyfill")

        tools.check_min_cppstd(self, "11")

        if self.options.polyfill == "std":
            tools.check_min_cppstd(self, "17")

        if self.options.polyfill == "boost":
            self.requires("boost/1.74.0")

        # Cannot model mnmlstc (not packaged, is pulled dynamically) or
        # std::experimental (how to check availability in stdlib?) polyfill
        # dependencies

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-r" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BSONCXX_POLY_USE_MNMLSTC"] = self.options.polyfill == "mnmlstc"
        self._cmake.definitions["BSONCXX_POLY_USE_STD_EXPERIMENTAL"] = self.options.polyfill == "experimental"
        self._cmake.definitions["BSONCXX_POLY_USE_BOOST"] = self.options.polyfill == "boost"
        self._cmake.definitions["BUILD_VERSION"] = self.version
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        if self.settings.compiler == "Visual Studio":
            cmake_file = os.path.join(self._source_subfolder, "../CMakeLists.txt")
            tools.replace_in_file(
                cmake_file,
                'add_subdirectory("source_subfolder")',
                'add_subdirectory("source_subfolder")\nadd_definitions(-D_ENABLE_EXTENDED_ALIGNED_STORAGE)'
            )

        self._patch_sources()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="THIRD-PARTY-NOTICES", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # Need to ensure mongocxx is linked before bsoncxx
        self.cpp_info.libs = sorted(tools.collect_libs(self), reverse=True)
        self.cpp_info.includedirs.extend([os.path.join("include", lib, "v_noabi") for lib in ["bsoncxx", "mongocxx"]])

        if self.options.polyfill == "mnmlstc":
            self.cpp_info.includedirs.append(os.path.join("include", "bsoncxx", "third_party", "mnmlstc"))

        if not self.options.shared:
            self.cpp_info.defines.extend(["BSONCXX_STATIC", "MONGOCXX_STATIC"])
