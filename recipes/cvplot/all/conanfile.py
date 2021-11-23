import os
from conans import ConanFile, CMake, tools

required_conan_version = ">=1.33.0"


class CvPlotConan(ConanFile):
    name = "cvplot"
    description = "fast modular opencv plotting library"
    license = "MIT License"
    topics = ("plot", "opencv")
    homepage = "https://github.com/Profactor/cv-plot"
    url = "https://github.com/conan-io/conan-center-index"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "header_only": [True, False]}
    default_options = {"shared": False, "header_only": False}
    requires = "opencv/4.5.3"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        if self.options.header_only:
            del self.options.shared

    def package_id(self):
        if self.options.header_only:
            self.info.header_only()
            
    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def build(self):
        if not self.options.header_only:
            cmake = self._configure_cmake()
            cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["CVPLOT_HEADER_ONLY"] = self.options.header_only
        self._cmake.definitions["CVPLOT_WITH_TESTS"] = False
        self._cmake.definitions["CVPLOT_WITH_EXAMPLES"] = False
        self._cmake.configure(source_folder=self._source_subfolder)
        return self._cmake

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if self.options.header_only:
            self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "CvPlot", "inc"))
        else:
            cmake = self._configure_cmake()
            cmake.install()
        
    def package_info(self):
        if self.options.header_only:
            self.cpp_info.defines.append("CVPLOT_HEADER_ONLY")
        else:
            self.cpp_info.libs = ["CvPlot"]
            if self.options.shared:
                self.cpp_info.defines.append("CVPLOT_SHARED")
