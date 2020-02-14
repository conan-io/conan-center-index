import os
import stat
import shutil
from conans import ConanFile, tools, CMake
from conans.errors import ConanInvalidConfiguration

class blake2Conan(ConanFile):
    name = "blake2"
    version = "20190723" #BLAKE2 doesn't have versions so we use the last commit date instead
    license = ["CC0-1.0", "OpenSSL", "APSL-2.0"]
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/BLAKE2/BLAKE2"
    description = ("BLAKE2 is a cryptographic hash function faster than MD5, \
                    SHA-1, SHA-2, and SHA-3, yet is at least as secure as the latest standard SHA-3")
    settings = "os", "arch", "compiler", "build_type"
    topics = ("conan", "blake2", "hash")
    exports_sources = ["CMakeLists.txt", "CMakeLists_build.txt"] #The first file is the conan wrapper, the second one is the actual CMakeList that builds the project
    generators = ["cmake"]
    options = {"fPIC": [True, False], "use_sse": [True, False], "use_neon": [True, False]}
    default_options = {"fPIC": True, "use_sse": False, "use_neon": False}
    _source_subfolder = "source_subfolder"
    _cmake = None

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["USE_SSE"] = self.options.use_sse
            self._cmake.definitions["USE_NEON"] = self.options.use_neon
            self._cmake.configure()
        return self._cmake

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.use_neon and not "arm" in self.settings.arch:
            raise ConanInvalidConfiguration("Neon sources only supported on arm-based CPUs")

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        #Get te extracted folder name. Its BLAKE2-githubCommit
        listdir = os.listdir()
        extracted_dir = [i for i in listdir if "BLAKE2-" in i][0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        #Move makefile into _source_subfolder.
        shutil.move(src=os.path.join(self.source_folder, "CMakeLists_build.txt"), dst=os.path.join(self.source_folder,self._source_subfolder, "CMakeLists.txt"))
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = ["include",os.path.join("include","blake2")]
