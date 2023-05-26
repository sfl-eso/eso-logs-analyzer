from pathlib import Path

import jinja2
from jinja2 import FileSystemLoader

__TEMPLATE_DIR = "templates/"


def render_template(template_name: str, context: dict) -> str:
    environment = jinja2.Environment(loader=FileSystemLoader(__TEMPLATE_DIR))
    template = environment.get_template(f"{template_name}.jinja2")
    return template.render(context)


def render_to_file(template_name: str, context: dict, output: Path) -> None:
    with open(output, "w") as out_file:
        out_file.write(render_template(template_name, context))
