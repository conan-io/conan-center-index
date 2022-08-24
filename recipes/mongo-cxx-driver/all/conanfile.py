from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os
import shutil

required_conan_version = ">=1.43.0"


class MongoCxxConan(ConanFile):
    name = "mongo-cxx-driver"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://mongocxx.org"
    description = "C++ Driver for MongoDB"
    topics = ("libbsoncxx", "libmongocxx", "mongo", "mongodb", "database", "db")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "polyfill": ["std", "boost", "mnmlstc", "experimental"],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "polyfill": "boost",
        "with_ssl": True,
    }

    generators = "cmake", "cmake_find_package"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

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
        self.requires("mongo-c-driver/1.17.6")
        if self.options.polyfill == "boost":
            self.requires("boost/1.78.0")

    @property
    def _minimal_std_version(self):
        return {
            "std": "17",
            "experimental": "14",
            "boost": "11",
            "polyfill": "11"
        }[str(self.options.polyfill)]

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
        elif self.options.polyfill == "experimental":
            # C++14
            return {
                "Visual Studio": "15",
                "gcc": "5",
                "clang": "3.5",
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

    def validate(self):
        if self.options.with_ssl and not bool(self.options["mongo-c-driver"].with_ssl):
            raise ConanInvalidConfiguration("mongo-cxx-driver with_ssl=True requires mongo-c-driver with a ssl implementation")

        if self.options.polyfill == "mnmlstc":
            # TODO: add mnmlstc polyfill support
            # Cannot model mnmlstc (not packaged, is pulled dynamically) polyfill dependencies
            raise ConanInvalidConfiguration("mnmlstc polyfill is not yet supported")

        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, self._minimal_std_version)

        compiler = str(self.settings.compiler)
        if self.options.polyfill == "experimental" and compiler == "apple-clang":
            raise ConanInvalidConfiguration("experimental polyfill is not supported for apple-clang")

        if compiler not in self._compilers_minimum_version:
            self.output.warn("Unknown compiler, assuming it supports at least C++{}".format(self._minimal_std_version))
            return

        version = tools.Version(self.settings.compiler.version)
        if version < self._compilers_minimum_version[compiler]:
            raise ConanInvalidConfiguration(
                "{} requires a compiler that supports at least C++{}".format(
                    self.name,
                    self._minimal_std_version
                )
            )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

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
        if not tools.valid_min_cppstd(self, self._minimal_std_version):
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
            tools.files.patch(self, **patch)

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
            for vc_file in ("concrt", "msvcp", "vcruntime"):
                tools.remove_files_by_mask(os.path.join(self.package_folder, "bin"), "{}*.dll".format(vc_file))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        # FIXME: two CMake module/config files should be generated (mongocxx-config.cmake and bsoncxx-config.cmake),
        # but it can't be modeled right now.
        mongocxx_target = "mongocxx_shared" if self.options.shared else "mongocxx_static"
        self.cpp_info.set_property("cmake_file_name", "mongocxx")
        self.cpp_info.set_property("cmake_target_name", "mongo::{}".format(mongocxx_target))

        self.cpp_info.filenames["cmake_find_package"] = "mongocxx"
        self.cpp_info.filenames["cmake_find_package_multi"] = "mongocxx"
        self.cpp_info.names["cmake_find_package"] = "mongo"
        self.cpp_info.names["cmake_find_package_multi"] = "mongo"

        # mongocxx
        self.cpp_info.components["mongocxx"].set_property("cmake_target_name", "mongo::{}".format(mongocxx_target))
        self.cpp_info.components["mongocxx"].set_property("pkg_config_name", "libmongocxx" if self.options.shared else "libmongocxx-static")

        self.cpp_info.components["mongocxx"].names["cmake_find_package"] = mongocxx_target
        self.cpp_info.components["mongocxx"].names["cmake_find_package_multi"] = mongocxx_target

        self.cpp_info.components["mongocxx"].libs = ["mongocxx" if self.options.shared else "mongocxx-static"]
        if not self.options.shared:
            self.cpp_info.components["mongocxx"].defines.append("MONGOCXX_STATIC")
        self.cpp_info.components["mongocxx"].requires = ["mongo-c-driver::mongoc", "bsoncxx"]

        # bsoncxx
        bsoncxx_target = "bsoncxx_shared" if self.options.shared else "bsoncxx_static"
        self.cpp_info.components["bsoncxx"].set_property("cmake_target_name", "mongo::{}".format(bsoncxx_target))
        self.cpp_info.components["bsoncxx"].set_property("pkg_config_name", "libbsoncxx" if self.options.shared else "libbsoncxx-static")

        self.cpp_info.components["bsoncxx"].names["cmake_find_package"] = bsoncxx_target
        self.cpp_info.components["bsoncxx"].names["cmake_find_package_multi"] = bsoncxx_target

        self.cpp_info.components["bsoncxx"].libs = ["bsoncxx" if self.options.shared else "bsoncxx-static"]
        if not self.options.shared:
            self.cpp_info.components["bsoncxx"].defines = ["BSONCXX_STATIC"]
        self.cpp_info.components["bsoncxx"].requires = ["mongo-c-driver::bson"]
        if self.options.polyfill == "boost":
            self.cpp_info.components["bsoncxx"].requires.append("boost::boost")
