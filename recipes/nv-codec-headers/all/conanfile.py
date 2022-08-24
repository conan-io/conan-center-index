from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os

required_conan_version = ">=1.35.0"

class FFNvEncHeaders(ConanFile):
    name = "nv-codec-headers"
    description = "FFmpeg version of headers required to interface with Nvidia's codec APIs"
    topics = ("ffmpeg", "video", "nvidia", "headers")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/FFmpeg/nv-codec-headers"
    license = "MIT"
    settings = "os"

    _autotools = None
    _source_subfolder = "source_subfolder"

    @property
    def _settings_build(self):
        return getattr(self, "settings_build", self.settings)

    def build_requirements(self):
        if self._settings_build.os == "Windows":
            if "CONAN_MAKE_PROGRAM" not in os.environ:
                self.build_requires("make/4.2.1")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version], strip_root=True, destination=self._source_subfolder)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
            autotools.make()

    def _extract_license(self):
        # Extract the License/s from the header to a file
        tmp = tools.files.load(self, os.path.join(self._source_subfolder, "include", "ffnvcodec", "nvEncodeAPI.h"))
        license_contents = tmp[2:tmp.find("*/", 1)] # The license begins with a C comment /* and ends with */
        tools.files.save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

    def package(self):
        self._extract_license()

        autotools = self._configure_autotools()
        with tools.chdir(os.path.join(self.build_folder, self._source_subfolder)):
            autotools.install(args=["PREFIX={}".format(self.package_folder)])

        tools.files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "ffnvcodec"
