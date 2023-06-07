import argparse
import zipfile
import os
from FileScorer import FileScorer
import pandas as pd

def process_input_file(input_file):
    print(f"Processing input file: {input_file}")

def unzip(input_file, destination):
    with zipfile.ZipFile(input_file, 'r') as zip:
        zip.extractall(destination)
    for root, directories, files in os.walk(destination):
        for dire in directories:
            for dire_root, dire_directories, dire_files in os.walk(destination+"\\" + dire):
                for file in dire_files:
                    file_path = destination+"\\" + dire + "\\"+file
                    if zipfile.is_zipfile(file_path):
                        with zipfile.ZipFile(file_path, 'r') as zip:
                            zip.extractall(destination+"\\" + dire)

def create_evaluation_tuples(folder_path, file_name):
    evaluation_tuples = []
    failure_tuples = []
    for root, directories, files in os.walk(folder_path):
        for dire in directories:
            if len(dire.split("_")) < 5:
                continue
            student_name, student_id,_, _, _ = dire.split("_")
            is_found = False
            for dire_root, dire_directories, dire_files in os.walk(folder_path+"\\" + dire):
                for dir_file in dire_files:
                    if dir_file == file_name:
                        evaluation_tuples.append((student_name, student_id, os.path.join(dire_root, file_name)))
                        is_found = True
                        break
            if not is_found:
                failure_tuples.append((student_name, student_id))

    print("evaluation {}".format(len(evaluation_tuples)))
    print("failure {}".format(len(failure_tuples)))
    return evaluation_tuples, failure_tuples

def score(folder_path, file_names, diff_cmd="{} {}"):
    writer = pd.ExcelWriter("result.xlsx")
    failure_df = pd.DataFrame(columns=["file name", "name", "id"])
    for file_name in file_names:
        evaluation_tuples, failure_tuples = create_evaluation_tuples(folder_path, file_name)
        for failure in failure_tuples:
            failure_df.loc[len(failure_df.index)] = [file_name, failure[0], failure[1]]

        score_df = pd.DataFrame(columns=["name 1",\
                        "id 1",\
                        "file 1",\
                        "name 2",\
                        "id 2",\
                        "file 2",\
                        "score1",\
                        "score2",\
                        "diff_cmd"])

        fs = FileScorer()

        tuple_count = len(evaluation_tuples)

        for i in range(tuple_count):
            for j in range(i + 1, tuple_count,1):
                score1, score2 = fs.score_for_files(evaluation_tuples[j][-1], evaluation_tuples[i][-1])
                score_df.loc[len(score_df.index)] = [\
                                                    evaluation_tuples[i][0],\
                                                    evaluation_tuples[i][1],\
                                                    evaluation_tuples[i][2],\
                                                    evaluation_tuples[j][0],\
                                                    evaluation_tuples[j][1],\
                                                    evaluation_tuples[j][2],\
                                                    score1,\
                                                    score2,\
                                                    diff_cmd.format(evaluation_tuples[i][2], evaluation_tuples[j][2])]
                
        #save evaluation to evaluation sheet
        score_df.to_excel(writer, sheet_name=file_name, index=False)
        print("{} scoring complete".format(file_name))
    #save failures to failure sheet
    failure_df.to_excel(writer, sheet_name="failed", index=False)
    writer.save()
    print("Results.xlsx generated")


def main():
    parser = argparse.ArgumentParser(description="This application has a few functions\n \
                                     1.Unzips the zipfile downloaded when downloading all submissions from moodle.\n\
                                     Submissions should be downloaded as folders. \n\
                                     It will attempt to unzip zip files within the individual folder if any.\n\
                                     2.Calculates similarity scores between submissions.\n\
                                     Each submission is identified by folder name.\n\
                                     If there are multiple files submitted, \n\
                                     scores will be saved on separate sheets of the result excel file.\n\
                                     \n\
                                     For convenience, this tool can generate a command line string\n\
                                     to launch a diff tool between the two files being compared for all comparisons.\n\
                                     Just enter your command following the example \"difftool {} {}\" as a single string\n\
                                     The \"{}\" characters will be replaced with the filepaths for comparison.")

    parser.add_argument("-i", "--input", dest="input_file", help="Input file path")
    parser.add_argument("-uz", "--unzip", nargs="+", help="Enter source file to unzip and folder to unzip to")
    parser.add_argument("-s", "--score", nargs="+", help="Enter folder path of all folders of code, then each file name for comparison.")
    parser.add_argument("-dt", "--difftool", dest="tool_line", help="Enter a single string for diff tool command line launching.")

    args = parser.parse_args()

    if args.input_file:
        process_input_file(args.input_file)
    else:
        print("No input file specified.")

    if args.unzip:
        unzip(args.unzip[0], args.unzip[1])
        return
    else:
        print("check arguments")

    tool_line = "{} {}"
    if args.tool_line:
        tool_line = args.tool_line

    if args.score:
        path = args.score[0]
        files = args.score[1:]
        score(path, files, tool_line)



if __name__ == "__main__":
    main()
