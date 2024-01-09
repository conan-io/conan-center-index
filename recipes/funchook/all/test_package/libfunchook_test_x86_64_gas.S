	.text

#if defined(__MINGW32__)
	.def	get_val_in_dll;	.scl	2;	.type	32;	.endef
#elif defined(__APPLE__)
#define get_val_in_dll _get_val_in_dll
#define call_get_val_in_dll _call_get_val_in_dll
#define jump_get_val_in_dll _jump_get_val_in_dll
#else
#define get_val_in_dll get_val_in_dll@PLT
#endif

	.p2align 4,,15
	.globl	call_get_val_in_dll
#if defined(__MINGW32__)
	.def	call_get_val_in_dll;	.scl	2;	.type	32;	.endef
#elif !defined(__APPLE__)
	.type	call_get_val_in_dll, @function
#endif
call_get_val_in_dll:
	call	get_val_in_dll
	ret

	.p2align 4,,15
	.globl	jump_get_val_in_dll
#if defined(__MINGW32__)
	.def	jump_get_val_in_dll;	.scl	2;	.type	32;	.endef
#elif !defined(__APPLE__)
	.type	jump_get_val_in_dll, @function
#endif
jump_get_val_in_dll:
	jmp	get_val_in_dll

#if defined(__MINGW32__)
	.section .drectve
	.ascii " -export:\"jump_get_val_in_dll\""
	.ascii " -export:\"call_get_val_in_dll\""
#endif
