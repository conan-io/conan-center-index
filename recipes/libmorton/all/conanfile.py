from conans import ConanFile, tools
import os

required_conan_version = ">=1.43.0"


class LibmortonConan(ConanFile):
    name = "libmorton"
    description = "C++ header-only library with methods to efficiently " \
                  "encode/decode 64, 32 and 16-bit Morton codes and coordinates, in 2D and 3D."
    license = "MIT"
    topics = ("libmorton", "morton", "encoding", "decoding")
    homepage = "https://github.com/Forceflow/libmorton"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def export_sources(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            self.copy(patch["patch_file"])

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.files.get(self, **self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.files.patch(self, **patch)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        if tools.Version(self.version) < "0.2.7":
            src_hdrs = os.path.join(self._source_subfolder, "libmorton", "include")
        elif tools.Version(self.version) < "0.2.8":
            src_hdrs = os.path.join(self._source_subfolder, "libmorton")
        else:
            src_hdrs = os.path.join(self._source_subfolder, "include", "libmorton")
        self.copy("*.h", dst=os.path.join("include", "libmorton"), src=src_hdrs)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libmorton")
        self.cpp_info.set_property("cmake_target_name", "libmorton::libmorton")
        self.cpp_info.set_property("pkg_config_name", "libmorton")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["m"]
