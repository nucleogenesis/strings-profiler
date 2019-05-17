from os import sys
from pathlib import Path
import re
import csv

# TODO: Approach this differently so that a user can run the program
# without having to edit the ROOT_PATH in the code.
ROOT_PATH = "/home/jacob/Code/LearningEquality/kolibri/kolibri/" 

PATHS = {
    'coach':'plugins/coach/assets/src',
    'learn':'plugins/learn/assets/src',
    'facility_management':'plugins/facility_management/assets/src',
    'device_management':'plugins/device_management/assets/src',
    'core':'core/assets/src',
}

REGEXES = {
    'str': re.compile("\$tr\(['\"](\w+)['\"]"),
}

CSV_HEADERS = ['KEY', '# USES', '# UNIQUE FILE SOURCES', 'ALL FILE SOURCES', 'DEFINED IN COMMON FILE']

COMMON_COACH_PATH = "/home/jacob/Code/LearningEquality/kolibri/kolibri/plugins/coach/assets/src/views/common/commonCoachStrings.js"

class StringProfiler:

    def run(self):
        # 1. Get all relevant files
        for path_key in PATHS.keys():
            print("Working on {}.".format(path_key))
            base_path = ROOT_PATH + PATHS[path_key]            

            js_file_paths = sorted(Path(base_path).glob('**/*.js'))
            vue_file_paths = sorted(Path(base_path).glob('**/*.vue'))
            ALL_FILE_PATHS = js_file_paths + vue_file_paths

            results = dict()

            for file_path in ALL_FILE_PATHS:
                file_path = str(file_path)

                # 2. Parse each file, get matching $tr('*') captures.
                with open(file_path) as active_file:
                    file_content = active_file.read()
                    search_results = REGEXES['str'].findall(file_content)

                    # 3. Take results and add them to results { key: [path1, path2...] }
                    if search_results:
                        for match in search_results:
                            if match in results.keys():
                                results[match].append(file_path)
                            else:
                                results[match] = [file_path]

            # 4. Write results to CSV
            csv_filename = "strings-profile-{}.csv".format(path_key)
            with open(csv_filename, "a") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerows([CSV_HEADERS])

                csv_data = []
                for key in results.keys():
                    paths = results[key]
                    unique_paths = list(set(results[key]))
                    has_common_definition = ''
                    
                    if path_key == "coach":
                        with open(COMMON_COACH_PATH) as commons:
                            common_coach_strings = commons.read()
                            has_common_definition = key in common_coach_strings

                    csv_data.append([key, len(paths), len(unique_paths), self.strip_path(unique_paths.pop(0), path_key), str(has_common_definition)])
                    for path in unique_paths:
                        csv_data.append(['','','',self.strip_path(path, path_key), ''])
                
                writer.writerows(csv_data)

    def strip_path(self, path, path_key):
        return path.replace(ROOT_PATH, '').replace(PATHS[path_key], '')
                    
        