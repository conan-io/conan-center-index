#if defined(_WIN32) || defined(__APPLE__)
#define get_val_in_exe _get_val_in_exe
#define int_val _int_val
#define x86_test_error_jump1 _x86_test_error_jump1
#define x86_test_error_jump2 _x86_test_error_jump2
#define x86_test_call_get_pc_thunk_ax _x86_test_call_get_pc_thunk_ax
#define x86_test_call_get_pc_thunk_bx _x86_test_call_get_pc_thunk_bx
#define x86_test_call_get_pc_thunk_cx _x86_test_call_get_pc_thunk_cx
#define x86_test_call_get_pc_thunk_dx _x86_test_call_get_pc_thunk_dx
#define x86_test_call_get_pc_thunk_si _x86_test_call_get_pc_thunk_si
#define x86_test_call_get_pc_thunk_di _x86_test_call_get_pc_thunk_di
#define x86_test_call_get_pc_thunk_bp _x86_test_call_get_pc_thunk_bp
#define x86_test_call_and_pop_eax _x86_test_call_and_pop_eax
#define x86_test_call_and_pop_ebx _x86_test_call_and_pop_ebx
#define x86_test_call_and_pop_ecx _x86_test_call_and_pop_ecx
#define x86_test_call_and_pop_edx _x86_test_call_and_pop_edx
#define x86_test_call_and_pop_esi _x86_test_call_and_pop_esi
#define x86_test_call_and_pop_edi _x86_test_call_and_pop_edi
#define x86_test_call_and_pop_ebp _x86_test_call_and_pop_ebp
#endif
	.text

	.p2align 4,,15
	.globl	x86_test_error_jump1
x86_test_error_jump1:
	jmp	label_1 /* jump whose size is not 32-bit */
label_1:
#ifdef __PIE__
	call	x86.get_pc_thunk.ax
	addl	$_GLOBAL_OFFSET_TABLE_, %eax
	mov	int_val@GOT(%eax), %eax
#elif defined __APPLE__
	call	x86.get_pc_thunk.ax
label_1_1:
	movl	L_int_val$non_lazy_ptr-label_1_1(%eax), %eax
#else
	mov	int_val, %eax
#endif
	ret

	.p2align 4,,15
	.globl	x86_test_error_jump2
x86_test_error_jump2:
	xorl	%eax, %eax
label_2:
	nop
	nop
	nop
	nop
	jnz	label_2 /* jump to hot-patched region */
#ifdef __PIE__
	call	x86.get_pc_thunk.ax
	addl	$_GLOBAL_OFFSET_TABLE_, %eax
	mov	int_val@GOT(%eax), %eax
#elif defined __APPLE__
	call	x86.get_pc_thunk.ax
label_2_1:
	movl	L_int_val$non_lazy_ptr-label_2_1(%eax), %eax
#else
	mov	int_val, %eax
#endif
	ret

#ifndef _WIN32
	.p2align 4,,15
	.globl	x86_test_call_get_pc_thunk_ax
x86_test_call_get_pc_thunk_ax:
	call	x86.get_pc_thunk.ax
#ifdef __APPLE__
L_ax:
	movl	L_int_val$non_lazy_ptr-L_ax(%eax), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_, %eax
	movl	int_val@GOT(%eax), %eax
#endif
	movl	(%eax), %eax
	ret

	.p2align 4,,15
	.globl	x86_test_call_get_pc_thunk_bx
x86_test_call_get_pc_thunk_bx:
	pushl	%ebx
	call	x86.get_pc_thunk.bx
#ifdef __APPLE__
L_bx:
	movl	L_int_val$non_lazy_ptr-L_bx(%ebx), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_, %ebx
	movl	int_val@GOT(%ebx), %eax
#endif
	movl	(%eax), %eax
	popl	%ebx
	ret

	.p2align 4,,15
	.globl	x86_test_call_get_pc_thunk_cx
x86_test_call_get_pc_thunk_cx:
	call	x86.get_pc_thunk.cx
#ifdef __APPLE__
L_cx:
	movl	L_int_val$non_lazy_ptr-L_cx(%ecx), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_, %ecx
	movl	int_val@GOT(%ecx), %eax
#endif
	movl	(%eax), %eax
	ret

	.p2align 4,,15
	.globl	x86_test_call_get_pc_thunk_dx
x86_test_call_get_pc_thunk_dx:
	call	x86.get_pc_thunk.dx
#ifdef __APPLE__
L_dx:
	movl	L_int_val$non_lazy_ptr-L_dx(%edx), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_, %edx
	movl	int_val@GOT(%edx), %eax
#endif
	movl	(%eax), %eax
	ret

	.p2align 4,,15
	.globl	x86_test_call_get_pc_thunk_si
x86_test_call_get_pc_thunk_si:
	pushl	%esi
	call	x86.get_pc_thunk.si
#ifdef __APPLE__
L_si:
	movl	L_int_val$non_lazy_ptr-L_si(%esi), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_, %esi
	movl	int_val@GOT(%esi), %eax
#endif
	movl	(%eax), %eax
	popl	%esi
	ret

	.p2align 4,,15
	.globl	x86_test_call_get_pc_thunk_di
x86_test_call_get_pc_thunk_di:
	pushl	%edi
	call	x86.get_pc_thunk.di
