import hello_ext

txt = hello_ext.greet()
print(txt)

if txt != "hello, world!!!!!":
    raise Exception("did not expect this!")

