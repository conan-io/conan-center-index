from conans import ConanFile, tools
import os

class ThrustConan(ConanFile):
    name = "thrust"
    license = "Apache-2.0"
    description = ("Thrust is a parallel algorithms library which resembles"
                   "the C++ Standard Template Library (STL).")
    topics = ("parallel", "stl", "header-only")
    homepage = "https://thrust.github.io/"
    url = "https://github.com/conan-io/conan-center-index"
    no_copy_source = True
    options = {"device_system": ["cuda", "cpp", "omp", "tbb"]}
    default_options = {"device_system": "cuda"}

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        if self.options.device_system == "tbb":
            self.requires("tbb/2020.1")
        elif self.options.device_system != "cpp":
            self.output.warn('Conan package for {0} is not available,'
                             ' this package will use {0} from system.'
                             .format(str(self.options.device_system).upper()))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def package(self):
        self.copy(pattern="LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("*", src=os.path.join(self._source_subfolder, "thrust"),
                  dst=os.path.join("include", "thrust"))

    def package_id(self):
        self.info.header_only()

    def package_info(self):
        self.cpp_info.defines = ["THRUST_DEVICE_SYSTEM=THRUST_DEVICE_SYSTEM_{}".format(
            str(self.options.device_system).upper())]
