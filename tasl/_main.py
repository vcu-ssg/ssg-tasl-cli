import click
from tasl.utils import add_new_topic,scan_for_topics
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
def add(topic,overwrite,template):
    """ Adds new topic to current folder. """
    logger.debug(f"{overwrite}")
    add_new_topic( topic,overwrite=overwrite, template_base=template )

@cli.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option("--save",help="Save topics to separate files",is_flag=True, default=False)
@click.option("--destination",help="Destination folder for topics",type=click.Path( exists=True, file_okay=False), default=".")
@click.option("--overwrite",help="Overwrite existing topic files",is_flag=True, default=False)
def scan(filename, save, destination, overwrite):
    """ Scan for topics in a QMD lecture file. """

    logger.debug(f"entering scan")
    scan_for_topics( filename, save=save, overwrite=overwrite, destination=destination )



if __name__ == '__main__':
    cli()
