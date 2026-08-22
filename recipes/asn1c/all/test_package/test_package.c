#include <stdio.h>	/* for stdout */
#include <stdlib.h>	/* for malloc() */
#include <assert.h>	/* for run-time control */
#include "MyTypes.h"	/* Include MyTypes definition */

int main() {
	/* Define an OBJECT IDENTIFIER value */
	int oid[] = { 1, 3, 6, 1, 4, 1, 9363, 1, 5, 0 }; /* or whatever */

	/* Declare a pointer to a new instance of MyTypes type */
	MyTypes_t *myType;
	/* Declare a pointer to a MyInt type */
	MyInt_t *myInt;

	/* Temporary return value */
	int ret;

	/* Allocate an instance of MyTypes */
	myType = calloc(1, sizeof *myType);
	assert(myType);	/* Assume infinite memory */

	/*
	 * Fill in myObjectId
	 */
	ret = OBJECT_IDENTIFIER_set_arcs(&myType->myObjectId,
			oid, sizeof(oid[0]), sizeof(oid) / sizeof(oid[0]));
	assert(ret == 0);

	/*
	 * Fill in mySeqOf with a couple of integers.
	 */

	/* Prepare a certain INTEGER */
	myInt = calloc(1, sizeof *myInt);
	assert(myInt);
	*myInt = 123;	/* Set integer value */

	/* Fill in mySeqOf with the prepared INTEGER */
	ret = ASN_SEQUENCE_ADD(&myType->mySeqOf, myInt);
	assert(ret == 0);

	/* Prepare another integer */
	myInt = calloc(1, sizeof *myInt);
	assert(myInt);
	*myInt = 111222333;	/* Set integer value */

	/* Append another INTEGER into mySeqOf */
	ret = ASN_SEQUENCE_ADD(&myType->mySeqOf, myInt);
	assert(ret == 0);

	/*
	 * Fill in myBitString
	 */

	/* Allocate some space for bitmask */
	myType->myBitString.buf = calloc(1, 1);
	assert(myType->myBitString.buf);
	myType->myBitString.size = 1;	/* 1 byte */

	/* Set the value of muxToken */
	myType->myBitString.buf[0] |= 1 << (7 - myBitString_muxToken);

	/* Also set the value of modemToken */
	myType->myBitString.buf[0] |= 1 << (7 - myBitString_modemToken);

	/* Trim unused bits (optional) */
	myType->myBitString.bits_unused = 6;

	/*
	 * Print the resulting structure as XER (XML)
	 */
	return xer_fprint(stdout, &asn_DEF_MyTypes, myType);
}
