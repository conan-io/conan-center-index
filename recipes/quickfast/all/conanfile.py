from conans import ConanFile, CMake, tools
import os
import shutil


class QuickfastConan(ConanFile):
    name = "quickfast"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://objectcomputing.com/"
    description = "QuickFAST is an Open Source native C++ implementation of the FAST Protocol"
    topics = ("conan", "QuickFAST", "FAST", "FIX", "Fix Adapted for STreaming", "Financial Information Exchange",
              "libraries", "cpp")
    settings = "os", "compiler", "build_type", "arch"
    options = {"fPIC": [True, False],
               "shared": [True, False]}
    default_options = {"fPIC": True,
                       "shared": False}
    requires = ["boost/1.73.0", "xerces-c/3.2.3"]
    generators = "cmake"
    exports_sources = "CMakeLists.txt", "patches/**"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["BOOST_BIND_NO_PLACEHOLDERS"] = True
            self._cmake.configure(source_folder=self._source_subfolder, build_folder=self._build_subfolder)
        return self._cmake

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename(self.name + "-" + self.version.replace(".", "_"), self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, "11")

    def build(self):
        # Patch taken from:
        # https://raw.githubusercontent.com/microsoft/vcpkg/master/ports/quickfast/00001-fix-boost-asio.patch
        patches = self.conan_data["patches"][self.version]
        for patch in patches:
            tools.patch(**patch)

        shutil.copy("CMakeLists.txt",
                    os.path.join(self._source_subfolder, "CMakeLists.txt"))

        cmake = self._configure_cmake()
        cmake.build(target="quickfast")

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("license.txt", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs.append(os.path.join("include", "quickfast"))
        self.cpp_info.defines.append("BOOST_BIND_NO_PLACEHOLDERS")
        if self.options.shared:
            self.cpp_info.defines.append("QUICKFAST_BUILD_DLL")
        else:
            self.cpp_info.defines.append("QUICKFAST_HAS_DLL=0")
