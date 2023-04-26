import os
import shutil
import sys

cp_dirs = {
        '.js': 'src_code','.h': 'src_code', '.c': 'src_code', '.php': 'src_code',
        '.phpt': 'src_code', '.kt': 'src_code', '.py': 'src_code', '.sh': 'src_code',
        '.pl': 'src_code', '.rb': 'src_code', '.go': 'src_code', '.java': 'src_code',
        '.hpp': 'src_code', '.rst': 'src_code', '.ads': 'src_code', '.adb': 'src_code',
        '.rs': 'src_code', '.cpp': 'src_code', '.cc': 'src_code', '.cxx': 'src_code',
        '.hxx': 'src_code', '.sql': 'src_code', '.asm': 'src_code', 
        '.pyx': 'src_code', '.lua' : 'src_code', 

        '.dll': 'exec', '.so': 'exec', '.deb': 'exec', '.ko': 'exec',
        '.pyc': 'exec', '.pm': 'exec', '.opq': 'exec', '.beam': 'exec',
        '.0': 'exec', '.1': 'exec', '.3': 'exec', '.jar': 'exec',
        '.exe': 'exec', '.bin': 'exec', '.o': 'exec', '.a': 'exec',
        '.cmd': 'exec', '.bat': 'exec', '.pt': 'exec',

        '.pak': 'res', '.json': 'res', '.tid': 'res', '.map': 'res',
        '.md': 'res', '.flow': 'res', '.html': 'res', '.css': 'res',
        '.multids': 'res', '.yml': 'res', '.txt': 'res', '.jst': 'res',
        '.proto': 'res', '.dat': 'res', '.xml': 'res', '.conf': 'res',
        '.mo': 'res', '.properties': 'res', '.po': 'res', '.lock': 'res',
        '.list': 'res', '.shlibs': 'res', '.spec': 'res', '.tfm': 'res',
        '.ali': 'res', '.page': 'res', '.info': 'res', '.desktop': 'res',
        '.d': 'res', '.xpm': 'res', '.vf': 'res', '.htm': 'res',
        '.cfg': 'res', 'xhtml': 'res', '.tmpl': 'res', '.tmpl.in': 'res',
        '.csv': 'res', '.pyi': 'res', '.in': 'res', '.jsonc': 'res',
        '.yaml': 'res', '.eb': 'res', '.csl': 'res', '.scss': 'res',
        '.pos': 'res', '.less': 'res', '.woff': 'res', '.ttf': 'res',
        '.ini': 'res', '.zcml': 'res', '.typed': 'res', '.j2': 'res',
        '.ipynb': 'res', '.pickle': 'res', '.woff2': 'res', '.cif': 'res',
        '.npy': 'res', '.toml': 'res', '.eot': 'res', '.svg': 'res',
        '.geojson': 'res', '.cu': 'res', '.h5': 'res', '.hdf5': 'res',

        '.svg': 'media', '.jpg': 'media', '.gif': 'media',
        '.ts': 'media', '.png': 'media', '.ico': 'media', '.bmp': 'media',
        '.ogg': 'media', '.mp3': 'media', '.wav': 'media', '.mp4': 'media',
        '.webp': 'media', '.webm': 'media', '.mkv': 'media', '.avi': 'media',
    }

def classify():
    if len(sys.argv) < 4:
        print('Usage: python file_cly.py SOURCE_DIR DEST_DIR PACKAGE_NAME(deb, apk, electron, python, container) [-d]')
        sys.exit(1)

    source_dir = sys.argv[1]
    dest_dir = sys.argv[2]
    # Deb, Apk, Electron App, Python, Container Image, etc.
    package_name = sys.argv[3]
    
    global debug_mode
    debug_mode = False
    # Check argv[4] is debug mode or not
    if len(sys.argv) == 5:
        if sys.argv[4] == '-d':
            print('Debug mode.')
            debug_mode = True
        else:
            print('Unknown argument.')
            sys.exit(1)

    # check if the dest directory exists
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    
    # create a dictionary to store the number of files of each type
    file_types = {}

    # loop through all files and count their types
    for dirpath, dirnames, filenames in os.walk(source_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            # check if file is symbolic link
            if os.path.islink(filepath):
                continue
            extension = os.path.splitext(filename)[1]
            if extension == '':
                extension = 'no_extension'
            if extension not in file_types:
                file_types[extension] = 0
            file_types[extension] += 1

    # calculate the total number of files
    total_files = sum(file_types.values())

    # print the total number of files to a file
    with open(os.path.join(dest_dir, 'file_counts.txt'), 'w') as f:
        f.write(f'Total files: {total_files}\n')
    # print(f'Total files: {total_files}\n')

    # sort the file types by their counts
    sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)

    if package_name == 'deb':
        copy_files_deb(total_files, sorted_types, source_dir, dest_dir)
    elif package_name == 'electron':
        copy_files_electron(total_files, sorted_types, source_dir, dest_dir)
    elif package_name == 'apk':
        copy_files_apk(total_files, sorted_types, source_dir, dest_dir)
    elif package_name == 'python':
        copy_files_python(total_files, sorted_types, source_dir, dest_dir)
    elif package_name == 'container':
        copy_files_container(total_files, sorted_types, source_dir, dest_dir)
    else:
        print('Unknown package type')
        sys.exit(1)

