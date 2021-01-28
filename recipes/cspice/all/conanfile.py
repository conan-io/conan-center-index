import os

from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration

class CspiceConan(ConanFile):
    name = "cspice"
    description = "NASA C SPICE library"
    license = "TSPA"
    topics = ("conan", "spice", "naif", "kernels", "space", "nasa", "jpl", "spacecraft", "planet", "robotics")
    homepage = "https://naif.jpl.nasa.gov/naif/toolkit.html"
    url = "https://github.com/conan-io/conan-center-index"
    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utilities": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utilities": True
    }

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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        self._raise_if_not_supported_triplet()

    def _raise_if_not_supported_triplet(self):
        sources_url_per_triplet = self.conan_data["sources"][self.version]["url"]
        the_os = self._get_os_or_subsystem()
        if the_os not in sources_url_per_triplet:
            raise ConanInvalidConfiguration("cspice does not support {0}".format(the_os))
        compiler = str(self.settings.compiler)
        if compiler not in sources_url_per_triplet[the_os]:
            raise ConanInvalidConfiguration("cspice does not support {0} on {1}".format(compiler, the_os))
        arch = str(self.settings.arch)
        if arch not in sources_url_per_triplet[the_os][compiler]:
            raise ConanInvalidConfiguration("cspice does not support {0} on {1} {2}".format(compiler, the_os, arch))

    def _get_os_or_subsystem(self):
        if self.settings.os == "Windows" and self.settings.os.subsystem != "None":
            os_or_subsystem = str(self.settings.os.subsystem)
        else:
            os_or_subsystem = str(self.settings.os)
        return os_or_subsystem

    def source(self):
        pass

    def build(self):
        self._get_sources()
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _get_sources(self):
        the_os = self._get_os_or_subsystem()
        compiler = str(self.settings.compiler)
        arch = str(self.settings.arch)
        url = self.conan_data["sources"][self.version]["url"][the_os][compiler][arch]
        sha256 = self.conan_data["sources"][self.version]["sha256"][the_os][compiler][arch]
        if url.endswith(".tar.Z"): # Python doesn't have any module to uncompress .Z files
            filename = os.path.basename(url)
            tools.download(url, filename, sha256=sha256)
            command = "zcat {} | tar -xf -".format(filename)
            self.run(command=command)
            os.remove(filename)
        else:
            tools.get(url, sha256=sha256)
        os.rename(self.name, self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_UTILITIES"] = self.options.utilities
        self._cmake.configure()
        return self._cmake

    def package(self):
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = self._configure_cmake()
        cmake.install()

    def _extract_license(self):
        spiceusr_header = tools.load(os.path.join(self._source_subfolder, "include", "SpiceUsr.h"))
        begin = spiceusr_header.find("-Disclaimer")
        end = spiceusr_header.find("-Required_Reading", begin)
        return spiceusr_header[begin:end]

    def package_info(self):
        self.cpp_info.libs = ["cspice"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")

        if self.options.utilities:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info("Appending PATH environment variable: {}".format(bin_path))
            self.env_info.PATH.append(bin_path)
