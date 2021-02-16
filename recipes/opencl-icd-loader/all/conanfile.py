from conans import ConanFile, CMake, tools
import os


class OpenclIcdLoaderConan(ConanFile):
    name = "opencl-icd-loader"
    description = "OpenCL ICD Loader."
    license = "Apache-2.0"
    topics = ("conan", "opencl-icd-loader", "opencl", "khronos", "parallel", "icd-loader")
    homepage = "https://github.com/KhronosGroup/OpenCL-ICD-Loader"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

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
        del self.settings.compiler.cppstd
        del self.settings.compiler.libcxx

    def requirements(self):
        self.requires("opencl-headers/{}".format(self.version))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("OpenCL-ICD-Loader-" + self.version, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OPENCL_ICD_LOADER_HEADERS_DIR"] = ";".join(self.deps_cpp_info["opencl-headers"].include_paths)
        if self.settings.compiler == "Visual Studio":
            self._cmake.definitions["USE_DYNAMIC_VCXX_RUNTIME"] = str(self.settings.compiler.runtime).startswith("MD")
        self._cmake.definitions["OPENCL_ICD_LOADER_PIC"] = self.options.get_safe("fPIC", True)
        self._cmake.definitions["OPENCL_ICD_LOADER_BUILD_TESTING"] = False
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["OpenCL"]
        if not self.options.shared:
            if self.settings.os == "Linux":
                self.cpp_info.system_libs = ["dl", "pthread"]
            elif self.settings.os == "Windows":
                self.cpp_info.system_libs = ["cfgmgr32", "runtimeobject"]