def do_mkdir(cp_dirs, dest_dir):
    if debug_mode:
        print('Debug mode. Not creating directories.')
    else:
        print('Creating directories...')
        for cp_dir in cp_dirs.values():
            if not os.path.exists(os.path.join(dest_dir, cp_dir)):
                os.mkdir(os.path.join(dest_dir, cp_dir))
        if not os.path.exists(os.path.join(dest_dir, 'others')):
            os.mkdir(os.path.join(dest_dir, 'others'))

def do_copy(total_files, sorted_types, source_dir, dest_dir, cp_dirs):
    # loop through all file types and calculate their proportions
    for extension, count in sorted_types:
        proportion = count / total_files
        # print(f'{extension}: {count} files, {proportion:.2%}\n')
        with open(os.path.join(dest_dir, 'file_counts.txt'), 'a') as f:
            f.write(f'{extension}: {count} files, {proportion:.2%}\n')

        if debug_mode:
            print("Debug mode. Not copying files.")
        else:
            print(f'Copying {extension} files...')
            same_file_count = 0
            
            if extension in cp_dirs:
                cp_dir = cp_dirs[extension]
                dirname = os.path.join(dest_dir, cp_dir)
            else:
                dirname = os.path.join(dest_dir, 'others')
            # copy files of this type into the new directory in the destination directory
            for dirpath, dirnames, filenames in os.walk(source_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.islink(filepath):
                        continue
                    if filename.endswith(extension):
                        src_path = filepath
                        dst_path = os.path.join(dirname, filename)
                        # check if the file already exists in the destination directory
                        if os.path.exists(dst_path):
                            # if so, append a number to the filename
                            same_file_count += 1
                            dst_path = os.path.join(dirname, f'{same_file_count}_{filename}')
                        assert not os.path.exists(dst_path)
                        shutil.copy(src_path, dst_path)

def copy_files_deb(total_files, sorted_types, source_dir, dest_dir):
    
    # create source directories for different file types
    cp_dirs_deb = cp_dirs

    # mkdir src_code, exec, res, media, others directories in dest_dir
    do_mkdir(cp_dirs=cp_dirs_deb, dest_dir=dest_dir)
    
    # copy files to dest_dir
    do_copy(total_files=total_files, sorted_types=sorted_types, 
            source_dir=source_dir, dest_dir=dest_dir, cp_dirs=cp_dirs_deb)

def copy_files_electron(total_files, sorted_types, source_dir, dest_dir):

    # create source directories for different file types
    cp_dirs = {
        '.js': 'src_code','.h': 'src_code', '.c': 'src_code',
        '.m': 'src_code', '.kt': 'src_code', '.py': 'src_code', '.sh': 'src_code',

        '.dll': 'exec', '.so': 'exec', '.deb': 'exec',

        '.pak': 'res', '.json': 'res', '.tid': 'res', '.map': 'res',
        '.md': 'res', '.flow': 'res', '.html': 'res', '.css': 'res',
        '.multids': 'res', '.yml': 'res', '.txt': 'res', '.jst': 'res',
        '.proto': 'res', '.dat': 'res', '.xml': 'res',

        '.svg': 'media', '.jpg': 'media', '.gif': 'media',
        '.ts': 'media',
    }

    # mkdir src_code, exec, res, media, others directories in dest_dir
    do_mkdir(cp_dirs=cp_dirs, dest_dir=dest_dir)

    # copy files to dest_dir
    do_copy(total_files=total_files, sorted_types=sorted_types,
            source_dir=source_dir, dest_dir=dest_dir, cp_dirs=cp_dirs)

def copy_files_apk(total_files, sorted_types, source_dir, dest_dir):
    
    # create source directories for different file types
    cp_dirs_apk = cp_dirs

    # mkdir src_code, exec, res, media, others directories in dest_dir
    do_mkdir(cp_dirs=cp_dirs_apk, dest_dir=dest_dir)

    # copy files to dest_dir
    do_copy(total_files=total_files, sorted_types=sorted_types,
            source_dir=source_dir, dest_dir=dest_dir, cp_dirs=cp_dirs_apk)

def copy_files_python(total_files, sorted_types, source_dir, dest_dir):
    
    # create source directories for different file types
    cp_dirs_python = cp_dirs

    # mkdir src_code, exec, res, media, others directories in dest_dir
    do_mkdir(cp_dirs=cp_dirs_python, dest_dir=dest_dir)

    # copy files to dest_dir
    do_copy(total_files=total_files, sorted_types=sorted_types,
            source_dir=source_dir, dest_dir=dest_dir, cp_dirs=cp_dirs_python)

def copy_files_container(total_files, sorted_types, source_dir, dest_dir):
    
    # create source directories for different file types
    cp_dirs_container = cp_dirs
    # mkdir src_code, exec, res, media, others directories in dest_dir
    do_mkdir(cp_dirs=cp_dirs_container, dest_dir=dest_dir)

    # copy files to dest_dir
    do_copy(total_files=total_files, sorted_types=sorted_types,
            source_dir=source_dir, dest_dir=dest_dir, cp_dirs=cp_dirs_container)

if __name__ == '__main__':
    classify()