#include "quickfix/config.h"

#include "quickfix/FileStore.h"
#include "quickfix/Application.h"
#include "quickfix/SocketAcceptor.h"
#include "quickfix/Log.h"
#include "quickfix/SessionSettings.h"
#include "quickfix/DOMDocument.h"
#include "quickfix/DataDictionaryProvider.h"


class Attributes : public FIX::DOMAttributes
{ };

class Node : public FIX::DOMNode
{
public:
  virtual ~Node(){ };
private:
  virtual SmartPtr<DOMNode> getFirstChildNode()
  { Node * ptr; return SmartPtr<DOMNode>(ptr); }
  virtual SmartPtr<DOMNode> getNextSiblingNode()
  { Node * ptr; return SmartPtr<DOMNode>(ptr); }
  virtual SmartPtr<FIX::DOMAttributes> getAttributes()
  { Attributes * ptr; return SmartPtr<FIX::DOMAttributes>(ptr); }
  virtual std::string getName()
  { return ""; }
  virtual std::string getText()
  { return ""; }
};

class Application
    : public FIX::Application
{
public:
  // Application overloads
  void onCreate( const FIX::SessionID& ) {}
  void onLogon( const FIX::SessionID& sessionID ) {}
  void onLogout( const FIX::SessionID& sessionID ) {}
  void toAdmin( FIX::Message&, const FIX::SessionID& ) {}
  void toApp( FIX::Message&, const FIX::SessionID& )
  EXCEPT( FIX::DoNotSend ) {};
  void fromAdmin( const FIX::Message&, const FIX::SessionID& )
  EXCEPT( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::RejectLogon )
  {}
  void fromApp( const FIX::Message& message, const FIX::SessionID& sessionID )
  EXCEPT( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::UnsupportedMessageType )
  {}
};

int main( int argc, char** argv )
{
  try
  {
    Node node;
    FIX::DataDictionaryProvider provider;
    provider.addTransportDataDictionary( FIX::BeginString("FIX.4.2"), ptr::shared_ptr<FIX::DataDictionary>(new FIX::DataDictionary()) );
    Application application;
    FIX::SessionSettings settings( "" );
    FIX::FileStoreFactory storeFactory( settings );
    FIX::ScreenLogFactory logFactory( settings );

    FIX::SocketAcceptor acceptor( application, storeFactory, settings, logFactory );
  }
  catch( std::exception & )
  { }

  return 0;
}
