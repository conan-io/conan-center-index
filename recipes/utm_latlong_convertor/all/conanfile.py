from conans import ConanFile, tools
import os
import glob


class UTMLatLongConvertorConan(ConanFile):
    name = "ofxGeo"
    description = "A convertor for Latitude Longitude to UTM Co-ordinate and vice versa."
    topics = ("conan", "utm_latlong_convertor", "utm", "latitude", "longitude")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/bakercp/ofxGeo"
    license = "MIT"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses",
                  src=self._source_subfolder)

        self.copy(pattern="UTM.h", dst="include",
                  src=os.path.join(self._source_subfolder, "libs", "UTM", "include", "UTM"))

        tools.replace_in_file(os.path.join(self.package_folder, "include", "UTM.h"),
                              "#include \"ofConstants.h\"", "// #include \"ofConstants.h\"")
        tools.replace_in_file(os.path.join(self.package_folder, "include", "UTM.h"), "#define UTM_EP2		(UTM_E2/(1-UTM_E2))	///< e'^2", """#define UTM_EP2		(UTM_E2/(1-UTM_E2))	///< e'^2
#define DEG_TO_RAD (M_PI/180.0)
#define RAD_TO_DEG (180.0/M_PI) """,)

    def package_info(self):
        # Original CMakeLists.txt exports "utm_latlong_convertor::utm_latlong_convertor" target:
        self.cpp_info.names["cmake_find_package"] = "utm_latlong_convertor"
        self.cpp_info.names["cmake_find_package_multi"] = "utm_latlong_convertor"

    def package_id(self):
        self.info.header_only()
