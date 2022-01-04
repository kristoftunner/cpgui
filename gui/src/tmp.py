parsedFunctions = ["main"]
parsedModules = ["gsm"]
modules = ["gsm", "modbus", "time"]
functions = ["gsm_init", "gsm_proces", "modbus_init", "modbus_process"]

for f,m in zip(functions, modules):
    print("function:" ,f)
    print("module:" ,m)