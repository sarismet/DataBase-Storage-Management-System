import struct
import re
import os


class Type:
    def __init__(self, TypeName, NumberOfFiles, NumberOfFields, Fields_Names, Files):

        self.TypeName = TypeName
        self.NumberOfFiles = NumberOfFiles
        self.NumberOfFields = NumberOfFields
        self.Fields_Names = Fields_Names
        self.Files = Files

    def addFile(self, newFile):
        self.Files.append(newFile)
        self.NumberOfFiles += 1


class File:
    def __init__(
        self, isFull, NumberOfRecords, NumberOfPages, NextFile, PreviousFile, Pages
    ):
        self.isFull = isFull
        self.NumberOfRecords = NumberOfRecords
        self.Pages = Pages
        self.NumberOfPages = NumberOfPages
        self.NextFile = NextFile
        self.PreviousFile = PreviousFile

    def addPage(self, newPage):
        self.Pages.append(newPage)
        self.NumberOfPages += 1


class Page:
    def __init__(self, NumberOfRecords, Records):
        self.NumberOfRecords = NumberOfRecords
        self.Records = Records

    def addPage(self, newRecord):
        self.Records.append(newRecord)
        self.NumberOfRecords += 1


class Record:
    def __init__(self, Fields):
        self.Fields = Fields


class indexFile:
    def __init__(self, Number_OF_Records, Max_Number_OF_Records_Per_File, Records):
        self.Number_OF_Records = Number_OF_Records
        self.Max_Number_OF_Records_Per_File = Max_Number_OF_Records_Per_File
        self.Records = Records

    def add_new_indexFile_Record(self, new_indexFile_Record):
        self.Records.append(new_indexFile_Record)
        self.Number_OF_Records += 1


class Record_indexFile:
    def __init__(self, FileID, PageID, RecordID, PrimaryKey):
        self.FileID = FileID
        self.PageID = PageID
        self.RecordID = RecordID
        self.PrimaryKey = PrimaryKey


