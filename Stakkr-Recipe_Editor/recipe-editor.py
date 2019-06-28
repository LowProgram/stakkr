


print("Enter the components you want to use: ")
while True:
    inputFiles = []
    userFileChoice = input()
    if userFileChoice == "go":

        break
    else:
        inputFiles.append(userFileChoice)

endFilename = input("Name your recipe: ")
with open(endFilename, "w+") as outputFile:
    for filename in inputFiles:
        with open(filename, 'a+') as inputFiles:



