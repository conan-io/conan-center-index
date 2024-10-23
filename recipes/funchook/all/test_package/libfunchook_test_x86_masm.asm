.686P
.XMM
include listing.inc
.model	flat

INCLUDELIB MSVCRT
INCLUDELIB OLDNAMES

PUBLIC	_call_get_val_in_dll
PUBLIC	_jump_get_val_in_dll
EXTRN	_get_val_in_dll:PROC

_TEXT	SEGMENT

_call_get_val_in_dll PROC EXPORT
	call	_get_val_in_dll
	ret	0
_call_get_val_in_dll ENDP

_jump_get_val_in_dll PROC EXPORT
	jmp	_get_val_in_dll
_jump_get_val_in_dll ENDP

_TEXT	ENDS

END
