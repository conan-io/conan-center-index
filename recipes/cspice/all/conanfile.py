from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, chdir, copy, download, get, load, rename, rmdir, save
import os

required_conan_version = ">=1.47.0"


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

    def export_sources(self):
        copy(self, "CMakeLists.txt", self.recipe_folder, self.export_sources_folder)
        for p in self.conan_data.get("patches", {}).get(self.version, []):
            copy(self, p["patch_file"], self.recipe_folder, self.export_sources_folder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            del self.options.fPIC
        try:
            del self.settings.compiler.libcxx
        except Exception:
            pass
        try:
            del self.settings.compiler.cppstd
        except Exception:
            pass

    def validate(self):
        sources_url_per_triplet = self.conan_data["sources"][self.version]
        host_os = self._get_os_or_subsystem()
        if host_os not in sources_url_per_triplet:
            raise ConanInvalidConfiguration(
                f"cspice N{self.version} does not support {host_os}",
            )
        compiler = str(self.info.settings.compiler)
        if compiler not in sources_url_per_triplet[host_os]:
            raise ConanInvalidConfiguration(
                f"cspice N{self.version} does not support {compiler} on {host_os}",
            )
        arch = str(self.info.settings.arch)
        if arch not in sources_url_per_triplet[host_os][compiler]:
            raise ConanInvalidConfiguration(
                f"cspice N{self.version} does not support {compiler} on {host_os} {arch}",
            )

    def _get_os_or_subsystem(self):
        if self.settings.os == "Windows" and self.settings.os.subsystem != "None":
            os_or_subsystem = str(self.settings.os.subsystem)
        else:
            os_or_subsystem = str(self.settings.os)
        return os_or_subsystem

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        pass

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CSPICE_SRC_DIR"] = self.source_folder.replace("\\", "/")
        tc.variables["CSPICE_BUILD_UTILITIES"] = self.options.utilities
        tc.generate()

    @property
    def _parent_source_folder(self):
        return os.path.join(self.source_folder, os.pardir)

    def _get_sources(self):
        with chdir(self, self._parent_source_folder):
            host_os = self._get_os_or_subsystem()
            compiler = str(self.settings.compiler)
            arch = str(self.settings.arch)
            data = self.conan_data["sources"][self.version][host_os][compiler][arch]
            url = data["url"]
            if url.endswith(".tar.Z"): # Python doesn't have any module to uncompress .Z files
                tarball = os.path.basename(url)
                download(self, url, tarball, sha256=data["sha256"])
                self.run(f"zcat {tarball} | tar -xf -")
                os.remove(tarball)
            else:
                get(self, **data)
            rmdir(self, self.source_folder)
            rename(self, "cspice", os.path.basename(self.source_folder))

    def build(self):
        self._get_sources()
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure(build_script_folder=self._parent_source_folder)
        cmake.build()

    def package(self):
        save(self, os.path.join(self.package_folder, "licenses", "LICENSE"), self._extract_license())
        cmake = CMake(self)
        cmake.install()

    def _extract_license(self):
        spiceusr_header = load(self, os.path.join(self.source_folder, "include", "SpiceUsr.h"))
        begin = spiceusr_header.find("-Disclaimer")
        end = spiceusr_header.find("-Required_Reading", begin)
        return spiceusr_header[begin:end]

    def package_info(self):
        self.cpp_info.libs = ["cspice"]
        if self.settings.os == "Linux":
            self.cpp_info.system_libs.append("m")

        if self.options.utilities:
            bin_path = os.path.join(self.package_folder, "bin")
            self.output.info(f"Appending PATH environment variable: {bin_path}")
            self.env_info.PATH.append(bin_path)
