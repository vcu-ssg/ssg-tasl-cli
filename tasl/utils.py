"""
"""
import re
import os
import sys
import yaml
import shutil
import subprocess

from loguru import logger
from collections import OrderedDict

def clean_topic_name( input_string ):
    """ clean topic name for use as a basename in a filename """
    cleaned_string = input_string
    # Remove HTML tags
    cleaned_string = re.sub(r'<.*?>', ' ', cleaned_string)
    # Convert to lowercase
    cleaned_string = cleaned_string.lower()
    # Remove non-alphanumeric characters (except spaces)
    cleaned_string = re.sub(r'[^a-z0-9\s]', ' ', cleaned_string)
    # Replace multiple spaces with a single space
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string)
    # Replace spaces with dashes
    cleaned_string = cleaned_string.replace(' ', '-')
    # Remove leading and trailing dashes
    cleaned_string = cleaned_string.strip('-')
    return cleaned_string

def get_git_root():
    try:
        # Run the Git command to get the root directory
        git_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], universal_newlines=True).strip()
        return git_root
    except subprocess.CalledProcessError:
        raise RuntimeError("Not a git repository or no git repository found.")

def get_repo_relative_path(target_folder):
    git_root = get_git_root()
    abs_target_folder = os.path.abspath(target_folder)
    return os.path.relpath(abs_target_folder, git_root)

def get_repo_relative_path_from_current_dir(git_relative_path):
    # Get the absolute path of the Git root
    git_root = get_git_root()
    
    # Combine the Git root with the given relative path
    target_path = os.path.join(git_root, git_relative_path)
    
    # Get the current working directory
    current_dir = os.getcwd()
    
    # Calculate the relative path from the current directory to the target path
    relative_path = os.path.relpath(target_path, current_dir)
    return relative_path

def get_yaml_header(filename: str):
    """ Opens filename and returns YAML header as python object """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file {filename} does not exist.")

    with open(filename, 'r') as file:
        lines = file.readlines()

    # Find the start and end of the YAML header
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "---" and start_idx is None:
            start_idx = i
        elif line.strip() == "---" and start_idx is not None:
            end_idx = i
            break

    if start_idx is None or end_idx is None:
        raise ValueError("YAML section not properly marked with '---' in the document.")

    # Extract the YAML header
    yaml_header = ''.join(lines[start_idx+1:end_idx])
    content = yaml.safe_load(yaml_header) or {}
    return content


def update_yaml_header(filename: str, **kwargs ):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file {filename} does not exist.")

    with open(filename, 'r') as file:
        lines = file.readlines()

    # Find the start and end of the YAML header
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "---" and start_idx is None:
            start_idx = i
        elif line.strip() == "---" and start_idx is not None:
            end_idx = i
            break

    if start_idx is None or end_idx is None:
        raise ValueError("YAML section not properly marked with '---' in the document.")

    # Extract the YAML header
    yaml_header = ''.join(lines[start_idx+1:end_idx])
    content = yaml.safe_load(yaml_header) or {}

    # Update the "tasl" section with the new dictionary

    for key in kwargs.keys():
        content[key] = kwargs.get(key,None)

    # Reorder the content so that "title" is the first key
    ordered_content = OrderedDict()
    if 'title' in content:
        ordered_content['title'] = content.pop('title')
    ordered_content.update(content)

    # Custom representer to dump OrderedDict as a regular dict
    def dict_representer(dumper, data):
        return dumper.represent_dict(data.items())

    yaml.add_representer(OrderedDict, dict_representer)

    # Convert the updated and ordered content back to YAML
    new_yaml_header = yaml.dump(ordered_content, default_flow_style=False, indent=4)
    logger.debug( new_yaml_header )

    # Reassemble the document with the updated YAML header
    new_lines = lines[:start_idx+1] + new_yaml_header.splitlines(keepends=True) + ["---","\n"] + lines[end_idx+1:]

    with open(filename, 'w') as file:
        file.writelines(new_lines)

