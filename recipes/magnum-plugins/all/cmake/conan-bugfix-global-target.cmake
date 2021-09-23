# If using 'cmake_find_package', all the components are being added to the global
# target unconditionally. See generated FindMagnum.cmake file:
# 
# if(NOT ${CMAKE_VERSION} VERSION_LESS "3.0")
#     if(NOT TARGET Magnum::Magnum)
#         add_library(Magnum::Magnum INTERFACE IMPORTED)
#     endif()
#     set_property(TARGET Magnum::Magnum APPEND PROPERTY
#                  INTERFACE_LINK_LIBRARIES "${Magnum_COMPONENTS}")
# endif()
# 
# but it doesn't add the library directories and the linker will fail.
# 
# Here we fix this bug (breaking change) for this recipe, we just override
# the list of targets again.
# 


if(NOT ${CMAKE_VERSION} VERSION_LESS "3.0")
    if(TARGET MagnumPlugins::MagnumPlugins)
        set_target_properties(MagnumPlugins::MagnumPlugins PROPERTIES INTERFACE_LINK_LIBRARIES
            "${MagnumPlugins_MagnumPlugins_LINK_LIBS};${MagnumPlugins_MagnumPlugins_LINKER_FLAGS_LIST}")
    endif()
endif()
