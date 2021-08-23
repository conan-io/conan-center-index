project('test_wayland_protocols', 'c')

wayland_client_dep = dependency('wayland-client', version: '>=1.2.0', required: true)
wayland_protocols_dep = dependency('wayland-protocols', required: true)
wayland_protocols_datadir = wayland_protocols_dep.get_pkgconfig_variable('pkgdatadir')

wayland_scanner = find_program('wayland-scanner')
wayland_scanner_code_gen = generator(
    wayland_scanner,
    output: '@BASENAME@-protocol.c',
    arguments: ['code', '@INPUT@', '@OUTPUT@'],
)
wayland_scanner_client_header_gen = generator(
    wayland_scanner,
    output: '@BASENAME@-client-protocol.h',
    arguments: ['client-header', '@INPUT@', '@OUTPUT@'],
)

xdg_shell_xml = wayland_protocols_datadir/'stable/xdg-shell/xdg-shell.xml'

xdg_shell_sources = [
    wayland_scanner_code_gen.process(xdg_shell_xml),
    wayland_scanner_client_header_gen.process(xdg_shell_xml),
]

executable('test_package',
            'test_package.c',
            xdg_shell_sources,
            dependencies: [wayland_client_dep],
            link_args : '-lrt')