def create_file(filename, contents, overwrite=False ):
    """Creates a new file with the given contents.
    
    Args:
        filename (str): The name of the file to create.
        contents (str): The contents to write to the file.
        overwrite (bool): Whether to overwrite the file if it already exists.
    """
    if os.path.exists(filename):
        if not overwrite:
            logger.warning(f"File '{filename}' already exists. Use --overwrite to store")
            sys.exit(1)
        else:
            logger.info(f"File '{filename}' already exists. Overwriting.")
    
    try:
        with open(filename, 'w') as file:
            file.write(contents)
        logger.info(f"File '{filename}' created successfully.")
    except Exception as e:
        logger.error(f"An error occurred while creating the file: {e}")
        sys.exit(1)


def get_wrapper_contents( topic_name, topic_file, template=None ):
    """ return contents of a wrapper file.  If template is available, use it. """
    contents = f"""---
title: "{topic_name}"
---

{{{{< include '{topic_file}' >}}}}

    """
    if not template is None:
        if os.path.exists(template):
            logger.info(f"Using default template: {template}")
            try:
                with open(template, 'r') as file:
                    lines = file.readlines()
                    for i, line in enumerate(lines):
                        if line.startswith("title:"):
                            lines[i] = f"title: {topic_name}\n"
                        if line.startswith("{{<"):
                            lines[i] = f"{{{{< include '{topic_file}' >}}}}"
                    contents = ''.join(lines)
                    return contents
            except Exception as e:
                pass
    return contents

def get_topic_contents( topic_name, template=None ):
    """ return contents for a topic file.  If template is available, use it. """
    contents = f"""# {topic_name}

## Slide 1
:::: {{.columns}}

::: {{.column width="50%"}}
### column 1

* bullet 1
* bullet 2
* bullet 3
:::
::: {{.column width="50%"}}
### column 2

1. item 
1. item
1. item
:::
::::

    """
    if not template is None:
        if os.path.exists(template):
            logger.info(f"Using default template: {template}")
            try:
                with open(template, 'r') as file:
                    # read the lines and drop first line
                    lines = file.readlines()[1:]
                    contents = ''.join(lines)
                    contents = f"# {topic_name}\n" + contents
                    return contents
            except Exception as e:
                pass
    return contents

def add_new_topic( topic_name, overwrite=False, template_base=None,topic_contents=None, destination="." ):
    """ Add new set of topic files to current folder. """

    logger.debug(f"Adding new topic: {topic_name}")
    basename = clean_topic_name( topic_name )
    wrapper_file = basename + ".qmd"
    wrapper_file_and_path = os.path.normpath( os.path.join( destination, basename+".qmd" ) )
    topic_file = "_" + basename + ".qmd"
    topic_file_and_path = os.path.normpath( os.path.join( destination, "_" + basename + ".qmd" ) )

    wrapper_template = None
    topic_template = None
    if not template_base is None:
        wrapper_template = template_base+".qmd"
        topic_template = "_" + wrapper_template

    if os.path.exists( topic_file_and_path ) and os.path.exists( wrapper_file_and_path ):
        logger.success(f"Topic ({topic_name}) already exists.  No changes made.")
        return

    if not os.path.exists( wrapper_file_and_path ):
        contents = get_wrapper_contents( topic_name, topic_file, template=wrapper_template )
        create_file( wrapper_file_and_path, contents, overwrite=overwrite )
    else:
        logger.info(f"Using existing wrapper file: {wrapper_file}")

    if not os.path.exists( topic_file_and_path ):
        contents = get_topic_contents( topic_name, template=topic_template )
        if not topic_contents is None:
            contents = topic_contents
        create_file( topic_file_and_path, contents, overwrite=overwrite )
    else:
        logger.info(f"Using existing topic file: {topic_file}")

    logger.success(f"Topic created: '{topic_name}' to '{os.path.normpath( os.path.join(destination,basename))}' wrapper, topic, and assets")
    return topic_file_and_path, wrapper_file_and_path


def extract_filenames(text):
    # Use a regular expression to find filenames in the text
    pattern = re.compile(r'assets/[^"\)]+')
    matches = pattern.findall(text)
    return matches

def extract_assets_from_file( filename ):
    """ Extract assets/* from a filename """
    with open(filename, 'r') as file:
        lines = file.read()
        assets = extract_filenames( lines )
    return assets


