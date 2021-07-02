
# Generate requested libraries:
#   - gsoap
#   - gsoap++
#   - gsoapssl
#   - gsoapssl++


# C library
set(SRCS_GSOAP_C
    ${GSOAP_PATH}/gsoap/stdsoap2.c
    ${GSOAP_PATH}/gsoap/dom.c
)
set_source_files_properties(${SRCS_GSOAP_C} PROPERTIES LANGUAGE C)
add_library(gsoap ${SRCS_GSOAP_C} ${GSOAP_PATH}/gsoap/stdsoap2.h)
set_target_properties(gsoap PROPERTIES
    COMPILE_PDB_OUTPUT_DIRECTORY bin
    PDB_OUTPUT_DIRECTORY bin
    PUBLIC_HEADER ${GSOAP_PATH}/gsoap/stdsoap2.h
    LINKER_LANGUAGE C
    )
install(TARGETS gsoap
            RUNTIME DESTINATION bin
            LIBRARY DESTINATION lib
            ARCHIVE DESTINATION lib
            PUBLIC_HEADER DESTINATION include
            )


# CXX library
set(SRCS_GSOAP_CXX
    ${GSOAP_PATH}/gsoap/stdsoap2.cpp
    ${GSOAP_PATH}/gsoap/dom.cpp
)
set_source_files_properties(${SRCS_GSOAP_CXX} PROPERTIES LANGUAGE CXX)
add_library(gsoap++ ${SRCS_GSOAP_CXX} ${GSOAP_PATH}/gsoap/stdsoap2.h)
set_target_properties(gsoap++ PROPERTIES
    COMPILE_PDB_OUTPUT_DIRECTORY bin
    PDB_OUTPUT_DIRECTORY bin
    PUBLIC_HEADER ${GSOAP_PATH}/gsoap/stdsoap2.h
    LINKER_LANGUAGE CXX
    )
install(TARGETS gsoap++
            RUNTIME DESTINATION bin
            LIBRARY DESTINATION lib
            ARCHIVE DESTINATION lib
            PUBLIC_HEADER DESTINATION include
            )

# Add SSL if requested
if(${WITH_OPENSSL})

    target_include_directories(gsoap PRIVATE ${GSOAP_PATH}/gsoap/plugin)
    target_compile_definitions(gsoap PUBLIC WITH_OPENSSL WITH_GZIP)
    set_target_properties(gsoap PROPERTIES OUTPUT_NAME gsoapssl)
    target_link_libraries(gsoap ${CONAN_LIBS})

    target_include_directories(gsoap++ PRIVATE ${GSOAP_PATH}/gsoap/plugin)
    target_compile_definitions(gsoap++ PUBLIC WITH_OPENSSL WITH_GZIP)
    set_target_properties(gsoap++ PROPERTIES OUTPUT_NAME gsoapssl++)
    target_link_libraries(gsoap++ ${CONAN_LIBS})
endif()
if(${WITH_IPV6})
    target_compile_definitions(gsoap PUBLIC WITH_IPV6)
    target_compile_definitions(gsoap++ PUBLIC WITH_IPV6)
endif()
if(${WITH_COOKIES})
    target_compile_definitions(gsoap PUBLIC WITH_COOKIES)
    target_compile_definitions(gsoap++ PUBLIC WITH_COOKIES)
endif()
if(${WITH_C_LOCALE})
    target_compile_definitions(gsoap PUBLIC WITH_C_LOCALE)
    target_compile_definitions(gsoap++ PUBLIC WITH_C_LOCALE)
endif()
