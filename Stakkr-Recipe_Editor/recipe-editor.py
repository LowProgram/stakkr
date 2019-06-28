
go = False
inputFiles = []
print("Enter the components you want to use: ")
while  go == False:
    userFileChoice = input()
    if userFileChoice == "go":
        go == True
        break
    else:
        inputFiles.append(userFileChoice)

endFilename = input("Name your recipe: ")
for file in inputFiles:


#with open(endFilename, 'w') as outputFile:
   #for filename in inputFiles:
        #with open(filename, 'r') as inputFile:
            #for service in seric


