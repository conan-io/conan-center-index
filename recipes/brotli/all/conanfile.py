from conans import CMake, ConanFile, tools
import os


class BrotliConan(ConanFile):
    name = "brotli"
    description = "Brotli is a generic-purpose lossless compression algorithm that compresses data using a combination of a modern variant of the LZ77 algorithm, Huffman coding and 2nd order context modeling, with a compression ratio comparable to the best currently available general-purpose compression methods. It is similar in speed with deflate but offers more dense compression."
    topics = ("conan", "snappy", "google", "compressor", "decompressor")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/brotli"
    license = "MIT",
    exports_sources = "CMakeLists.txt",
    generators = "cmake",
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_folder = "brotli-{}".format(self.version)
        os.rename(extracted_folder, self._source_subfolder)

    def _patch_sources(self):
        # avoid building and installing static libraries if shared build and vice versa
        cmakefile = os.path.join(self._source_subfolder, "CMakeLists.txt")
        tools.save(cmakefile,
                   "set_target_properties(brotli PROPERTIES EXCLUDE_FROM_ALL ON EXCLUDE_FROM_DEFAULT ON)\n", append=True)
        for lib in self._get_libraries(not self.options.shared):
            tools.save(cmakefile,
                       "set_target_properties({} PROPERTIES EXCLUDE_FROM_ALL ON EXCLUDE_FROM_DEFAULT ON)\n".format(lib), append=True)
        shared_libraries_cmake = "${BROTLI_LIBRARIES_CORE}"
        static_libraries_cmake = "${BROTLI_LIBRARIES_CORE_STATIC}"
        tools.replace_in_file(cmakefile,
                              "TARGETS {}".format(static_libraries_cmake if self.options.shared else shared_libraries_cmake),
                              "TARGETS {}".format(shared_libraries_cmake if self.options.shared else static_libraries_cmake),)
        tools.replace_in_file(cmakefile,
                              "TARGETS brotli",
                              "TARGETS {}".format(shared_libraries_cmake if self.options.shared else static_libraries_cmake),)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BROTLI_BUNDLED_MODE"] = False
        cmake.definitions["BROTLI_DISABLE_TESTS"] = True
        cmake.configure()
        return cmake

    def build(self):
        self._patch_sources()
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def _get_libraries(self, shared):
        libs = ["brotlienc", "brotlidec", "brotlicommon"]
        if not shared:
            libs = ["{}-static".format(l) for l in libs]
        return libs

    def package_info(self):
        self.cpp_info.name = "Brotli"
        self.cpp_info.libs = self._get_libraries(self.options.shared)
        self.cpp_info.includedirs = [os.path.join(self.package_folder, "include"),
                                     os.path.join(self.package_folder, "include", "brotli")]
        if self.options.shared:
            self.cpp_info.defines.append("BROTLI_SHARED_COMPILATION")
