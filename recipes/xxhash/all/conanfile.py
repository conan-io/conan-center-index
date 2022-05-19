from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class XxHashConan(ConanFile):
    name = "xxhash"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Cyan4973/xxHash"
    description = "Extremely fast non-cryptographic hash algorithm"
    topics = ("hash", "algorithm", "fast", "checksum", "hash-functions")
    license = "BSD-2-Clause"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utility": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utility": True,
    }

    generators = "cmake"
    _cmake = None

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def _configure_cmake(self):
        if self._cmake is None:
            self._cmake = CMake(self)
            self._cmake.definitions["XXHASH_BUNDLED_MODE"] = False
            self._cmake.definitions["XXHASH_BUILD_XXHSUM"] = self.options.utility
            # Fix CMake configuration if target is iOS/tvOS/watchOS
            self._cmake.definitions["CMAKE_MACOSX_BUNDLE"] = False
            # Generate a relocatable shared lib on Macos
            self._cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
            self._cmake.configure()
        return self._cmake

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "xxHash")
        self.cpp_info.set_property("cmake_target_name", "xxHash::xxhash")
        self.cpp_info.set_property("pkg_config_name", "libxxhash")
        # TODO: back to global scope in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.components["libxxhash"].libs = ["xxhash"]

        if self.options.utility:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "xxHash"
        self.cpp_info.names["cmake_find_package_multi"] = "xxHash"
        self.cpp_info.names["pkg_config"] = "libxxhash"
        self.cpp_info.components["libxxhash"].names["cmake_find_package"] = "xxhash"
        self.cpp_info.components["libxxhash"].names["cmake_find_package_multi"] = "xxhash"
        self.cpp_info.components["libxxhash"].set_property("cmake_target_name", "xxHash::xxhash")
