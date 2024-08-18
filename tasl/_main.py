
import os
import glob
import click
from tasl.utils import add_new_topic,scan_for_topics,copy_topic_file,rename_topic_file, list_topic_files, \
      delete_topic_files, update_yaml_header, get_yaml_header
from tasl.slides_from_guide import slides_from_qmd
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


@cli.command()
@click.option('--file', help="specify a single file to process", type=click.Path(exists=True), default=None )
@click.option("--folder",help="convert all files in this folder",type=click.Path(exists=True), default=None)
@click.option("--exclude-files",multiple=True, type=click.Path(), help="exclude these files from the folder",default=['index.qmd'])
@click.option("--confirm",help="perform the conversion",is_flag=True, default=False)
@click.option("--delete",help="delete the files from current folder",is_flag=True, default=False)
@click.option("--add-tag",help="Assign tag to the files",default=None)
def slides_from(file, folder, exclude_files, confirm, delete,add_tag ):
    """ Deletes topic QMD and related files. """
    if file is None and folder is None:
        logger.error("Must specific either --file or --folder")
        return
    
    if not file is None:
        one_file = file
        if confirm:
            slides_from_qmd( file )        
            logger.success(f"Topic from guide: {os.path.splitext(os.path.basename(file))[0]}.")
        else:
            # Print or process the filtered files
            if os.path.exists( os.path.basename(one_file) ):
                logger.warning(f"{one_file} already exists.")
            else:
                logger.success(f"Topic from guide: {os.path.splitext(os.path.basename(file))[0]} NOT built.  Use --confirm")

    if not folder is None:
        all_files = glob.glob(os.path.join(folder, '*'))
        filtered_files = [f for f in all_files if os.path.basename(f) not in exclude_files]

        if confirm:
            for one_file in filtered_files:
                if (not add_tag is None) and os.path.exists( os.path.basename(one_file) ):

                    logger.debug(f"getting header from: { os.path.basename(one_file)}")
                    header = get_yaml_header(  os.path.basename(one_file) )
                    logger.debug( header )
                    if not "tasl" in header.keys():
                        header["tasl"] = {}
                    if not "tags" in header["tasl"]:
                        header["tasl"]["tags"] = []
                    if not add_tag.lower() in header["tasl"]["tags"]:
                        header["tasl"]["tags"].append( add_tag.lower() )
                    logger.debug( header )
                    update_yaml_header( os.path.basename(one_file), **header )
                    h2 = get_yaml_header(  os.path.basename(one_file) ) 
                    logger.debug(f"h2: {h2}")
                    logger.success(f"Added tag: '{add_tag}' to YAML headers for { os.path.basename(one_file) }.")

                elif not delete:
                    
                    slides_from_qmd( one_file )
                    logger.success(f"Topic from guide: {os.path.splitext(os.path.basename(one_file))[0]} built.")
                  
                else:
                    if os.path.exists( os.path.basename(one_file) ):
                        os.remove( os.path.basename(one_file) )
                    if os.path.exists( os.path.basename("_"+one_file) ):
                        os.remove( os.path.basename("_"+ one_file ) )
                    logger.success(f"Topic deleted from current folder: {os.path.splitext(os.path.basename(one_file))[0]}")
        else:
            for one_file in filtered_files:
                if os.path.exists( os.path.basename(one_file) ):
                    if delete:
                        logger.success(f"Not deleting topic {os.path.basename(one_file)}.  Use --confirm.")
                    elif (not add_tag is None) and os.path.exists( os.path.basename(one_file) ):
                        logger.success(f"Tag NOT added: '{add_tag}' to YAML headers for { os.path.basename(one_file) }. Use --confirm")
                    else:
                        logger.warning(f"Topic exists: {os.path.splitext(os.path.basename(one_file))[0]} NOT built.  Use --confirm")
                else:
                    logger.success(f"Topic from guide: {os.path.splitext(os.path.basename(one_file))[0]} NOT built.  Use --confirm")


if __name__ == '__main__':
    cli()
