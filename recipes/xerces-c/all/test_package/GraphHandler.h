// GraphHandler.h
#include <xercesc/sax2/DefaultHandler.hpp>
#include <vector>
#include <algorithm>

#include "XercesString.h"

struct department
{
  XercesString mName;
  double mSales;
  double mInventory;
  double mLabor;

  department() : mSales(0.0), mInventory(0.0), mLabor(0.0) { };

  department(const department &copy) : mName(copy.mName)
  {
    mSales = copy.mSales;
    mLabor = copy.mLabor;
    mInventory = copy.mInventory;
  };
 
  department(const XMLCh *wstr) : mName(wstr), mSales(0.0), mInventory(0.0), mLabor(0.0) { };

  virtual ~department() { };
};

class GraphHandler : public DefaultHandler
{
    XercesString mName;
  std::vector<department> mList;

public:
  virtual void startDocument();

  virtual void endDocument();
    
  virtual void startElement(
    const XMLCh* const uri, 
    const XMLCh* const localname, 
    const XMLCh* const qname, 
    const Attributes& attrs);
    
  virtual void endElement(
    const XMLCh* const uri, 
    const XMLCh* const localname,
    const XMLCh* const qname);

  virtual void characters(
    const XMLCh* const chars,
    const unsigned int length);
};
