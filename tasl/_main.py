import click
from tasl.utils import add_new_topic
from loguru import logger

@click.group()
def cli():
    """This is a command group for topic-related commands."""
    pass

@cli.command()
@click.argument('topic', metavar='<TOPIC>', type=str)
@click.option("--overwrite",help="Overwrite topic files",is_flag=True, default=False)
@click.option("--template",help="Basename of template file (e.g., template1)",default="template1")
def add(topic,overwrite,template):
    """ Adds new topic to current folder. """
    logger.success(f"{overwrite}")
    add_new_topic( topic,overwrite=overwrite, template_base=template )


if __name__ == '__main__':
    cli()
