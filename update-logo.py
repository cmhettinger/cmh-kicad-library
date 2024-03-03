
#
# modify bitmap2component output to adjust layers, cleanup naming, and add metadata 
#
# run on a python enabled host:
# python update-logo.py filename.kicad_mod "my description" "tag1 tag2 tagn"
#
# or launch with script and footprint in the current directory via docker:
# docker run --rm -v "%cd%:/app" -w /app python:latest python update-logo.py filename.kicad_mod "my description" "tag1 tag2 tagn"
#

import sys

# define modified kicad file extension constant
NEW_EXTENSION = ".kicad_mod_modified"

def detect_line_ending(filename):
    with open(filename, 'rb') as f:
        # read the last two bytes of the file
        f.seek(-2, 2)
        last_bytes = f.read()
        
        # detect line ending type
        if last_bytes.endswith(b'\r\n'):
            return b'\r\n'  # windows style
        elif last_bytes.endswith(b'\n'):
            return b'\n'  # unix style
        elif last_bytes.endswith(b'\r'):
            return b'\r'  # mac style
        else:
            # default to unix style if unable to detect
            return b'\n'
            
def modify_footprint(filename, description, tags):
    try:
    
        # detect the line ending type
        line_ending = detect_line_ending(filename)
        
        # open the input file
        with open(filename, 'rb') as f:
            # read the content
            content = f.readlines()
            
            modified_content = []
            for line in content:
            
                # decode the line to string
                line = line.decode()
                
                # replace "LOGO" with the filename without extension
                line = line.replace("LOGO", filename.split('.')[0])
                # replace "G***" with "REF***"
                line = line.replace("G***", "REF***")
                
                # check for "(layer "F.SilkS")" and "fp_text"
                if "(layer \"F.SilkS\")" in line and "fp_text" in line:
                    # check if it's not followed by " hide"
                    if " hide" not in line:
                        # add " hide" immediately after "(layer "F.SilkS")" and before the current end of line
                        line = line.replace("(layer \"F.SilkS\")", "(layer \"F.SilkS\") hide", 1)
                    else:
                        # skip adding " hide" if it is already present
                        pass
                        
                # check for "fp_text value" and "F.SilkS"
                if "fp_text value" in line and "F.SilkS" in line:
                    # replace "F.SilkS" with "F.Fab"
                    line = line.replace("F.SilkS", "F.Fab")

                # check for "(layer "F.Cu")"
                if "(layer \"F.Cu\")" in line:
                    # insert new lines after for description and tags
                    modified_content.append(line)
                    modified_content.append("  (descr \"" + description + "\")" + line_ending.decode())
                    modified_content.append("  (tags \"" + tags + "\")" + line_ending.decode())
                else:
                    modified_content.append(line)
                                
            # create a new filename
            new_filename = filename.split('.')[0] + NEW_EXTENSION
            
            # write the modified content to the new file
            with open(new_filename, 'wb') as new_file:
                for line in modified_content:
                    # encode the line to bytes and write to the new file
                    new_file.write(line.encode())
                
            print(f"File {filename} has been modified and saved as {new_filename}")
            
    except FileNotFoundError:
        print("File not found.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py filename.kicad_mod description tags")
    else:
        filename = sys.argv[1]
        description = sys.argv[2]
        tags = sys.argv[3]
        modify_footprint(filename, description, tags)