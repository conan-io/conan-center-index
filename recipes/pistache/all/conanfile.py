import os
import glob
from conans import ConanFile, CMake, tools


required_conan_version = ">=1.29.1"


class PistacheConan(ConanFile):
    name = "pistache"
    license = "Apache-2.0"
    homepage = "https://github.com/pistacheio/pistache"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("http", "rest", "framework", "networking")
    description = "Pistache is a modern and elegant HTTP and REST framework for C++"
    settings = "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
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
        compilers = {
            "gcc": "5",
            "clang": "3.4",
        }
        if self.options.os != "Linux":
            raise ConanInvalidConfiguration("Pistache is only support by Linux.")

        if self.options.shared:
            del self.options.fPIC

        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 14)
        minimum_compiler = compilers.get(str(self.settings.compiler))
        if minimum_compiler:
            if tools.Version(self.settings.compiler.version) < minimum_compiler:
                raise ConanInvalidConfiguration("Pistache requires c++14, which your compiler does not support.")
        else:
            self.output.warn("Pistache requires c++14, but is unknown to this recipe. Assuming your compiler supports c++14.")

    def requirements(self):
        self.requires("openssl/1.1.1h")
        self.requires("rapidjson/1.1.0")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("pistache-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PISTACHE_ENABLE_NETWORK_TESTS"] = False
        self._cmake.definitions["PISTACHE_USE_SSL"] = False
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "*.a")

    def package_info(self):
        # TODO: Pistache does not use namespace
        # TODO: Pistache variables are CamelCase e.g Pistache_BUILD_DIRS
        self.cpp_info.filenames["cmake_find_package"] = "Pistache"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Pistache"
        suffix = "_{}".format("shared" if self.options.shared else "static")
        self.cpp_info.components["libpistache"].names["cmake_find_package"] = "pistache" + suffix
        self.cpp_info.components["libpistache"].names["cmake_find_package_multi"] = "pistache" + suffix
        self.cpp_info.components["libpistache"].libs = tools.collect_libs(self)
        self.cpp_info.components["libpistache"].requires = ["openssl::openssl", "rapidjson::rapidjson"]
        self.cpp_info.components["libpistache"].defines = ["PISTACHE_USE_SSL=1"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libpistache"].system_libs = ["pthread"]
