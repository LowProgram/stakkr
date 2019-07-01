# User input; the files that need to be merged
print('Enter the components you want to use: ')
while True:
    inputFiles = []
    userFileChoice = input()
    if userFileChoice == "":
        break
    else:
        inputFiles.append(userFileChoice)

# Ask user what name the recipe is gonna be
endFilename = input('Name your recipe: ')
with open(endFilename, 'w') as outputFile:
    # Should walk trough the inputFiles list opening and merging one file at the time
    for i in inputFiles:
        with open(inputFiles[i], 'r') as f:
            readData = f.read
            f.close()

            # First file determines format
            if i == inputFiles[0]:
                outputFile.write(readData)

            # Search data and merge this into the outputFile
            else:
                do = 'nothing'

                    
                    
                    





