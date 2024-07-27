"""
"""
import re
import os
import sys

from loguru import logger


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
        logger.warning(f"An error occurred while creating the file: {e}")
        sys.exit(1)


def get_wrapper_contents( topic_name, topic_file, template=None ):
    """ return contents of a wrapper file.  If template is available, use it. """
    contents = f"""---
title: {topic_name}
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
    wrapper_file = os.path.join( destination, basename+".qmd" )
    topic_file = "_" + basename + ".qmd"
    topic_file_and_path = os.path.join( destination, "_" + basename + ".qmd" )

    wrapper_template = None
    topic_template = None
    if not template_base is None:
        wrapper_template = template_base+".qmd"
        topic_template = "_" + wrapper_template

    contents = get_wrapper_contents( topic_name, topic_file, template=wrapper_template )
    create_file( wrapper_file, contents, overwrite=overwrite )

    contents = get_topic_contents( topic_name, template=topic_template )
    if not topic_contents is None:
        contents = topic_contents

    create_file( topic_file_and_path, contents, overwrite=overwrite )

    logger.success(f"Created: '{topic_name}' to '{os.path.join(destination,basename)}' wrapper and topic qmds")


def scan_for_topics( filename, save=False, overwrite=False, destination="." ):
    """ scan filename for topics """
    logger.debug(f'entering scan_for_topics: {filename}')

    blocks = {}
    key = "prefix"
    blocks["prefix"] = []
    try:
        with open(filename, 'r',  encoding='utf-8' ) as file:
            lines = file.readlines()
            ignore = False
            logger.debug(filename)
            for i, line in enumerate(lines):
                if line.startswith("```"):
                    ignore = not ignore
                    if ignore:
                        logger.debug("block on")
                    else:
                        logger.debug("block off")
                    continue
                if not ignore:
                    if line.startswith("# "):
                        key = line[2:].strip()
                        logger.debug(f"found {key}")
                        blocks[key] = []
                        continue
                blocks[key].append( line )
    except Exception as e:
        logger.error(f"unable to load file: {filename}\n{e}")
        sys.exit(1)

    for key in [ key for key in blocks.keys() if not key in ['prefix'] ]:

        if save:
            add_new_topic( key, destination=destination, overwrite=overwrite, topic_contents="\n".join( blocks[key]) )
        else:
            logger.success(f"Found: {clean_topic_name( key )}" )

    if (not save) and (len( blocks.keys() ) > 1):
        logger.warning(f"Use --save to save topics to files.  Use --overwrite if files already exists.")



