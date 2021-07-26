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

    _autotools = None

    def package_id(self):
        self.info.header_only()

    def build_requirements(self):
        if tools.os_info.is_windows:
            if "CONAN_MAKE_PROGRAM" not in os.environ:
                self.build_requires("make/4.2.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version], strip_root=True)

    def _configure_autotools(self):
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self)
        return self._autotools

    def build(self):
        autotools = self._configure_autotools()
        autotools.make()

    def package(self):
        # Extract the License/s from the header to a file
        tmp = tools.load(os.path.join("include", "ffnvcodec", "nvEncodeAPI.h"))
        license_contents = tmp[2:tmp.find("*/", 1)] # The license begins with a C comment /* and ends with */
        tools.save(os.path.join(self.package_folder, "licenses", "LICENSE"), license_contents)

        autotools = self._configure_autotools()
        vars = autotools.vars
        autotools.install(args=["PREFIX={}".format(self.package_folder)])

        tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.names["pkg_config"] = "ffnvcodec"
