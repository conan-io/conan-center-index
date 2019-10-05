#ifndef _XERCESSTRING_H
#define _XERCESSTRING_H

#include <xercesc/util/XMLString.hpp>

#ifdef XERCES_CPP_NAMESPACE_USE
XERCES_CPP_NAMESPACE_USE
#endif

class XercesString
{
	XMLCh *_wstr;
public:
	XercesString() : _wstr(0L) { };
	XercesString(const char *str);
	XercesString(XMLCh *wstr);
	XercesString(const XMLCh *wstr);
	XercesString(const XercesString &copy);
    XercesString & operator=(const XercesString &);
    
	~XercesString();
	bool append(const XMLCh *tail);
	bool erase(const XMLCh *head, const XMLCh *tail);
	const XMLCh* begin() const;
	const XMLCh* end() const;
	int size() const;
	XMLCh & operator [] (const int i);
	const XMLCh operator [] (const int i) const;
	operator const XMLCh * () const { return _wstr; };
};

#endif
