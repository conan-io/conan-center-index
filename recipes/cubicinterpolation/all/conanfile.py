from conans import ConanFile, CMake, tools
import glob
import os

class CubicInterpolationConan(ConanFile):
    name = "cubic-interpolation"
    homepage = "https://github.com/MaxSac/cubic_interpolation"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    description = "Leightweight interpolation library based on boost and eigen."
    topics = ("interpolation", "splines", "cubic", "bicubic", "boost", "eigen3")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {"shared": False, "fPIC": True}
    generators = "cmake"
    _source_subfolder = "source_subfolder"
    exports_sources = ["CMakeLists.txt"]
	_cmake = None

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

	def configure(self):
	    if self.options.shared:
	        del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob("cubic_interpolation-*/")[0]
        os.rename(extracted_dir, self._source_folder)

    def requirements(self):
        self.requires("boost/1.75.0")
        self.requires("eigen/3.3.9")

    def _configure_cmake(self):
    	if self._cmake:
    	    return self._cmake
    	self._cmake = CMake(self)
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
        self.cpp_info.libs = tools.collect_libs(self)
