from conans import ConanFile, CMake, tools
from conans.errors import ConanException
import requests

required_conan_version = ">=1.33.0"


class LibnovaConan(ConanFile):
    name = "libnova"
    description = (
        "libnova is a general purpose, double precision, celestial mechanics, "
        "astrometry and astrodynamics library."
    )
    license = "LGPL-2.0-only"
    topics = ("libnova", "celestial-mechanics", "astrometry", "astrodynamics")
    homepage = "https://sourceforge.net/projects/libnova"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    exports_sources = ["CMakeLists.txt", "patches/**"]
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
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    @staticmethod
    def _generate_git_tag_archive_sourceforge(url, timeout=10, retry=2):
        def try_post(retry_count):
            try:
                requests.post(url, timeout=timeout)
            except:
                if retry_count < retry:
                    try_post(retry_count + 1)
                else:
                    raise ConanException("All the attempt to generate archive url have failed.")
        try_post(0)

    def source(self):
        # Generate the archive download link
        self._generate_git_tag_archive_sourceforge(self.conan_data["sources"][self.version]["url"]["post"])

        # Download archive
        archive_url = self.conan_data["sources"][self.version]["url"]["archive"]
        sha256 = self.conan_data["sources"][self.version]["sha256"]
        tools.get(url=archive_url, sha256=sha256, destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["BUILD_SHARED_LIBRARY"] = self.options.shared
        self._cmake.configure()
        return self._cmake

    def package(self):
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        postfix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.libs = ["nova{}".format(postfix)]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
