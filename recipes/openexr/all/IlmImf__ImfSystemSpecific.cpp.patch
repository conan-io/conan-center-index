--- IlmImf/ImfSystemSpecific.cpp.orig	2017-11-17 23:00:24 UTC
+++ IlmImf/ImfSystemSpecific.cpp
@@ -44,11 +44,23 @@ namespace {
     // Helper functions for gcc + SSE enabled
     void cpuid(int n, int &eax, int &ebx, int &ecx, int &edx)
     {
+#if __i386__
         __asm__ __volatile__ (
-            "cpuid"
-            : /* Output  */ "=a"(eax), "=b"(ebx), "=c"(ecx), "=d"(edx) 
-            : /* Input   */ "a"(n)
+            "xchgl %%ebx,%k1\n"
+            "cpuid\n"
+            "xchgl %%ebx,%k1" \
+            : /* Output  */ "=a"(eax), "=&r"(ebx), "=c"(ecx), "=d"(edx)
+            : /* Input   */ "0"(n)
             : /* Clobber */);
+#else
+        __asm__ __volatile__ (
+            "xchgq %%rbx,%q1\n"
+            "cpuid\n"
+            "xchgq %%rbx,%q1" \
+            : /* Output  */ "=a"(eax), "=&r"(ebx), "=c"(ecx), "=d"(edx)
+            : /* Input   */ "0"(n)
+            : /* Clobber */);
+#endif
     }
 
 #else // IMF_HAVE_SSE2 && __GNUC__