class SystemCatalog:
    def __init__(self):
        self.NumberOfTypes = 0
        self.Types = {}
        self.indexFiles = {}
        self.SystemCatalogFile = None

    def __enter__(self):
        if os.path.exists("SystemCatalog"):
            print("SystemCatalogFile is opened successsively")
            self.readSystemCatalogFile()
        else:

            print("There is no such a file...")
            self.createCatalogFile()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Closing System Catalog...")
        self.writeback()

    def createCatalogFile(self):
        print("Creating a new SystemCatalog File...")
        open("SystemCatalog", "a").close()

    def readSystemCatalogFile(self):
        print("SystemCatalogFile is being read...")
        try:
            self.SystemCatalogFile = open("SystemCatalog", "rb")
            self.NumberOfTypes = struct.unpack("i", self.SystemCatalogFile.read(4))[0]
            print(self.NumberOfTypes, " is read from SystemCatalog ")

            for i in range(self.NumberOfTypes):

                Temp_Type_Name = self.SystemCatalogFile.read(16).decode("utf-8")
                Type_Name = re.sub(" ", "", Temp_Type_Name)
                print(Type_Name)

                File_No = struct.unpack("b", self.SystemCatalogFile.read(1))[0]
                Fields_No = struct.unpack("b", self.SystemCatalogFile.read(1))[0]
                Fields = []

                for b in range(Fields_No):

                    tempx = self.SystemCatalogFile.read(16).decode("utf-8")
                    tempx = re.sub(" ", "", tempx)
                    Fields.append(tempx)
                Files = []
                for c in range(int(File_No)):
                    print(
                        "BUNU GORMEMEMEN LAZIMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
                    )
                    File = open(str(Type_Name) + str(c), "rb")
                    isFullinFileHeader = struct.unpack("b", File.read(1))[0]
                    NumberOfRecordsinFileHeader = struct.unpack("i", File.read(4))[0]
                    NumberOfPageinFileHeader = struct.unpack("b", File.read(1))[0]
                    NextFileinFileHeader = struct.unpack("b", File.read(1))[0]
                    PreviousFileinFileHeader = struct.unpack("b", File.read(1))[0]
                    Pages = []
                    for d in range(int(NumberOfPageinFileHeader)):

                        NumberOfRecordsinPageHeader = struct.unpack("b", File.read(1))[
                            0
                        ]
                        Records = []
                        for e in range(int(NumberOfRecordsinPageHeader)):
                            Fields_Of_NewRecord = []
                            for f in range(Fields_No):
                                Fields_Of_NewRecord.append(
                                    int(struct.unpack("i", File.read(4))[0])
                                )
                            Records.append(Record(Fields_Of_NewRecord))
                        Pages.append(Page(NumberOfRecordsinPageHeader, Records))

                    Files.append(
                        File(
                            isFullinFileHeader,
                            NumberOfRecordsinFileHeader,
                            NumberOfPageinFileHeader,
                            NextFileinFileHeader,
                            PreviousFileinFileHeader,
                            Pages,
                        )
                    )
                    File.close()

                T = Type(Type_Name, File_No, Fields_No, Fields, Files)
                self.Types.update({str(Type_Name): T})
            self.SystemCatalogFile.close()
            print("Reading All Type Files is Compleated")

            print("Phase 2 ....Reading All indexFiles.... ")
            self.readindexFiles()
        except Exception as e:
            print(e)
            self.SystemCatalogFile.close()

    def readindexFiles(self):
        print("All indexFiles are being read...")
        for TypeName in self.Types:
            try:
                filepath = "./indexFiles/" + str(TypeName) + "index"
                print(filepath)
                TindexFile = open(filepath, "rb")
                NumberOfRecords = struct.unpack("i", TindexFile.read(4))[0]
                NumberOfRecordsPerFile = struct.unpack("i", TindexFile.read(4))[0]
                print("In related indexFile we found")
                print("The Number Of Records ", NumberOfRecords)
                print("The Number Of Records Per File", NumberOfRecordsPerFile)
                Temp_Records_Array = []
                for i in range(NumberOfRecords):
                    FileID = struct.unpack("b", TindexFile.read(1))[0]
                    PageID = struct.unpack("b", TindexFile.read(1))[0]
                    RecordID = struct.unpack("b", TindexFile.read(1))[0]
                    PrimaryKey = struct.unpack("i", TindexFile.read(4))[0]
                    Temp_Records_Array.append(
                        Record_indexFile(
                            int(FileID), int(PageID), int(RecordID), int(PrimaryKey)
                        )
                    )

                TI = indexFile(
                    NumberOfRecords, NumberOfRecordsPerFile, Temp_Records_Array
                )

                self.indexFiles.update({TypeName: TI})
                TindexFile.close()
            except Exception as e:
                print(e)

    def writeback(self):

        print("writing back on System Catalog File...")
        try:
            self.SystemCatalogFile = open("SystemCatalog", "wb")
            self.SystemCatalogFile.write(struct.pack("i", self.NumberOfTypes))
            for TypeName in self.Types:
                TypeNameToWrite = self.complate(TypeName)
                self.SystemCatalogFile.write(TypeNameToWrite.encode("utf-8"))
                self.SystemCatalogFile.write(
                    bytes([self.Types[TypeName].NumberOfFiles])
                )
                self.SystemCatalogFile.write(
                    bytes([self.Types[TypeName].NumberOfFields])
                )

                for i in range(self.Types[TypeName].NumberOfFields):
                    FN = self.complate(self.Types[TypeName].Fields_Names[i])
                    self.SystemCatalogFile.write(FN.encode("utf-8"))
                    index = 0
                for File in self.Types[TypeName].Files:
                    PATH = "Files/" + str(TypeName) + "/" + str(TypeName) + str(index)

                    if not os.path.exists(PATH):
                        print("Creating a new Type-File")
                        open(PATH, "a").close()
                    File_To_Write = open(PATH, "wb")
                    File_To_Write.write(bytes([File.isFull]))
                    File_To_Write.write(struct.pack("i", File.NumberOfRecords))
                    File_To_Write.write(bytes([File.NumberOfPages]))
                    File_To_Write.write(bytes([File.NextFile]))
                    File_To_Write.write(bytes([File.PreviousFile]))
                    try:
                        for Page in File.Pages:

                            File_To_Write.write(bytes([Page.NumberOfRecords]))
                            for Record in Page.Records:
                                for Field in Record.Fields:
                                    File_To_Write.write(struct.pack("i", Field))

                    except Exception as e:
                        print(e)
                    File_To_Write.close()
                    index += 1
            self.SystemCatalogFile.close()
            print("Writing of All Type Files is compleated...")
            self.writebackindexFiles()

        except Exception as e:
            print("There is an exception occured in writing back page such that \n ", e)

    def writebackindexFiles(self):
        print("All indexFiles are being written back...")
        for x in self.indexFiles:
            print("KEYS,", self.indexFiles[x])
        for key in self.indexFiles:
            filename = "./indexFiles/" + str(key) + "index"
            TindexFile = open(filename, "wb")
            TindexFile.write(struct.pack("i", self.indexFiles[key].Number_OF_Records))
            TindexFile.write(
                struct.pack("i", self.indexFiles[key].Max_Number_OF_Records_Per_File)
            )
            if len(self.indexFiles[key].Records) > 0:
                for record in self.indexFiles[key].Records:

                    TindexFile.write(bytes([int(record.FileID)]))
                    TindexFile.write(bytes([int(record.PageID)]))
                    TindexFile.write(bytes([int(record.RecordID)]))
                    TindexFile.write(struct.pack("i", record.PrimaryKey))

    def complate(self, TypeName):
        for i in range(len(TypeName), 16):
            TypeName = " " + TypeName
        return TypeName


