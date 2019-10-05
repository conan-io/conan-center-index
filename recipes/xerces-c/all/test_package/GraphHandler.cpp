// GraphHandler.cpp
#include "GraphHandler.h"
#include <xercesc/sax2/Attributes.hpp>
#include <stdio.h>
#include "XercesString.h"
#include <float.h>
#include <wchar.h>

static const bool bDebug = false;

void GraphHandler::startDocument()
{
  if (bDebug) printf("starting...\n");
}

// given a value, minimum, maximum and overall discrete number of tiles;
// computes how many tiles or blocks will be displaced by the value.
static int tiles(double fValue, double fMin, double fMax, int nSpan)
{
  double fDel = fMax - fMin;
  fValue -= fMin;
  if (fDel <= FLT_MIN) fValue = 0.;
  else fValue /= (fMax - fMin);
  return (int)(fValue * nSpan);
}

// returns a null terminated string whose length 
// is the requested span (up to some limit).
static const char *bars(int nSpan)
{
  static const char strBars[] = 
    "########################################"
	"########################################";
  const int kLimit = sizeof strBars - 1;
  if (nSpan > kLimit) nSpan = kLimit;
  return &strBars[kLimit - nSpan];
}

void GraphHandler::endDocument()
{
  int nDex = 0;
  double fMin = 0.0, fMax = 0.0;
  if (bDebug) printf("...ends.\n");

  const unsigned kLimit = mList.size();
  if (bDebug)
  {
    printf("Department               Sales Inventory     Labor\n");
    printf("-------------------- --------- --------- ---------\n");
  }
  for (nDex = 0; nDex < kLimit; nDex++)
  {
    double fValue = mList[nDex].mSales;
    if (!nDex)
      fMin = fMax = fValue;
    else
    {
      if (fValue > fMax) fMax = fValue;
      else if (fValue < fMin) fMin = fValue;
    }
    if (bDebug)
    {
      char *strName = XMLString::transcode(mList[nDex].mName);
      printf("%-20.20s %9.2f %9.2f %9.2f\n", strName, mList[nDex].mSales, 
        mList[nDex].mInventory, mList[nDex].mLabor);
      XMLString::release(&strName);
    }
  }
  const int nSpan = 70;
  fMin *= 0.8;
  for (nDex = 0; nDex < kLimit; nDex++)
  {
    int nWidth = tiles(mList[nDex].mSales, fMin, fMax, nSpan);
    char *strName = XMLString::transcode(mList[nDex].mName);
    printf("%-20.20s (%7.0f) %s\n", strName, mList[nDex].mSales, bars(nWidth) );
    XMLString::release(&strName);
  }
}

void GraphHandler::startElement(
    const XMLCh* const uri, 
    const XMLCh* const localname, 
    const XMLCh* const qname, 
    const Attributes& attrs)
{
  char *strLocalname = XMLString::transcode(localname);
  if (bDebug) printf("element  [%s]\n", strLocalname);
  XMLString::release(&strLocalname);

  const XercesString kstrFigures("figures");
  const XercesString kstrType("type");
  const XercesString kstrValue("value");
  const XercesString kstrDepartment("department");
  const XercesString kstrSales("sales");
  const XercesString kstrLabel("label");
  const XercesString kstrLabor("labor");
  const XercesString kstrInventory("inventory");
  const XercesString kstrName("name");
  const XercesString kstrCorporate("corporate");

  if ( !XMLString::compareString(localname, kstrFigures) )
  {
    const XercesString wstrType( attrs.getValue(kstrType) );
    const XercesString wstrValue( attrs.getValue(kstrValue) );
    double fValue = 0.;

    // warning: this assumes <XMLCh> is compatible 
	// with <wchar_t> which is not portable.
    fValue = wcstod(reinterpret_cast<const wchar_t *>( wstrValue.begin() ), NULL );

    if (mList.size())
    {
      if ( !XMLString::compareString(wstrType, kstrSales) )
        mList[mList.size() - 1].mSales = fValue;
      else if ( !XMLString::compareString(wstrType, kstrInventory) )
        mList[mList.size() - 1].mInventory = fValue;
      else if ( !XMLString::compareString(wstrType, kstrLabor) )
        mList[mList.size() - 1].mLabor = fValue;
    }
  }
  else if ( !XMLString::compareString(localname, kstrDepartment) )
  {
    const XercesString wstrValue( attrs.getValue(kstrName) );
    mList.insert( mList.end(), department(wstrValue) );
    char *strValue =  XMLString::transcode(wstrValue);
    if (bDebug) puts(strValue);
    XMLString::release(&strValue);
  }
  else if ( !XMLString::compareString(localname, kstrCorporate) )
  {
    mName = attrs.getValue(kstrName);
    char *strValue =  XMLString::transcode(mName);
    if (bDebug) puts(strValue);
    XMLString::release(&strValue);
  }
}

void GraphHandler::endElement(
  const XMLCh* const uri, 
  const XMLCh* const localname,
  const XMLCh* const qname)
{
  char *strLocalname = XMLString::transcode(localname);
  if (bDebug) printf("...end element %s.\n", strLocalname);
  XMLString::release(&strLocalname);
}

void GraphHandler::characters(
  const XMLCh* const chars,
  const unsigned int length)
{
  if (!bDebug) return;
  char *strChars = XMLString::transcode(chars);
  printf("chars [ %-0.*s ] \n", length, strChars);
  XMLString::release(&strChars);
}
