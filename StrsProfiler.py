from os import sys
from pathlib import Path
import re
import csv




class StrsProfiler:

    def __init__(self):
        self.summary = {}
        
        self.directory, self.django_scope, self.path_prefix = self.initialize_params()
        self.format_directory()
        print("Directory: {}\nPath Prefix: {}".format(self.directory, self.path_prefix))

        self.paths = self.file_paths()

    def run(self):
        self.summarize_paths()
        
    # Command Methods
    def summarize_paths(self):
        print("Summarizing paths...")
        for path_ext in self.paths:
            for path in path_ext:
                path = str(path)
                with open(path) as file:
                    self.define_keys(file, path)
                with open(path) as file:
                    self.process_file(file, path)
        
        with open("strs-{}.csv".format(self.django_scope), 'a+') as csv_file:
            headers = ['key', 'defined at', 'used at', 'uses']
            
            writer = csv.writer(csv_file)
            writer.writerows([headers])            
            
            datarows = []

            for key in self.summary:
                datarows.append([key, self.summary[key]['defined_at'].replace(self.path_prefix, ''), "\n".join(self.summary[key]['used_at']).replace(self.path_prefix, ''), len(self.summary[key]['used_at'])])
            
            writer.writerows(datarows)
        
        csv_file.close()

    # Utility Methods
    def define_keys(self, file, path):
        start_line = re.compile("\$trs.*\{$") # Finds `$trs: {`
        end_line = re.compile("\},$") # Finds `},`
        key_match = re.compile("(\w+):")
        lines = file.read().split("\n")

        keys = []

        processing_lines = False
        for idx, line in enumerate(lines):
            if end_line.search(line):
                processing_lines = False

            if processing_lines:
                matches = key_match.search(line)
                if(matches):
                    key = matches.groups()[0]
                    keys.append((key, idx))
                else:
                    print("WARNING: In define_keys() - No match found in $trs.\n{}\n{}\n".format(path,line))

            if start_line.search(line):
                processing_lines = True
        for key_tuple in keys:
            key = key_tuple[0]
            line_number = key_tuple[1] + 1
            self.summary[key] = {
                'defined_at': "{} : {}".format(path, line_number),
                'used_at': []
            }

    def process_file(self, file, path):
        summaries = []
        str_pattern = re.compile("\$tr\(['\"](\w+)['\"]\)") # Finds for $tr('capturedGroup')
        lines = file.read().split("\n")
        for line_number, line in enumerate(lines):
            search_results = str_pattern.search(line)
            if search_results:
                for key in search_results.groups():
                    if key in self.summary.keys():
                        self.summary[key]['used_at'].append("{} : {}".format(path, line_number + 1))


    def file_paths(self):
        print("Filing paths...")
        try:
            js_files = sorted(Path(self.directory).glob('**/*.js'))
            vue_files = sorted(Path(self.directory).glob('**/*.vue'))
            return [vue_files, js_files]
        except(Exception):
            print("Error in file_paths()")
            return []

    def format_directory(self):
        self.directory = self.directory.replace('.', '/')
        self.directory += '/assets/src'
        self.directory = self.path_prefix + self.directory

    def initialize_params(self):
        directory = ''
        command = 'summary'  # Default to summary
        postfix = None

        try:
            directory = sys.argv[1]
            django_scope = directory.split('.')[-1]
        except:
            print("Please try again. Provide an argument for the directory that you'd like to process. You may enter the directory like `kolibri.plugins.coach` or `kolibri/plugins/coach`")

        try:
            path_prefix = sys.argv[2]
        except:
            pass

        return [directory, django_scope, path_prefix]
