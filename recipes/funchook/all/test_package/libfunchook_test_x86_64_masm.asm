EXTRN	get_val_in_dll:PROC

_TEXT	SEGMENT

call_get_val_in_dll PROC EXPORT
	sub	rsp, 40
	call	get_val_in_dll
	add	rsp, 40
	ret	0
call_get_val_in_dll ENDP

jump_get_val_in_dll PROC EXPORT
	jmp	get_val_in_dll
jump_get_val_in_dll ENDP

_TEXT	ENDS

END
