import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.36.0"


class OneDNNConan(ConanFile):
    name = "onednn"
    description = "oneAPI Deep Neural Network Library (oneDNN) is an open-source cross-platform performance library "  \
                  "of basic building blocks for deep learning applications."
    license = "Apache-2.0"
    topics = ("machine-learning", "neural-networks", "deep-learning", "gpu")
    homepage = "https://github.com/oneapi-src/oneDNN"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cpu_runtime": ["OMP", "TBB", "SEQ"]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "cpu_runtime": "TBB"  # The default in oneDNN's CMakeLists is OMP but this necessitates having OpenMP on the system
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def requirements(self):
        if self.options.cpu_runtime == "TBB":
            self.requires("onetbb/2021.3.0")

    def build_requirements(self):
        self.build_requires("ninja/1.10.2")

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions.update({
            "DNNL_LIBRARY_TYPE": "SHARED" if self.options.shared else "STATIC",
            "DNNL_BUILD_EXAMPLES": False,
            "DNNL_BUILD_TESTS": False,
            "DNNL_GPU_RUNTIME": "NONE",
            "DNNL_WITH_SYCL": False,
            "DNNL_CPU_RUNTIME": self.options.cpu_runtime
        })
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()
        tools.rmdir(os.path.join(self.package_folder, "share"))
        tools.rmdir(os.path.join(self.package_folder, "lib", "cmake"))
        tools.remove_files_by_mask(os.path.join(self.package_folder, "lib"), "libmkldnn.*")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "oneDNN")
        self.cpp_info.set_property("cmake_target_name", "DNNL")
        if not self.options.shared and self.options.cpu_runtime == "OMP":
            if self.settings.compiler in ("Visual Studio", "msvc"):
                openmp_flags = ["-openmp"]
            elif self.settings.compiler in ("gcc", "clang"):
                openmp_flags = ["-fopenmp"]
            elif self.settings.compiler == "apple-clang":
                openmp_flags = ["-Xpreprocessor", "-fopenmp"]
            else:
                openmp_flags = []
            self.cpp_info.components["dnnl"].exelinkflags = openmp_flags
            self.cpp_info.components["dnnl"].sharedlinkflags = openmp_flags
        self.cpp_info.components["dnnl"].libs = ["dnnl"]
        if self.options.cpu_runtime == "TBB":
            self.cpp_info.components["dnnl"].requires = ["onetbb::libtbb"]
        if self.settings.os == "Linux":
            self.cpp_info.components["dnnl"].system_libs = ["dl"]