def copy_files_to_destination(destination_folder, file_list, overwrite=False, save=False):
    for file_path in file_list:
        # Construct the full source path
        full_source_path = os.path.normpath( os.path.abspath(file_path) )
        
        # Check if the source file exists
        if not os.path.exists(full_source_path):
            logger.info(f'Source file does not exist: {full_source_path}')
            continue

        if save:
            # Construct the full destination path
            relative_path = os.path.normpath( os.path.relpath(file_path) )
            full_destination_path = os.path.normpath( os.path.join(destination_folder, relative_path) )
            
            # Create any necessary directories at the destination
            os.makedirs(os.path.dirname(full_destination_path), exist_ok=True)
            
            # Check if the file exists and if we should overwrite it
            if os.path.exists(full_destination_path) and not overwrite:
                logger.info(f'Skipped {full_destination_path} (already exists)')
                continue
            
            # Copy the file to the destination
            shutil.copy2(full_source_path, full_destination_path)
            logger.info(f'Copied {file_path} to {full_destination_path}')
        else:
            logger.info(f"Found: {file_path}")

def copy_asset_files( content, destination=".", overwrite=False, save=False ):
    """ scan and copy content (a list) looking for 'assets/*'. """
    logger.debug(f"copying asset files")
    files = []
    for i,line in enumerate( content ):
        matches = extract_filenames( line )
        for match in matches:
            files.append( match )
    logger.debug( files )
    copy_files_to_destination( destination, files, overwrite=overwrite, save=save )
    

def scan_for_topics( filename, save=False, overwrite=False, destination="." ):
    """ scan filename for topics """
    logger.debug(f'entering scan_for_topics: {filename}')
    include_pattern = r'\{\{< include [\'"]?([^\'">]+)[\'"]? >\}\}'

    blocks = {}
    key = "prefix"
    blocks["prefix"] = []
    logger.success(f'Loading: {filename}')
    uses_topics = {}
    try:
        with open(filename, 'r',  encoding='utf-8' ) as file:
            lines = file.readlines()
            ignore = False
            logger.debug(filename)
            for i, line in enumerate(lines):
                if line.startswith("```"):
                    ignore = not ignore
                    if ignore:
                        logger.trace("block on")
                    else:
                        logger.trace("block off")
                    continue
                if not ignore:
                    # this identifies a block.
                    if line.startswith("# "):
                        key = line[2:].strip()
                        logger.debug(f"found {key}")
                        blocks[key] = []
                        continue
                    # identify list of topics used.
    
                    # Search for the pattern in the given line
                    match = re.search(include_pattern, line)
                    if match:
                        uses_topics[ match.group(1) ] = match.group(1)

                blocks[key].append( line )
    except Exception as e:
        logger.error(f"unable to load file: {filename}\n{e}")
        sys.exit(1)

    # with each block identified, create new files in destination
    for key in [ key for key in blocks.keys() if not key in ['prefix'] ]:
        if save:
            topic_file_and_path,wrapper_file_and_path = add_new_topic( key, destination=destination, overwrite=overwrite, topic_contents="\n".join( blocks[key]) )
            copy_asset_files( blocks[key], destination=destination, overwrite=overwrite, save=save )
            tasl = dict( topic=key, source=get_repo_relative_path( filename ) )
            update_yaml_header( wrapper_file_and_path, tasl=tasl )
        else:
            logger.success(f"Found: {clean_topic_name( key )}" )
            # this call to copy_asset_files will only display asset file found
            copy_asset_files( blocks[key], destination=destination, overwrite=overwrite, save=save )

    for key in uses_topics:
        logger.success(f"Includes: {key}")

    if (not save) and (len( blocks.keys() ) > 1):
        logger.warning(f"Use --save to save topics to files.  Use --overwrite if files already exists.")


def copy_topic_file( filename, save=False, overwrite=False, destination="." ):
    """ Copy a topic identified by it's wrapper file to a new destination folder """
    logger.debug(f"Entering copy_topic_file: {filename}")
    files = []
    files.append( filename )
    topic_file = "_" + filename
    files.append( topic_file )
    files = files + extract_assets_from_file( topic_file )
    logger.debug( files )
    copy_files_to_destination( destination, files, overwrite=overwrite,save=save )
    if save:
        logger.success(f"Topic {filename} copied to {destination}")
    else:
        logger.success(f"Topic {filename} not copied to {destination}.  Use --save")

