import os
import functools
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration


class SquirrelConan(ConanFile):
    name = "squirrel"
    description = "Squirrel is a high level imperative, object-oriented programming " \
                  "language, designed to be a light-weight scripting language that " \
                  "fits in the size, memory bandwidth, and real-time requirements " \
                  "of applications like video games."
    topics = ("object-oriented", "scripting", "light-weight")
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.squirrel-lang.org/"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    generators = "cmake"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

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

    def validate(self):
        if tools.Version(self.version) <= "3.1":
            if self.settings.os == "Macos":
                raise ConanInvalidConfiguration("squirrel 3.1 and earlier does not support Macos")
            if self.settings.compiler == "clang" and tools.Version(self.settings.compiler.version) < "9":
                raise ConanInvalidConfiguration("squirrel 3.1 and earlier does not support Clang 8 and earlier")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DISABLE_DYNAMIC"] = not self.options.shared
        cmake.definitions["DISABLE_STATIC"] = self.options.shared
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        # squirrel
        squirrel_name = "squirrel" if self.options.shared else "squirrel_static"
        self.cpp_info.components["libsquirrel"].names["cmake_find_package"] = squirrel_name
        self.cpp_info.components["libsquirrel"].names["cmake_find_package_multi"] = squirrel_name
        self.cpp_info.components["libsquirrel"].libs = [squirrel_name]
        # sqstdlib
        sqstdlib_name = "sqstdlib" if self.options.shared else "sqstdlib_static"
        self.cpp_info.components["sqstdlib"].names["cmake_find_package"] = sqstdlib_name
        self.cpp_info.components["sqstdlib"].names["cmake_find_package_multi"] = sqstdlib_name
        self.cpp_info.components["sqstdlib"].libs = [sqstdlib_name]
        self.cpp_info.components["sqstdlib"].requires = ["libsquirrel"]

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var : {}".format(binpath))
        self.env_info.PATH.append(binpath)
