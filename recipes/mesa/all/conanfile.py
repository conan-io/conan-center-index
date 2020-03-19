from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


dri_list = ['i915', 'i965', 'r100', 'r200', 'nouveau']
vk_list = ['amd', 'freedreno', 'intel']
gallium_list = ['kmsro', 'radeonsi', 'r300', 'r600', 'nouveau', 'freedreno',\
'swrast', 'v3d', 'vc4', 'etnaviv', 'tegra', 'i915', 'svga', 'virgl',\
'swr', 'panfrost', 'iris', 'lima', 'zink']
swr_list = ['avx', 'avx2', 'knl', 'skx']
tools_list = ['drm-shim', 'etnaviv', 'freedreno', 'glsl', 'intel', 'intel-ui', 'nir', 'nouveau', 'xvmc', 'lima']

class LibnameConan(ConanFile):
    name = "mesa"
    description = "Mesa is an OpenGL compatible 3D graphics library"
    topics = ("conan", "mesa", "OpenGL")
    url = "https://github.com/bincrafters/conan-mesa"
    homepage = "https://mesa.freedesktop.org"
    license = "MIT"
    generators = "pkg_config"

    # Options may need to change depending on the packaged library
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "opengl": [True, False],
        "egl": [True, False],
        "gles1": [True, False],
        "gles2": [True, False],
        'vk_intel': [True, False],
        'vk_amd': [True, False],
        'vk_freedreno': [True, False],
        'gallium_vdpau': [True, False],
        'gallium_xvmc': [True, False],
        'gallium_va': [True, False],
        'gallium_xa': [True, False],
        'gallium_nine': [True, False],
        'gallium_extra_hud': [True, False],
        'gallium_omx':['disabled', 'bellagio', 'tizonia'],
        'gallium_opencl': ['icd', 'standalone', 'disabled'],
        'opencl_spirv' : [True, False],
        'valgrind': [True, False],
        'libunwind': [True, False],
        'selinux': [True, False],
        'shader_cache': [True, False],
        'vulkan_overlay_layer': [True, False],
        'gbm': [True, False],
        'glvnd': [True, False],
        'glx_read_only_text': [True, False],
        'osmesa': ['none', 'classic', 'gallium'],
        'osmesa_bits': [8, 16, 32],
        'power8': [True, False],
        'glx_direct': [True, False],
    }
    options.update({"dri_%s" % driver: [True, False] for driver in dri_list})
    options.update({"vk_%s" % driver: [True, False] for driver in vk_list})
    options.update({"gallium_%s" % driver: [True, False] for driver in gallium_list})
    options.update({"swr_%s" % arch: [True, False] for arch in swr_list})
    options.update({"tool_%s" % tool: [True, False] for tool in tools_list})

    default_options = {
        "fPIC": True,
        "opengl": True,
        "egl": True,
        "gles1": False,
        "gles2": False,
        'gallium_vdpau': False,
        'gallium_xvmc': False,
        'gallium_va': False,
        'gallium_xa': False,
        'gallium_nine': False,
        'gallium_extra_hud': False,
        'gallium_omx':'disabled',
        'gallium_opencl':'disabled',
        'opencl_spirv' : False,
        'valgrind': False,
        'libunwind': True,
        'selinux': False,
        'shader_cache': True,
        'vulkan_overlay_layer': False,
        'gbm': True,
        'glvnd': False,
        'glx_read_only_text': False,
        'osmesa': 'none',
        'osmesa_bits': 8,
        'power8': False,
        'glx_direct': 'True',
        'libxcb:shared': True,
        'libx11:shared': True,
    }
    default_options.update({"dri_%s" % driver: True for driver in dri_list})
    default_options.update({"vk_%s" % driver: (driver not in ['freedreno', 'amd']) for driver in vk_list})
    default_options.update({"gallium_%s" % driver: (driver == 'swrast') for driver in gallium_list})
    default_options.update({"swr_%s" % arch: (arch in ['avx', 'avx2']) for arch in swr_list})
    default_options.update({"tool_%s" % tool: False for tool in tools_list})

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        "zlib/1.2.11",
    )

    # TODO - Packages required but not listed in this recipe
    # wayland-scanner (libwayland-dev on Ubuntu)
    # wayland-protocols (wayland-protocols on Ubuntu)
    # wayland-egl-backend (libwayland-egl-backend-dev on Ubuntu)
    # Python module mako

    @property
    def _with_any_opengl(self):
        return self.options.opengl or self.options.gles1 or self.options.gles2

    @property
    def _with_dri(self):
        for driver in dri_list:
            if getattr(self.options, 'dri_%s' % driver):
                return True
        return False

    @property
    def _with_any_vk(self):
        for driver in vk_list:
            if getattr(self.options, 'vk_%s' % driver):
                return True
        return False

    @property
    def _with_gallium(self):
        for driver in gallium_list:
            if getattr(self.options, 'gallium_%s' % driver):
                return True
        return False

    @property
    def _with_dri_platform (self):
        if tools.is_apple_os(self.settings.os):
            return 'apple'
        elif self.settings.os == 'Windows':
            return 'windows'
        elif self._with_any_vk:
            return 'drm'
        else:
            return 'none'

    @property
    def _system_has_kms_drm(self):
        return self.settings.os in ['Linux', 'FreeBSD', 'SunOS']

    @property
    def _with_dri2(self):
        return (self._with_dri or self._with_any_vk) and (self._with_dri_platform == 'drm')

    @property
    def _with_dri3(self):
        return self._system_has_kms_drm and self._with_dri2

    @property
    def _platforms(self):
        if self._system_has_kms_drm:
            return ['x11', 'drm', 'surfaceless'] #, 'wayland' TODO: Create package
        elif tools.is_apple_os(self.settings.os):
            return ['surfaceless'] # TODO: 'x11' when conan-x11 will be available and apple
        elif self.settings.os == 'Windows':
            return ['windows']
        else:
            raise ConanInvalidConfiguration('Unknown OS. Patches gladly accepted to fix this.')

    @property
    def _with_glx(self):
        if self._with_dri:
            return 'dri'
        elif self.settings.os == 'Windows':
            return 'disabled'
        elif self._with_gallium:
            # Even when building just gallium drivers the user probably wants dri
            return 'dri'
        elif 'x11' in self._platforms and self._with_any_opengl and not self._with_any_vk:
            # The automatic behavior should not be to turn on xlib based glx when
            # building only vulkan drivers
            return 'xlib'
        else:
            return 'disabled'

    @property
    def _with_xlib_lease(self):
        return 'x11' in self._platforms and 'drm' in self._platforms


    def build_requirements(self):
        if not tools.which("meson"):
            self.build_requires("meson/0.53.2")
        if not tools.which('pkg-config'):
            self.build_requires('pkg-config_installer/0.29.2@bincrafters/stable')
        if self._with_any_opengl:
            if not tools.which("bison"):
                self.build_requires("bison_installer/3.3.2@bincrafters/stable")
            if not tools.which("flex"):
                self.build_requires("flex_installer/2.6.4@bincrafters/stable")

    def configure(self):
        if self.settings.os not in ["Linux", "FreeBSD"]:
            self.options.libunwind = False
        if not self._system_has_kms_drm:
            self.options.gbm = False
            self.options.gallium_vdpau = False
            self.options.gallium_xvmc = False
            self.options.gallium_omx = 'disabled'
            self.options.gallium_va = False
            self.options.gallium_xa = False
        if self.settings.os == 'Windows':
            self.options.shader_cache = False
        if tools.is_apple_os(self.settings.os) or self.settings.os == 'Windows':
            self.options.egl = False
        if 'windows' in self._platforms:
            self.options.glvnd = False
        if 'x11' not in self._platforms:
            self.options.gallium_vdpau = False
            self.options.gallium_xvmc = False

    def requirements(self):
        if self.settings.os != 'Windows':
            self.requires("expat/2.2.9")
        if self.options.gallium_xvmc:
            self.requires('libxvmc/1.0.11@bincrafters/stable')
            self.requires('libxv/1.0.11@bincrafters/stable')
        if self._with_dri2 or self._with_dri3:
            self.requires("libdrm/2.4.100@bincrafters/stable")
        if self.options.vk_amd or self.options.gallium_radeonsi or self.options.gallium_opencl:
            self.requires("libelf/0.8.13")
        if self.options.libunwind:
            self.requires('libunwind/1.3.1')
        if self.options.selinux:
            self.requires('selinux/2.9@bincrafters/stable')
        if 'x11' in self._platforms:
            if self._with_glx == 'xlib' or self._with_glx == 'gallium-xlib':
                self.requires("libx11/1.6.8@bincrafters/stable")
                self.requires("libxext/1.3.4@bincrafters/stable")
                self.requires("libxcb/1.13.1@bincrafters/stable")
            elif self._with_glx == 'dri':
                self.requires("libx11/1.6.8@bincrafters/stable")
                self.requires("libxext/1.3.4@bincrafters/stable")
                self.requires("libxdamage/1.1.5@bincrafters/stable")
                self.requires("libxfixes/5.0.3@bincrafters/stable")
                self.requires("libxcb/1.13.1@bincrafters/stable")
            if self._with_any_vk or self._with_glx == 'dri' or self.options.egl or \
                    self.options.gallium_vdpau or self.options.gallium_xvmc or self.options.gallium_va or \
                    self.options.gallium_omx != 'disabled':
                self.requires("libxcb/1.13.1@bincrafters/stable")
            if self._with_any_vk or self.options.egl or (self._with_glx == 'dri' and self._with_dri_platform == 'drm'):
                self.requires("libxcb/1.13.1@bincrafters/stable")
                if self._with_dri3:
                    self.requires("libxshmfence/1.3@bincrafters/stable")
            if self._with_glx == 'dri' or self._with_glx == 'gallium-xlib':
                pass#self.requires('glproto/1.4.17@bincrafters/stable') TODO: create package in conan-x11

            if self._with_glx == 'dri':
                if self._with_dri_platform == 'drm':
                    #self.requires('dri2proto/2.8@bincrafters/stable') TODO: create package in conan-x11
                    self.requires("libxxf86vm/1.1.4@bincrafters/stable")

            if self.options.egl or \
                self.options.gallium_vdpau or self.options.gallium_xvmc or self.options.gallium_xa or\
                self.options.gallium_omx != 'disabled':
                self.requires("libxcb/1.13.1@bincrafters/stable")
            if self._with_xlib_lease:
                self.requires('libxrandr/1.5.2@bincrafters/stable')

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)


    def _configure_meson(self):
        for package in self.deps_cpp_info.deps:
            if package != 'libunwind':
                lib_path = self.deps_cpp_info[package].rootpath
                for dirpath, _, filenames in os.walk(lib_path):
                    for filename in filenames:
                        if filename.endswith('.pc'):
                            shutil.copyfile(os.path.join(dirpath, filename), filename)
                            tools.replace_prefix_in_pc_file(filename, lib_path)

        meson = Meson(self)
        meson.configure(
            defs={
                'llvm': 'false',
                'platforms': self._platforms,
                'valgrind': 'true' if self.options.valgrind else 'false',
                'libunwind': 'true' if self.options.libunwind else 'false',
                'dri3': 'true' if self._with_dri3 else 'false',
                'dri-drivers': [driver for driver in dri_list if getattr(self.options, 'dri_' + driver)],
                'gallium-drivers': [driver for driver in gallium_list if getattr(self.options, 'gallium_' + driver)],
                'gallium-vdpau': 'true' if self.options.gallium_vdpau else 'false',
                'gallium-xvmc': 'true' if self.options.gallium_xvmc else 'false',
                'gallium-omx': self.options.gallium_omx,
                'gallium-va': 'true' if self.options.gallium_va else 'false',
                'gallium-xa': 'true' if self.options.gallium_xa else 'false',
                'gallium-nine': 'true' if self.options.gallium_nine else 'false',
                'gallium-opencl': self.options.gallium_opencl,
                'opencl-spirv': 'true' if self.options.opencl_spirv else 'false',
                'gallium-extra-hud': 'true' if self.options.gallium_extra_hud else 'false',
                "vulkan-drivers": [driver for driver in vk_list if getattr(self.options, 'vk_' + driver)],
                'gles1': 'true' if self.options.gles1 else 'false',
                'gles2': 'true' if self.options.gles2 else 'false',
                'opengl': 'true' if self.options.opengl else 'false',
                'glx': self._with_glx,
                'egl': 'true' if self.options.egl else 'false',
                'xlib-lease': 'true' if self._with_xlib_lease else 'false',
                'shader-cache': 'true' if self.options.shader_cache else 'false',
                'vulkan-overlay-layer': 'true' if self.options.vulkan_overlay_layer else 'false',
                'gbm': 'true' if self.options.gbm else 'false',
                'glvnd': 'true' if self.options.glvnd else 'false',
                'glx-read-only-text': 'true' if self.options.glx_read_only_text else 'false',
                'osmesa': self.options.osmesa,
                'osmesa-bits': self.options.osmesa_bits,
                'swr-arches': [arch for arch in swr_list if getattr(self.options, 'swr_' + arch)],
                'tools': [tool for tool in tools_list if getattr(self.options, 'tool_' + tool)],
                'power8': 'true' if self.options.power8 else 'false',
                'glx-direct': 'true' if self.options.glx_direct else 'false',
            },
            source_folder=self._source_subfolder,
            build_folder=self._build_subfolder)
        return meson

    def build(self):
        tools.check_min_cppstd(self, "11")
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
    
    def package_id(self):
        del self.info.settings.compiler.cppstd

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.env_info.LIBGL_DRIVERS_PATH = os.path.join(self.package_folder, 'lib', 'dri')