def rename_topic_includes( filename, old_topic_file, new_topic_file ):
    with open(filename, 'r') as file:
        lines = file.readlines()
    new_lines = []
    for i,line in enumerate(lines):
        if old_topic_file in line:
            line = line.replace(old_topic_file, new_topic_file )
            logger.debug(f"replacing {old_topic_file} with {new_topic_file}")
        new_lines.append( line )
    with open(filename, 'w') as file:
        file.writelines(new_lines)
    return


def rename_topic_file( basename, new_topic, confirm=False ):
    """ rename a topic identified by it's wrapper file to a new topic name """
    logger.debug(f"Renaming {basename} to {new_topic}")

    original_wrapper_file = basename + ".qmd"
    original_topic_file = "_" + original_wrapper_file
    ok = True
    if not os.path.exists( original_wrapper_file ):
        logger.warning(f"Missing {original_wrapper_file}.  Check your folder.")
        ok = False
    if not os.path.exists( original_topic_file ):
        logger.warning(f"Missing {original_topic_file}.  Check your folder.")
        ok = False

    new_basename = clean_topic_name( new_topic )
    new_wrapper_file = new_basename + ".qmd"
    new_topic_file = "_" + new_wrapper_file

    if os.path.exists( new_wrapper_file ):
        logger.warning(f"Already exists {new_wrapper_file}.  Try a different topic name.")
        ok = False

    if os.path.exists( new_topic_file ):
        logger.warning(f"Already exists {new_topic_file}.  Try a different topic name.")
        ok = False

    if ok and confirm:
        shutil.move( original_wrapper_file, new_wrapper_file )
        shutil.move( original_topic_file, new_topic_file )
        rename_topic_includes( new_wrapper_file, original_topic_file, new_topic_file )
        update_yaml_header( new_wrapper_file, title=new_topic )
        logger.success(f"Topic renamed from '{basename}' to '{new_basename}'")
    elif not confirm:
        logger.success(f"Topic NOT renamed from '{basename}' to '{new_basename}'.  Use --confirm")


def categorize_keywords(keywords):
    """
    Categorize keywords into include and exclude lists.

    :param keywords: List of keywords with '+' or '-' prefixes.
    :return: Tuple containing include list and exclude list.
    """
    include = []
    exclude = []

    for keyword in keywords:
        if keyword.startswith('+'):
            include.append(keyword[1:].strip())
        elif keyword.startswith('--'):
            logger.warning(f"unrecognized option: {keyword}.  Ignoring.")
        elif keyword.startswith('-'):
            exclude.append(keyword[1:].strip())

    return include, exclude

def load_topic_files_from_directory(directory_path):
    """
    Load all files in the specified directory.

    :param directory_path: Path to the directory containing files.
    :return: Dictionary with filenames as keys and file contents as values.
    """
    files_content = {}

    files = os.listdir( directory_path )
    for filename in [file for file in files if str(file).startswith("_") and file[1:] in files]:
        file_path = os.path.join(directory_path, filename)
        
        if os.path.isfile(file_path):
            try:
                with open(file_path, 'r') as file:
                    files_content[filename] = dict(content=file.read())
                files_content[filename]["yaml"] = get_yaml_header( filename[1:] )
            except Exception as e:
                logger.error(f"An error occurred: {file_path}\n{e}")
                return {}
            
    return files_content