class DLL:
    def __init__(self, SystemCatalog):
        self.SystemCatalog = SystemCatalog

    def Create_Type(self, TypeName, NumberOfFields, Fields_Names):

        if not Check_If_Type_Exits(TypeName, self.SystemCatalog):
            newType = Type(TypeName, 0, NumberOfFields, Fields_Names, [])
            self.SystemCatalog.Types.update({TypeName: newType})
            self.SystemCatalog.NumberOfTypes += 1
            PATH = "./indexFiles/" + str(TypeName) + "index"
            os.mkdir("Files/" + str(TypeName))
            open(PATH, "a").close()
            maxNoofRecordsPerFile = int(2048 / (4 * NumberOfFields)) * 256
            newIndexFile = indexFile(0, maxNoofRecordsPerFile, [])
            self.SystemCatalog.indexFiles.update({TypeName: newIndexFile})

    def Delete_Type(self):
        print()

    def List_All_Types(self):
        for Type in self.SystemCatalog.Types:
            print(Type.TypeName)


class DML:
    def __init__(self, SystemCatalog):
        self.SystemCatalog = SystemCatalog

    def Create_Record(self, TypeName, Fields_Values):
        Type = self.SystemCatalog.Types[TypeName]

        indexFile = self.SystemCatalog.indexFiles[TypeName]

        MaxNumberOfRecordsPerFile = indexFile.Max_Number_OF_Records_Per_File

        MaxNumberOfRecordsPerPage = int(MaxNumberOfRecordsPerFile / 256)

        main_indexFile = self.SystemCatalog.indexFiles[TypeName]
        newRecord = Record(Fields_Values)
        if len(main_indexFile.Records) == 0:
            newRecord = Record_indexFile(0, 0, 0, Fields_Values[0])
            main_indexFile.add_new_indexFile_Record(newRecord)
            newPage = Page(1, [])
            newPage.Records.append(Record(Fields_Values))
            newFile = File(1, 0, 0, [])
            newFile.Pages.append(newPage)
            self.SystemCatalog.Types[TypeName].Files.append(newFile)
            return

        Returned_Index = insert_Record_To_indexFile(
            Fields_Values[0], main_indexFile, Type, MaxNumberOfRecordsPerPage
        )

        index = Returned_Index
        while index < len(main_indexFile):

            main_indexFile.Records[index].RecordID += 1
            if main_indexFile.Records[index].RecordID == MaxNumberOfRecordsPerPage - 1:
                main_indexFile.Records[index].RecordID = 0
                main_indexFile.Records[index].PageID += 1

                if main_indexFile.Records[index].PageID == 256:

                    main_indexFile.Records[index].PageID = 0
                    main_indexFile.Records[index].FileID += 1
                    if main_indexFile.Records[index].FileID == len(Type.Files):
                        newFile = File(
                            1, 0, main_indexFile.Records[index].FileID - 1, []
                        )
                        newPage = Page(1, [])
                        newRecord = (
                            Type.Files[main_indexFile.Records[index].FileID - 1]
                            .Pages[255]
                            .Records.pop()
                        )
                        newPage.Records.append(newRecord)
                        newFile.Pages.append(newPage)
                        Type.Files.append(newFile)
                        return

                    newRecord = (
                        Type.Files[main_indexFile.Records[index].FileID - 1]
                        .Pages[255]
                        .Records.pop()
                    )
                    Type.Files[main_indexFile.Records[index].FileID].Pages[
                        0
                    ].Records.insert(0, newRecord)
                    continue
                newRecord = (
                    Type.Files[main_indexFile.Records[index].FileID]
                    .Pages[main_indexFile.Records[index].PageID - 1]
                    .Records.pop()
                )
                Type.Files[main_indexFile.Records[index].FileID].Pages[
                    main_indexFile.Records[index].PageID
                ].Records.insert(0, newRecord)
                continue

            index += 1


