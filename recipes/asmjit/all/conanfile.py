from conans import ConanFile, CMake, tools
import glob
import os


class AsmjitConan(ConanFile):
    name = "asmjit"
    description = "AsmJit is a lightweight library for machine code " \
                  "generation written in C++ language."
    license = "Zlib"
    topics = ("conan", "asmjit", "compiler", "assembler", "jit")
    homepage = "https://asmjit.com"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = "CMakeLists.txt"
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
        if self.settings.compiler.get_safe("cppstd"):
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("asmjit-*")[0]
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["ASMJIT_EMBED"] = False
        self._cmake.definitions["ASMJIT_STATIC"] = not self.options.shared
        self._cmake.definitions["ASMJIT_BUILD_X86"] = False
        self._cmake.definitions["ASMJIT_TEST"] = False
        self._cmake.definitions["ASMJIT_NO_NATVIS"] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "asmjit"
        self.cpp_info.names["cmake_find_package_multi"] = "asmjit"
        self.cpp_info.libs = ["asmjit"]
        if not self.options.shared:
            self.cpp_info.defines = ["ASMJIT_STATIC"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread", "rt"]
