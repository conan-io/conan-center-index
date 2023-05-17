--- cmake/FindJemalloc.cmake
+++ cmake/FindJemalloc.cmake
@@ -10,10 +10,10 @@
 find_path(JEMALLOC_INCLUDE_DIR
   NAMES jemalloc/jemalloc.h
   HINTS ${PC_JEMALLOC_INCLUDE_DIRS}
 )
 find_library(JEMALLOC_LIBRARY
-  NAMES jemalloc
+  NAMES jemalloc jemalloc_s jemalloc_pic
   HINTS ${PC_JEMALLOC_LIBRARY_DIRS}
 )

 if(JEMALLOC_INCLUDE_DIR)
