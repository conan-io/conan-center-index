#include <tixi.h>

#include <iostream>

int main()
{
    TixiDocumentHandle handle = -1;
    char* str = NULL;
    
    tixiCreateDocument("root", &handle);
    
    tixiAddTextElement(handle, "/root", "message", "This is a tixi test.");
    
    tixiExportDocumentAsString(handle, &str);
    
    std::cout << str << std::endl;
    
    tixiCloseDocument(handle);
    return 0;
}