#ifdef __APPLE__
L_di:
	movl	L_int_val$non_lazy_ptr-L_di(%edi), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_, %edi
	movl	int_val@GOT(%edi), %eax
#endif
	movl	(%eax), %eax
	popl	%edi
	ret

	.p2align 4,,15
	.globl	x86_test_call_get_pc_thunk_bp
x86_test_call_get_pc_thunk_bp:
	pushl	%ebp
	call	x86.get_pc_thunk.bp
#ifdef __APPLE__
L_bp:
	movl	L_int_val$non_lazy_ptr-L_bp(%ebp), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_, %ebp
	movl	int_val@GOT(%ebp), %eax
#endif
	movl	(%eax), %eax
	popl	%ebp
	ret

	.p2align 4,,15
x86.get_pc_thunk.ax:
	movl (%esp), %eax
	ret

	.p2align 4,,15
x86.get_pc_thunk.bx:
	movl (%esp), %ebx
	ret

	.p2align 4,,15
x86.get_pc_thunk.cx:
	movl (%esp), %ecx
	ret

	.p2align 4,,15
x86.get_pc_thunk.dx:
	movl (%esp), %edx
	ret

	.p2align 4,,15
x86.get_pc_thunk.si:
	movl (%esp), %esi
	ret

	.p2align 4,,15
x86.get_pc_thunk.di:
	movl (%esp), %edi
	ret

	.p2align 4,,15
x86.get_pc_thunk.bp:
	movl (%esp), %ebp
	ret

	.p2align 4,,15
	.globl	x86_test_call_and_pop_eax
x86_test_call_and_pop_eax:
	call	L_call_and_pop_eax
L_call_and_pop_eax:
	popl	%eax
#ifdef __APPLE__
	movl	L_int_val$non_lazy_ptr-L_call_and_pop_eax(%eax), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_+1, %eax
	movl	int_val@GOT(%eax), %eax
#endif
	movl	(%eax), %eax
	ret

	.p2align 4,,15
	.globl	x86_test_call_and_pop_ebx
x86_test_call_and_pop_ebx:
	pushl	%ebx
	call	L_call_and_pop_ebx
L_call_and_pop_ebx:
	popl	%ebx
#ifdef __APPLE__
	movl	L_int_val$non_lazy_ptr-L_call_and_pop_ebx(%ebx), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_+1, %ebx
	movl	int_val@GOT(%ebx), %eax
#endif
	movl	(%eax), %eax
	popl	%ebx
	ret

	.p2align 4,,15
	.globl	x86_test_call_and_pop_ecx
x86_test_call_and_pop_ecx:
	call	L_call_and_pop_ecx
L_call_and_pop_ecx:
	popl	%ecx
#ifdef __APPLE__
	movl	L_int_val$non_lazy_ptr-L_call_and_pop_ecx(%ecx), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_+1, %ecx
	movl	int_val@GOT(%ecx), %eax
#endif
	movl	(%eax), %eax
	ret

	.p2align 4,,15
	.globl	x86_test_call_and_pop_edx
x86_test_call_and_pop_edx:
	call	L_call_and_pop_edx
L_call_and_pop_edx:
	popl	%edx
#ifdef __APPLE__
	movl	L_int_val$non_lazy_ptr-L_call_and_pop_edx(%edx), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_+1, %edx
	movl	int_val@GOT(%edx), %eax
#endif
	movl	(%eax), %eax
	ret

	.p2align 4,,15
	.globl	x86_test_call_and_pop_esi
x86_test_call_and_pop_esi:
	pushl	%esi
	call	L_call_and_pop_esi
L_call_and_pop_esi:
	popl	%esi
#ifdef __APPLE__
	movl	L_int_val$non_lazy_ptr-L_call_and_pop_esi(%esi), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_+1, %esi
	movl	int_val@GOT(%esi), %eax
#endif
	movl	(%eax), %eax
	popl	%esi
	ret

	.p2align 4,,15
	.globl	x86_test_call_and_pop_edi
x86_test_call_and_pop_edi:
	pushl	%edi
	call	L_call_and_pop_edi
L_call_and_pop_edi:
	popl	%edi
#ifdef __APPLE__
	movl	L_int_val$non_lazy_ptr-L_call_and_pop_edi(%edi), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_+1, %edi
	movl	int_val@GOT(%edi), %eax
#endif
	movl	(%eax), %eax
	popl	%edi
	ret

	.p2align 4,,15
	.globl	x86_test_call_and_pop_ebp
x86_test_call_and_pop_ebp:
	pushl	%ebp
	call	L_call_and_pop_ebp
L_call_and_pop_ebp:
	popl	%ebp
#ifdef __APPLE__
	movl	L_int_val$non_lazy_ptr-L_call_and_pop_ebp(%ebp), %eax
#else
	addl	$_GLOBAL_OFFSET_TABLE_+1, %ebp
	movl	int_val@GOT(%ebp), %eax
#endif
	movl	(%eax), %eax
	popl	%ebp
	ret

#endif

#ifdef __APPLE__
	.section	__IMPORT,__pointers,non_lazy_symbol_pointers
L_int_val$non_lazy_ptr:
	.indirect_symbol	_int_val
	.long	0
#endif
