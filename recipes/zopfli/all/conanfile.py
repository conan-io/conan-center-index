from conans import ConanFile, CMake, tools
import os

required_conan_version = ">=1.43.0"


class ZopfliConan(ConanFile):
    name = "zopfli"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/zopfli/"
    description = (
        "Zopfli Compression Algorithm is a compression library programmed in C "
        "to perform very good, but slow, deflate or zlib compression."
    )
    topics = ("zopfli", "compression", "deflate", "gzip", "zlib")

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        cmake = CMake(self)
        cmake.definitions["ZOPFLI_BUILD_INSTALL"] = True
        cmake.definitions["CMAKE_MACOSX_BUNDLE"] = False
        # Generate a relocatable shared lib on Macos
        cmake.definitions["CMAKE_POLICY_DEFAULT_CMP0042"] = "NEW"
        cmake.configure()
        self._cmake = cmake
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Zopfli")

        self.cpp_info.components["libzopfli"].set_property("cmake_target_name", "Zopfli::libzopfli")
        self.cpp_info.components["libzopfli"].libs = ["zopfli"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["libzopfli"].system_libs = ["m"]

        self.cpp_info.components["libzopflipng"].set_property("cmake_target_name", "Zopfli::libzopflipng")
        self.cpp_info.components["libzopflipng"].libs = ["zopflipng"]
        self.cpp_info.components["libzopflipng"].requires = ["libzopfli"]

        bin_path = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bin_path))
        self.env_info.PATH.append(bin_path)

        # TODO: to remove in conan v2 once cmake_find_package_* generators removed
        self.cpp_info.names["cmake_find_package"] = "Zopfli"
        self.cpp_info.names["cmake_find_package_multi"] = "Zopfli"
        self.cpp_info.components["libzopfli"].names["cmake_find_package"] = "libzopfli"
        self.cpp_info.components["libzopfli"].names["cmake_find_package_multi"] = "libzopfli"
        self.cpp_info.components["libzopflipng"].names["cmake_find_package"] = "libzopflipng"
        self.cpp_info.components["libzopflipng"].names["cmake_find_package_multi"] = "libzopflipng"
