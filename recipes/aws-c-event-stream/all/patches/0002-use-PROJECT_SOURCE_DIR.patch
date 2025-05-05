--- CMakeLists.txt
+++ CMakeLists.txt
@@ -70,25 +70,25 @@
     ${AWS_EVENT_STREAM_SRC}
 )

-add_library(${CMAKE_PROJECT_NAME} ${EVENT_STREAM_SRC})
-aws_set_common_properties(${CMAKE_PROJECT_NAME})
-aws_add_sanitizers(${CMAKE_PROJECT_NAME})
-aws_prepare_symbol_visibility_args(${CMAKE_PROJECT_NAME} "AWS_EVENT_STREAM")
+add_library(${PROJECT_NAME} ${EVENT_STREAM_SRC})
+aws_set_common_properties(${PROJECT_NAME})
+aws_add_sanitizers(${PROJECT_NAME})
+aws_prepare_symbol_visibility_args(${PROJECT_NAME} "AWS_EVENT_STREAM")

-target_include_directories(${CMAKE_PROJECT_NAME} PUBLIC
+target_include_directories(${PROJECT_NAME} PUBLIC
     $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
     $<INSTALL_INTERFACE:include>)


-set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES VERSION 1.0.0)
-set_target_properties(${CMAKE_PROJECT_NAME} PROPERTIES SOVERSION 0unstable)
+set_target_properties(${PROJECT_NAME} PROPERTIES VERSION 1.0.0)
+set_target_properties(${PROJECT_NAME} PROPERTIES SOVERSION 0unstable)

 find_package(aws-c-common REQUIRED)
 find_package(aws-checksums REQUIRED)

-target_link_libraries(${CMAKE_PROJECT_NAME} PUBLIC AWS::aws-c-common AWS::aws-checksums)
+target_link_libraries(${PROJECT_NAME} PUBLIC AWS::aws-c-common AWS::aws-checksums)

-aws_prepare_shared_lib_exports(${CMAKE_PROJECT_NAME})
+aws_prepare_shared_lib_exports(${PROJECT_NAME})

 install(FILES ${AWS_EVENT_STREAM_HEADERS}
     DESTINATION "include/aws/event-stream"
@@ -100,17 +100,17 @@
    set (TARGET_DIR "static")
 endif()

-install(EXPORT "${CMAKE_PROJECT_NAME}-targets"
-    DESTINATION "${LIBRARY_DIRECTORY}/${CMAKE_PROJECT_NAME}/cmake/${TARGET_DIR}/"
+install(EXPORT "${PROJECT_NAME}-targets"
+    DESTINATION "${LIBRARY_DIRECTORY}/${PROJECT_NAME}/cmake/${TARGET_DIR}/"
     NAMESPACE AWS::
     COMPONENT Development)

-configure_file("cmake/${CMAKE_PROJECT_NAME}-config.cmake"
-    "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}-config.cmake"
+configure_file("cmake/${PROJECT_NAME}-config.cmake"
+    "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-config.cmake"
     @ONLY)

-install(FILES "${CMAKE_CURRENT_BINARY_DIR}/${CMAKE_PROJECT_NAME}-config.cmake"
-    DESTINATION "${LIBRARY_DIRECTORY}/${CMAKE_PROJECT_NAME}/cmake/"
+install(FILES "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}-config.cmake"
+    DESTINATION "${LIBRARY_DIRECTORY}/${PROJECT_NAME}/cmake/"
     COMPONENT Development)


