from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import glob
import shutil


class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mongocxx.org"
    description = "C++ Driver for MongoDB"
    topics = ("conan", "libbsoncxx", "libmongocxx", "mongo", "mongodb", "database", "db")
    settings = "os", "compiler", "arch", "build_type"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = ("cmake", "cmake_find_package")
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "polyfill": ["std", "boost", "mnmlstc", "experimental"],
        "with_ssl": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "polyfill": "boost",
        "with_ssl": True
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

    @property
    def _minimal_std_version(self):
        return "17" if self.options.polyfill == "std" else "11"

    @property
    def _compilers_minimum_version(self):
        if self.options.polyfill == "std":
            # C++17
            return {
                "Visual Studio": "15",
                "gcc": "7",
                "clang": "5",
                "apple-clang": "10"
            }
        elif self.options.polyfill == "boost":
            # C++11
            return {
                "Visual Studio": "14",
                "gcc": "5",
                "clang": "3.3",
                "apple-clang": "9"
            }
        else:
            raise ConanInvalidConfiguration(
                "please, specify _compilers_minimum_version for {} polyfill".format(self.options.polyfill)
            )

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

        if self.options.polyfill == "mnmlstc":
            # TODO: add mnmlstc polyfill support
            # Cannot model mnmlstc (not packaged, is pulled dynamically) polyfill dependencies
            raise ConanInvalidConfiguration("mnmlstc polyfill is not yet supported")
        if self.options.polyfill == "experimental":
            # TODO: add experimental support
            # Cannot model std::experimental (how to check availability in stdlib?)
            raise ConanInvalidConfiguration("experimental polyfill is not yet supported")

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimal_std_version)
        else:
            compiler = str(self.settings.compiler)
            version = tools.Version(self.settings.compiler.version)
            if version < self._compilers_minimum_version[compiler]:
                raise ConanInvalidConfiguration(
                    "{} requires a compiler that supports at least C++{}".format(
                        self.name,
                        self._minimal_std_version
                    )
                )

    def requirements(self):
        self.requires("mongo-c-driver/1.17.2")
        if self.options.polyfill == "boost":
            self.requires("boost/1.74.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-r" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions["BSONCXX_POLY_USE_MNMLSTC"] = self.options.polyfill == "mnmlstc"
        self._cmake.definitions["BSONCXX_POLY_USE_STD"] = self.options.polyfill == "std"
        self._cmake.definitions["BSONCXX_POLY_USE_STD_EXPERIMENTAL"] = self.options.polyfill == "experimental"
        self._cmake.definitions["BSONCXX_POLY_USE_BOOST"] = self.options.polyfill == "boost"
        self._cmake.definitions["BUILD_VERSION"] = self.version
        self._cmake.definitions["BSONCXX_LINK_WITH_STATIC_MONGOC"] = not self.options["mongo-c-driver"].shared
        self._cmake.definitions["MONGOCXX_LINK_WITH_STATIC_MONGOC"] = not self.options["mongo-c-driver"].shared
        self._cmake.definitions["MONGOCXX_ENABLE_SSL"] = self.options.with_ssl
        if self.settings.compiler.get_safe("cppstd") is None:
            self.output.warn("The recipe will force the cppstd to {}".format(self._minimal_std_version))
            self._cmake.definitions["CMAKE_CXX_STANDARD"] = self._minimal_std_version
        # FIXME: two CMake module/config files should be generated (mongoc-1.0-config.cmake and bson-1.0-config.cmake),
        # but it can't be modeled right now.
        # Fix should happen in mongo-c-driver recipe
        if not os.path.exists("Findbson-1.0.cmake"):
            self.output.info("Copying mongoc config file to bson")
            shutil.copy("Findmongoc-1.0.cmake", "Findbson-1.0.cmake")
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)

    def build(self):
        self._patch_sources()

        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="THIRD-PARTY-NOTICES", dst="licenses", src=self._source_subfolder)

        cmake = self._configure_cmake()
        cmake.install()

        if self.settings.os == "Windows":
            for dll_file in glob.glob(os.path.join(self.package_folder, "bin", "*.dll")):
                if os.path.basename(dll_file).startswith(("concrt", "msvcp", "vcruntime")):
                    os.remove(dll_file)
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: two CMake module/config files should be generated (mongocxx-config.cmake and bsoncxx-config.cmake),
        # but it can't be modeled right now.
        self.cpp_info.filenames["cmake_find_package"] = "mongocxx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mongocxx"
        self.cpp_info.names["cmake_find_package"] = "mongo"
        self.cpp_info.names["cmake_find_package_multi"] = "mongo"

        # mongocxx
        self.cpp_info.components["mongocxx"].names["cmake_find_package"] = "mongocxx_shared" if self.options.shared else "mongocxx_static"
        self.cpp_info.components["mongocxx"].names["cmake_find_package_multi"] = "mongocxx_shared" if self.options.shared else "mongocxx_static"
        self.cpp_info.components["mongocxx"].names["pkg_config"] = "libmongocxx"
        self.cpp_info.components["mongocxx"].includedirs = [os.path.join("include", "lib", "v_noabi", "mongocxx")]
        self.cpp_info.components["mongocxx"].libs = ["mongocxx" if self.options.shared else "mongocxx-static"]
        if not self.options.shared:
            self.cpp_info.components["mongocxx"].defines.append("MONGOCXX_STATIC")
        if self.options.with_ssl:
            self.cpp_info.components["mongocxx"].defines.append("MONGOCXX_ENABLE_SSL")
        self.cpp_info.components["mongocxx"].requires = ["mongo-c-driver::mongoc", "bsoncxx"]

        # bsoncxx
        self.cpp_info.components["bsoncxx"].names["cmake_find_package"] = "bsoncxx_shared" if self.options.shared else "bsoncxx_static"
        self.cpp_info.components["bsoncxx"].names["cmake_find_package_multi"] = "bsoncxx_shared" if self.options.shared else "bsoncxx_static"
        self.cpp_info.components["bsoncxx"].names["pkg_config"] = "libbsoncxx" if self.options.shared else "libbsoncxx-static"
        self.cpp_info.components["bsoncxx"].includedirs = [os.path.join("include", "lib", "v_noabi", "bsoncxx")]
        self.cpp_info.components["bsoncxx"].libs = ["bsoncxx" if self.options.shared else "bsoncxx-static"]
        if not self.options.shared:
            self.cpp_info.components["bsoncxx"].defines = ["BSONCXX_STATIC"]
        self.cpp_info.components["bsoncxx"].requires = ["mongo-c-driver::bson"]
        if self.options.polyfill == "boost":
            self.cpp_info.components["bsoncxx"].requires.append("boost::boost")
        if self.options.polyfill == "mnmlstc":
            self.cpp_info.components["bsoncxx"].includedirs.append(os.path.join("include", "bsoncxx", "third_party", "mnmlstc"))
