if(USEARCH_USE_FP16LIB)
    find_package(fp16 REQUIRED CONFIG)
    link_libraries(fp16::fp16)
endif()
