from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class PistacheConan(ConanFile):
    name = "pistache"
    license = "Apache-2.0"
    homepage = "https://github.com/pistacheio/pistache"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("http", "rest", "framework", "networking")
    description = "Pistache is a modern and elegant HTTP and REST framework for C++"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_ssl": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_ssl": False,
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

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        self.requires("rapidjson/1.1.0")
        if self.options.with_ssl:
            self.requires("openssl/1.1.1q")

    def validate(self):
        compilers = {
            "gcc": "7",
            "clang": "6",
        }
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("Pistache is only support by Linux.")

        if self.settings.compiler == "clang":
            raise ConanInvalidConfiguration("Clang support is broken. See pistacheio/pistache#835.")

        if self.settings.compiler.cppstd:
            tools.build.check_min_cppstd(self, 17)
        minimum_compiler = compilers.get(str(self.settings.compiler))
        if minimum_compiler:
            if tools.scm.Version(self.settings.compiler.version) < minimum_compiler:
                raise ConanInvalidConfiguration("Pistache requires c++17, which your compiler does not support.")
        else:
            self.output.warn("Pistache requires c++17, but this compiler is unknown to this recipe. Assuming your compiler supports c++17.")

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["PISTACHE_ENABLE_NETWORK_TESTS"] = False
        self._cmake.definitions["PISTACHE_USE_SSL"] = self.options.with_ssl
        # pistache requires explicit value for fPIC
        self._cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.get_safe("fPIC", True)
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        if self.options.shared:
            tools.files.rm(self, "*.a", os.path.join(self.package_folder, "lib"))

    def package_info(self):
        # TODO: Pistache does not use namespace
        # TODO: Pistache variables are CamelCase e.g Pistache_BUILD_DIRS
        self.cpp_info.filenames["cmake_find_package"] = "Pistache"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Pistache"
        self.cpp_info.names["pkg_config"] = "libpistache"
        suffix = "_{}".format("shared" if self.options.shared else "static")
        self.cpp_info.components["libpistache"].names["cmake_find_package"] = "pistache" + suffix
        self.cpp_info.components["libpistache"].names["cmake_find_package_multi"] = "pistache" + suffix
        self.cpp_info.components["libpistache"].libs = tools.files.collect_libs(self, self)
        self.cpp_info.components["libpistache"].requires = ["rapidjson::rapidjson"]
        if self.options.with_ssl:
            self.cpp_info.components["libpistache"].requires.append("openssl::openssl")
            self.cpp_info.components["libpistache"].defines = ["PISTACHE_USE_SSL=1"]
        if self.settings.os == "Linux":
            self.cpp_info.components["libpistache"].system_libs = ["pthread"]
