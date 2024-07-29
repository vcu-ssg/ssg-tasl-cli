
import os
import click
from tasl.utils import add_new_topic,scan_for_topics,copy_topic_file,rename_topic_file, list_topic_files, delete_topic_files
from loguru import logger
from tasl import DEFAULT_LOG_LEVEL

@click.group()
@click.version_option( prog_name='tasl' )
@click.option("--log-level",help="set level for logging messages",default=DEFAULT_LOG_LEVEL )
def cli(log_level):
    """This is a command group for topic-related commands."""
    pass

@cli.command()
@click.argument('topic', metavar='<TOPIC>', type=str)
@click.option("--overwrite",help="Overwrite topic files",is_flag=True, default=False)
@click.option("--template",help="Basename of template file (e.g., template1)",default="template1")
def create(topic,overwrite,template):
    """ Creates new topic files in current folder. """
    logger.debug(f"{overwrite}")
    add_new_topic( topic,overwrite=overwrite, template_base=template )


@cli.command()
@click.argument('filename', type=click.Path(exists=True),nargs=-1)
@click.option("--confirm",help="Save topics to separate files",is_flag=True, default=False)
@click.option("--destination",help="Destination folder for topics",type=click.Path( exists=True, file_okay=False), default=".")
@click.option("--overwrite",help="Overwrite existing topic files",is_flag=True, default=False)
def scanl(filename, confirm, destination, overwrite):
    """ Scan a QMD for topics (lecture file by section).
    
    """

    logger.debug(f"entering scan")
    if isinstance( filename, str ):
        scan_for_topics( filename, confirm=confirm, overwrite=overwrite, destination=destination )
    elif isinstance( filename, tuple ):
        for file in filename:
            scan_for_topics( file, confirm=confirm, overwrite=overwrite, destination=destination )

    else:
        logger.debug(f"type: {type(filename)}\n {filename}" )


@cli.command()
@click.argument('filename', type=click.Path(exists=True),nargs=-1)
@click.option("--confirm",help="Save topics to separate files",is_flag=True, default=False)
@click.option("--destination",help="Destination folder for topics",type=click.Path( exists=True, file_okay=False), default=".")
@click.option("--overwrite",help="Overwrite existing topic files",is_flag=True, default=False)
def copy(filename, confirm, destination, overwrite):
    """ Copies a topic (all related files) to a new folder.
     
       Does not rename topic.

    """

    if isinstance( filename, str ):
        copy_topic_file( filename, confirm=confirm, overwrite=overwrite, destination=destination )
    elif isinstance( filename, tuple ):
        for file in filename:
            copy_topic_file( file, confirm=confirm, overwrite=overwrite, destination=destination )
    else:
        logger.warning(f"Unprocessed type: {type(filename)}\n {filename}" )


@cli.command()
@click.argument('wrapper_qmd', type=click.Path(exists=True),nargs=1)
@click.argument('new_topic', nargs=1)
@click.option("--confirm",help="run the command",is_flag=True, default=False)
def rename(wrapper_qmd, new_topic, confirm ):
    """ Renames topic QMD and related files to new topic in the current folder. """
    original_basename = os.path.splitext(os.path.basename(wrapper_qmd))[0]
    rename_topic_file( original_basename, new_topic, confirm=confirm )


@cli.command()
@click.argument('wrapper_qmd', type=click.Path(exists=True),nargs=1)
@click.option("--confirm",help="run the command",is_flag=True, default=False)
def delete(wrapper_qmd, confirm ):
    """ Deletes topic QMD and related files. """
    original_basename = os.path.basename(wrapper_qmd)
    if confirm:
        delete_topic_files( ["_"+original_basename], confirm=confirm )
#        logger.success(f"Topic {os.path.splitext(os.path.basename(wrapper_qmd))[0]} deleted.")
    else:
        logger.success(f"Topic {os.path.splitext(os.path.basename(wrapper_qmd))[0]} NOT deleted.  Use --confirm")


def parse_comma_separated(ctx, param, value):
    if value:
        return value.split(',')
    return []

@cli.command(context_settings=dict(ignore_unknown_options=True))
@click.argument('filters',nargs=-1,type=click.STRING)
@click.option("--add-tag",help="Assign tag to the files",default=None)
@click.option("--with-tags",callback=parse_comma_separated,help="Include files with these tags",default=None)
@click.option("--without-tags",callback=parse_comma_separated,help="Exclude files with these tags",default=None)
@click.option("--remove-tag",help="Remove tag from files",default=None)
@click.option("--confirm",help="Confirm add or remove of tag",is_flag=True, default=False)
@click.option("--delete",help="Delete matching topics",is_flag=True, default=False)
@click.option("--copy",help="Copy matching topics to destination",is_flag=True, default=False)
@click.option("--destination",help="Destination folder for topics",type=click.Path( exists=True, file_okay=False), default=None)
def list( filters, add_tag, with_tags, without_tags, remove_tag, confirm, delete, copy, destination ):
    """ List topic files by tag """

    logger.debug( filters )
    logger.debug( add_tag )
    logger.debug( remove_tag )
    logger.debug( with_tags )
    logger.debug( without_tags )
    logger.debug( copy )
    logger.debug( destination )

    list_topic_files( filters, add_tag=add_tag, remove_tag=remove_tag, confirm=confirm, 
                     with_tags=with_tags, without_tags=without_tags, delete=delete, copy=copy, destination=destination)



if __name__ == '__main__':
    cli()
