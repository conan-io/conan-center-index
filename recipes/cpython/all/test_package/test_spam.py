import spam

spam.system("dir")

if "This is an example spam doc." not in spam.__doc__:
    raise Exception
