import os
from conans import ConanFile, tools, CMake

class eigenConan(ConanFile):
    name = "eigen"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "http://eigen.tuxfamily.org"
    description = "Eigen is a C++ template library for linear algebra: matrices, vectors, \
                   numerical solvers, and related algorithms."
    license = "MPL-2.0"
    topics = ("eigen", "algebra", "linear-algebra", "vector", "numerical")
    settings = "os", "compiler"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "_source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        #Get te extracted folder name. They allways have the format eigen-eigen-xxxxxx
        listdir = os.listdir()
        extracted_dir = [i for i in listdir if "eigen-eigen" in i][0]
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        cmake = CMake(self)
        cmake.configure(source_folder=self._source_subfolder)
        cmake.install()

        self.copy("COPYING.*", dst="licenses", src=self._source_subfolder)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.includedirs = [os.path.join("include","eigen3")]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs = ["m"]
        self.cpp_info.names["cmake_find_package"] = "Eigen3"
        self.cpp_info.names["cmake_find_package_multi"] = "Eigen3"
