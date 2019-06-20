# Python Program - Merge Two Files

""""import shutil;
print("Enter 'x' for exit.");
file1 = input("Enter first file name to merge: ");
if file1 == 'x':
    exit();
else:
    file2 = input("Enter second file name to merge: ");
    endFilename = input("Create a new file to merge content of two file inside this file: ");
    print();
    print("Merging the content of two file in",endFilename);
    with open(endFilename, "wb") as wfd:
        for f in [file1, file2]:
            with open(f, "rb") as fd:
                shutil.copyfileobj(fd, wfd, 1024*1024*10);
    print("\nContent merged successfully.!");
    print("Want to see ? (y/n): ");
    check = input();
    if check == 'n':
        exit();
    else:
        print();
        c = open(endFilename, "r");
        print(c.read());
        c.close();"""""

files = input("Enter the components you want to use (servicename.yml servicename2.yml): ")
filenameList = files.split()
endFilename = input("Name your recipe (name.yml): ")
with open(endFilename, 'w') as outputFile:
    for filename in filenameList:
        with open(filename, 'r') as inputFile:
            for line in inputFile:
                outputFile.write(line)

