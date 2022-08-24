from conan import ConanFile, tools$
import os

required_conan_version = ">=1.43.0"


class CvPlotConan(ConanFile):
    name = "cvplot"
    description = "fast modular opencv plotting library"
    license = "MIT"
    topics = ("plot", "opencv", "diagram", "plotting")
    homepage = "https://github.com/Profactor/cv-plot"
    url = "https://github.com/conan-io/conan-center-index"
    requires = "opencv/4.5.3"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(pattern="*", dst="include", src=os.path.join(self._source_subfolder, "CvPlot", "inc"))
        
    def package_id(self):
        self.info.header_only()
            
    def package_info(self):
        self.cpp_info.defines.append("CVPLOT_HEADER_ONLY")
        self.cpp_info.set_property("cmake_find_mode", "both") 
        self.cpp_info.names["cmake_find_package"] = "CvPlot"
        self.cpp_info.names["cmake_find_package_multi"] = "CvPlot"
