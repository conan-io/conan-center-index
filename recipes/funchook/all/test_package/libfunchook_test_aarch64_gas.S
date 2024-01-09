	.arch armv8-a
	.file	"libfunchook_test_aarch64_gas.S"
	.text
	.align	2
	.p2align 3,,7

test_data:
	.8byte 0x1020304050607080, 0x0102030405060708

call_get_val_in_dll:
	.global	call_get_val_in_dll
	.type	call_get_val_in_dll, %function
	stp	x29, x30, [sp, -16]!
	bl	get_val_in_dll
	ldp	x29, x30, [sp], 16
	ret

jump_get_val_in_dll:
	.global	jump_get_val_in_dll
	.type	jump_get_val_in_dll, %function
	b	get_val_in_dll

arm64_test_adr:
	.global	arm64_test_adr
	.type	arm64_test_adr, %function
	adr x9, test_data
	ldr x9, [x9]
	add x0, x0, x9
	ret

arm64_test_beq:
	.global	arm64_test_beq
	.type	arm64_test_beq, %function
	adds x0, x0, 1
	beq 1f
	sub x0, x0, 2
1:
	ret

arm64_test_bne:
	.global	arm64_test_bne
	.type	arm64_test_bne, %function
	adds x0, x0, 1
	bne 1f
	sub x0, x0, 2
1:
	ret


arm64_test_cbnz:
	.global	arm64_test_cbnz
	.type	arm64_test_cbnz, %function
	cbnz x0, 1f
	add x0, x0, 2
1:
	sub x0, x0, 1
	ret

arm64_test_cbz:
	.global	arm64_test_cbz
	.type	arm64_test_cbz, %function
	cbz x0, 1f
	add x0, x0, 2
1:
	sub x0, x0, 1
	ret

arm64_test_ldr_w:
	.global	arm64_test_ldr_w
	.type	arm64_test_ldr_w, %function
	ldr w9, test_data
	add x0, x0, x9
	ret

arm64_test_ldr_x:
	.global	arm64_test_ldr_x
	.type	arm64_test_ldr_x, %function
	ldr x9, test_data
	add x0, x0, x9
	ret

arm64_test_ldr_s:
	.global	arm64_test_ldr_s
	.type	arm64_test_ldr_s, %function
	ldr s16, test_data
	mov w9, v16.s[0]
	add x0, x0, x9
	ret

arm64_test_ldr_d:
	.global	arm64_test_ldr_d
	.type	arm64_test_ldr_d, %function
	ldr d16, test_data
	mov x9, v16.d[0]
	add x0, x0, x9
	ret

arm64_test_ldr_q:
	.global	arm64_test_ldr_q
	.type	arm64_test_ldr_q, %function
	ldr q16, test_data
	mov x9, v16.d[0]
	add x0, x0, x9
	mov x9, v16.d[1]
	add x0, x0, x9
	ret

arm64_test_prfm:
	.global	arm64_test_prfm
	.type	arm64_test_prfm, %function
	prfm pldl1keep, test_data
	ldr x9, test_data
	add x0, x0, x9
	ret

arm64_test_ldrsw:
	.global	arm64_test_ldrsw
	.type	arm64_test_ldrsw, %function
	ldrsw x9, 1f
	add x0, x0, x9
	ret

arm64_test_tbnz:
	.global	arm64_test_tbnz
	.type	arm64_test_tbnz, %function
	tbnz x0, 32, 1f
	add x0, x0, 2
1:
	sub x0, x0, 1
	ret

arm64_test_tbz:
	.global	arm64_test_tbz
	.type	arm64_test_tbz, %function
	tbz x0, 32, 1f
	add x0, x0, 2
1:
	sub x0, x0, 1
	ret