def Check_If_Type_Exits(TypeName, SystemCatalog):
    # print("Checking If Type Exits...")
    for Type in SystemCatalog.Types:
        if Type == TypeName:
            print("The Type is found!!! ")
            return True


def insert_Record_To_indexFile(Fields, TheindexFile, Type, MaxNumberOfRecordsPerPage):
    TheindexFile.Number_OF_Records += 1

    index = 0
    PrimaryKey = Fields[0]
    RID, FID, PID = 1, 1, 1
    print(TheindexFile.Records)
    for RecordN in TheindexFile.Records:

        if RecordN.PrimaryKey > PrimaryKey:
            break
        index += 1

    if index == 0:
        FID = TheindexFile.Records[0].FileID
        PID = TheindexFile.Records[0].PageID
        RID = TheindexFile.Records[0].RecordID

        newRecord = Record_indexFile(FID, PID, RID, PrimaryKey)
        TheindexFile.Records.insert(index, newRecord)
        Type.Files[0].Pages[0].Records.insert(0, Record(Fields))

        if Type.Files[0].Pages[0].NumberOfRecords < MaxNumberOfRecordsPerPage:
            Type.Files[0].Pages[0].NumberOfRecords += 1

        return 1
    FID = TheindexFile.Records[index - 1].FileID
    PID = TheindexFile.Records[index - 1].PageID
    RID = TheindexFile.Records[index - 1].RecordID
    newRecord = Record_indexFile(FID, PID, RID, PrimaryKey)
    TheindexFile.Records.insert(index, newRecord)
    Type.Files[FID].Pages[PID].Records.insert(RID + 1, Record(Fields))
    return index


if not os.path.exists("indexFiles"):
    os.mkdir("indexFiles")

if not os.path.exists("Files"):
    os.mkdir("Files")
with SystemCatalog() as f:
    d1 = DLL(f)
    d2 = DML(f)
    d1.Create_Type("5", 3, ["age", "len", "spe"])  # 16
    d1.Create_Type("6", 4, ["age", "len", "spe", "smell"])  # 18
    d1.Create_Type("7", 3, ["age", "len", "spe"])  # 16
    d1.Create_Type("8", 4, ["agex", "lenx", "spex", "prox"])  # 16
    # d2.Create_Record("5", [1, 172, 45, 1, 1, 1, 2, 3, 4, 5])