def search_files(directory_path, include_keywords, exclude_keywords, with_tags=[], without_tags=[]):
    """
    Search text files for specific keywords to include and exclude.

    :param directory_path: Path to the directory containing files.
    :param include_keywords: List of keywords to include.
    :param exclude_keywords: List of keywords to exclude.
    :param with_tag: list of tags to include
    :param without_tags
    :return: List of filenames that meet the criteria.
    """
    files_content = load_topic_files_from_directory(directory_path)

    if files_content=={}:
        result_files = []
        return


    result_files = [file for file in files_content]
    logger.debug(f"include_keywords: {include_keywords}")
    logger.debug(f"with_tags: {with_tags}")
    if (len(include_keywords)>0) or (len(with_tags)>0):
        result_files = []
        for filename, content in files_content.items():
            include = any(keyword.lower() in content["content"].lower() for keyword in include_keywords)
            if include:
                result_files.append(filename)
                logger.debug(f'including: {filename}')
            
            if "tags" in content["yaml"]:
                include = any(keyword.lower() in content["yaml"]["tags"] for keyword in with_tags)
                if include and not( filename in result_files ):
                    result_files.append( filename )
                    logger.debug(f'including: {filename} for tags: {content["yaml"]["tags"]}')

    if len(exclude_keywords)>0 or (len(without_tags)>0):
        for filename, content in files_content.items():
            exclude = any(keyword.lower() in content["content"].lower() for keyword in exclude_keywords)
            if exclude:
                logger.debug(f'excluding: {filename}')
                result_files = [ file for file in result_files if not file==filename ]
            if "tags" in content["yaml"]:
                exclude = any(keyword.lower() in content["yaml"]["tags"] for keyword in without_tags)
                if exclude and ( filename in result_files ):
                    result_files = [ file for file in result_files if not file==filename ]

    available_tags = []
    for file in result_files:
        if "tags" in files_content[file]["yaml"].keys():
            for tag in files_content[file]["yaml"]["tags"]:
                if not tag in available_tags:
                    available_tags.append( tag )

    return result_files, available_tags

def delete_topic_files( files,confirm=False ):
    """ delete files.  Assumes files are topics with leading understore, e.g. _sample-topic.qmd """
    if confirm:
        for file in files:
            ok = True
            if os.path.isfile(file):
                os.remove(file)
            else:
                ok = False
                logger.warning(f"File not found: {file}")
            if os.path.isfile(file[1:]):
                os.remove( file[1:])
            else:
                ok = False
                logger.warning(f"File not found: {file[1:]}")
            if ok:
                logger.success(f"Topic {os.path.splitext(os.path.basename(file[1:]))[0]} deleted.")

    return


def list_topic_files( filters, add_tag=None, remove_tag=None, confirm=False, with_tags=None, without_tags=None, delete=False):
    """ List topic files with filters """
    
    directory_path = "."
    include,exclude = categorize_keywords( filters )
    result_files, result_tags = search_files( directory_path, include, exclude, with_tags=with_tags, without_tags=without_tags )

    if result_files is None:
        logger.success(f"Error loading files")
        return
    if len(include)>0:
        logger.success(f"Including files with words: '{ ','.join(include)}'")
    else:
        logger.success(f"Including all files.")
    if len(exclude)>0:
        logger.success(f"Excluding files with words: '{ ','.join(exclude)}'")
    else:
        logger.success(f"Excluding no files.")

    if result_files==[]:
        logger.success(f"No files meet criteria")
        return

    logger.success(f"Available tags: {result_tags}")

    for file in result_files:
        logger.success(f"Found: {file}" )

    if delete:
        if confirm:
            delete_topic_files( result_files,confirm )
            logger.success("Deleted matching topics.")
        else:
            logger.success("NOT deleting matching topics.  Use --confirm")
        return
    
    if not add_tag is None:
        if confirm:
            for file in result_files:
                logger.debug(f"getting header from: {file[1:]}")
                header = get_yaml_header( file[1:] )
                logger.debug( header )
                if not "tags" in header.keys():
                    header["tags"] = []
                if not add_tag.lower() in header["tags"]:
                    header["tags"].append( add_tag.lower() )
                logger.debug( header )
                update_yaml_header(file[1:], **header )
                h2 = get_yaml_header( file[1:] )
                logger.debug(f"h2: {h2}")
            logger.success(f"Adding tag: '{add_tag}' to YAML headers.")
        else:
            logger.success(f"NOT Adding tag: '{add_tag}' to YAML headers.  Use --confirm")

    if not remove_tag is None:
        if confirm:
            for file in result_files:
                logger.debug(f"getting header from: {file[1:]}")
                header = get_yaml_header( file[1:] )
                logger.debug( header )
                if not "tags" in header.keys():
                    header["tags"] = []
                if remove_tag in header["tags"]:
                    header["tags"] = [ tag for tag in header["tags"] if not tag.lower()==remove_tag.lower() ]
                logger.debug( header )
                update_yaml_header(file[1:], **header )
                h2 = get_yaml_header( file[1:] )
                logger.debug(f"h2: {h2}")
            logger.success(f"Removing tag: '{add_tag}' from YAML headers.")
        else:
            logger.success(f"NOT Removing tag: '{remove_tag}' to YAML headers.  Use --confirm")


