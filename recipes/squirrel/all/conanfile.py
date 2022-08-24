from conan import ConanFile, tools
from conans import CMake
from conan.errors import ConanInvalidConfiguration
import functools
import os

required_conan_version = ">=1.43.0"


class SquirrelConan(ConanFile):
    name = "squirrel"
    description = "Squirrel is a high level imperative, object-oriented programming " \
                  "language, designed to be a light-weight scripting language that " \
                  "fits in the size, memory bandwidth, and real-time requirements " \
                  "of applications like video games."
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://www.squirrel-lang.org/"
    license = "MIT"
    topics = ("squirrel", "programming-language", "object-oriented", "scripting")

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
            if self.settings.compiler == "clang":
                compiler_version = tools.Version(self.settings.compiler.version)
                if compiler_version < "9" or compiler_version >= "11":
                    raise ConanInvalidConfiguration(
                        f"squirrel 3.1 and earlier does not support Clang {compiler_version}"
                    )

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    @functools.lru_cache(1)
    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["DISABLE_DYNAMIC"] = not self.options.shared
        cmake.definitions["DISABLE_STATIC"] = self.options.shared
        cmake.configure()
        return cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "squirrel")
        # CMakeDeps generator uses the global target if a downstream recipe depends on squirrel globally,
        # and squirrel::squirrel is stolen by libsquirrel component (if shared) which doesn't depend on all other components.
        # So this unofficial target is created as a workaround.
        self.cpp_info.set_property("cmake_target_name", "squirrel::squirel-all-do-not-use")

        suffix = "" if self.options.shared else "_static"

        # squirrel
        self.cpp_info.components["libsquirrel"].set_property("cmake_target_name", "squirrel::squirrel{}".format(suffix))
        self.cpp_info.components["libsquirrel"].libs = ["squirrel{}".format(suffix)]

        # sqstdlib
        self.cpp_info.components["sqstdlib"].set_property("cmake_target_name", "squirrel::sqstdlib{}".format(suffix))
        self.cpp_info.components["sqstdlib"].libs = ["sqstdlib{}".format(suffix)]
        self.cpp_info.components["sqstdlib"].requires = ["libsquirrel"]

        binpath = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var : {}".format(binpath))
        self.env_info.PATH.append(binpath)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libsquirrel"].names["cmake_find_package"] = "squirrel{}".format(suffix)
        self.cpp_info.components["libsquirrel"].names["cmake_find_package_multi"] = "squirrel{}".format(suffix)
        self.cpp_info.components["sqstdlib"].names["cmake_find_package"] = "sqstdlib{}".format(suffix)
        self.cpp_info.components["sqstdlib"].names["cmake_find_package_multi"] = "sqstdlib{}".format(suffix)
