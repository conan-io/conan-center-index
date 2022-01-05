from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os

required_conan_version = ">=1.33.0"


class CspiceConan(ConanFile):
    name = "cspice"
    description = "NASA C SPICE library"
    license = "TSPA"
    topics = ("spice", "naif", "kernels", "space", "nasa", "jpl", "spacecraft", "planet", "robotics")
    homepage = "https://naif.jpl.nasa.gov/naif/toolkit.html"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "utilities": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "utilities": True,
    }

    generators = "cmake"
    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        self.copy("CMakeLists.txt")
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def validate(self):
        sources_url_per_triplet = self.conan_data["sources"][self.version]["url"]
        the_os = self._get_os_or_subsystem()
        if the_os not in sources_url_per_triplet:
            raise ConanInvalidConfiguration(
                "cspice N{} does not support {0}".format(self.version, the_os)
            )
        compiler = str(self.settings.compiler)
        if compiler not in sources_url_per_triplet[the_os]:
            raise ConanInvalidConfiguration(
                "cspice N{} does not support {0} on {1}".format(self.version, compiler, the_os)
            )
        arch = str(self.settings.arch)
        if arch not in sources_url_per_triplet[the_os][compiler]:
            raise ConanInvalidConfiguration(
                "cspice N{} does not support {0} on {1} {2}".format(self.version, compiler, the_os, arch)
            )

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
        self._patch_sources()
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
        tools.rename(self.name, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        # TODO: find a more elegant patch, there is likely some conflict between
        #       fio.h and io.h in 0067 but the diff with 0066 is not obvious.
        if str(self.settings.compiler) in ["Visual Studio", "msvc"] and self.version == "0067":
            tools.replace_in_file(os.path.join(self._source_subfolder, "src", "cspice", "fio.h"),
                                  "extern int isatty(int);", "")

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
