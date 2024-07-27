"""
"""
import re
import os
import sys

from loguru import logger


def clean_topic_name( input_string ):
    """ clean topic name for use as a basename in a filename """
    # Convert to lowercase
    cleaned_string = input_string.lower()
    # Remove non-alphanumeric characters (except spaces)
    cleaned_string = re.sub(r'[^a-z0-9\s]', '', cleaned_string)
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
            logger.warning(f"File '{filename}' already exists. Exiting without overwriting.")
            sys.exit(1)
        else:
            logger.info(f"File '{filename}' already exists. Overwriting.")
    
    try:
        with open(filename, 'w') as file:
            file.write(contents)
        logger.info(f"File '{filename}' created successfully.")
    except Exception as e:
        logger.warning(f"An error occurred while creating the file: {e}")


def get_wrapper_contents( topic_name, topic_file ):
    """ return contents of a wrapper file.  If template is available, use it. """
    contents = f"""---
title: {topic_name}
---

{{{{< include '{topic_file}' >}}}}

    """
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

def add_new_topic( topic_name, overwrite=False, template_base=None ):
    """ Add new set of topic files to current folder. """
    logger.info(f"Adding new topic: {topic_name}")
    basename = clean_topic_name( topic_name )
    wrapper_file = basename+".qmd"
    topic_file = "_" + wrapper_file

    wrapper_template = None
    topic_template = None
    if not template_base is None:
        topic_template = "_" + template_base+".qmd"

    contents = get_wrapper_contents( topic_name, topic_file )
    create_file( wrapper_file, contents, overwrite=overwrite )

    contents = get_topic_contents( topic_name, template=topic_template )
    create_file( topic_file, contents, overwrite=overwrite )

