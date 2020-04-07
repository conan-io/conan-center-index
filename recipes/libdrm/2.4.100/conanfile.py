from conans import ConanFile, Meson, tools
import os
import shutil


class LibnameConan(ConanFile):
    name = "libdrm"
    description = "User space library for accessing the Direct Rendering Manager, on operating systems that support the ioctl interface"
    topics = ("conan", "libdrm", "graphics")
    url = "https://github.com/bincrafters/conan-libdrm"
    homepage = "https://gitlab.freedesktop.org/mesa/drm"
    license = "MIT"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "libkms": [True, False],
        "intel": [True, False],
        "radeon": [True, False],
        "amdgpu": [True, False],
        "nouveau": [True, False],
        "vmwgfx": [True, False],
        "omap": [True, False],
        "exynos": [True, False],
        "freedreno": [True, False],
        "tegra": [True, False],
        "vc4": [True, False],
        "etnaviv": [True, False],
        "valgrind": [True, False],
        "freedreno-kgsl": [True, False],
        "udev": [True, False]
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "libkms": True,
        "intel": True,
        "radeon": True,
        "amdgpu": True,
        "nouveau": True,
        "vmwgfx": True,
        "omap": False,
        "exynos": False,
        "freedreno": True,
        "tegra": False,
        "vc4": True,
        "etnaviv": False,
        "valgrind": False,
        "freedreno-kgsl": False,
        "udev": False
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def build_requirements(self):
        if not tools.which("meson"):
            self.build_requires("meson/0.53.2")
        if not tools.which('pkg-config'):
            self.build_requires('pkg-config_installer/0.29.2@bincrafters/stable')
    
    def requirements(self):
        if self.options.intel:
            self.requires("libpciaccess/0.16@bincrafters/stable")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC
    
    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        
        defs={
            "cairo-tests" : "false",
            "install-test-programs": "false"
        }
        for o in ["libkms", "intel", "radeon", "amdgpu","nouveau", "vmwgfx", "omap", "exynos",
                  "freedreno", "tegra", "vc4", "etnaviv", "valgrind", "freedreno-kgsl", "udev"]:
            defs[o] = "true" if getattr(self.options, o) else "false"            
            
        meson.configure(
            defs = defs,
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)
        return meson

    def build(self):
        def _get_pc_files(package):
            if package in self.deps_cpp_info.deps:
                lib_path = self.deps_cpp_info[package].rootpath
                for dirpath, _, filenames in os.walk(lib_path):
                    for filename in filenames:
                        if filename.endswith('.pc'):
                            shutil.copyfile(os.path.join(dirpath, filename), filename)
                            tools.replace_prefix_in_pc_file(filename, lib_path)
                for dep in self.deps_cpp_info[package].public_deps:
                    _get_pc_files(dep)
        _get_pc_files('libpciaccess')
        meson = self._configure_meson()
        meson.build()

    def package(self):
        meson = self._configure_meson()
        meson.install()

    def package_info(self):
        self.cpp_info.includedirs.append(os.path.join('include', 'libdrm'))
        self.cpp_info.includedirs.append(os.path.join('include', 'libkms'))
        self.cpp_info.libs = tools.collect_libs(self)
