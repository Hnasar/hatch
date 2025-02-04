import re
import textwrap

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

_code_tab_regex = re.compile(
    r'^( *)((`{3,})[^ ].*) tab="(.+)"\n([\s\S]+?)\n\1\3$',
    re.MULTILINE,
)
_config_example_regex = re.compile(
    r'^( *)((`{3,})toml\b.*) config-example\n([\s\S]+?)\n\1\3$',
    re.MULTILINE,
)


def _code_tab_replace(m):
    indent, fence_start, fence_end, title, content = m.groups()
    return f"""\
{indent}=== ":octicons-file-code-16: {title}"
{indent}    {fence_start}
{textwrap.indent(content, '    ')}
{indent}    {fence_end}
"""


def _config_example_replace(m):
    indent, fence_start, fence_end, content = m.groups()
    content_without = re.sub(r' *\[tool.hatch\]\n', '', content.replace('[tool.hatch.', '['))
    return f"""\
{indent}=== ":octicons-file-code-16: pyproject.toml"
{indent}    {fence_start}
{textwrap.indent(content, '    ')}
{indent}    {fence_end}

{indent}=== ":octicons-file-code-16: hatch.toml"
{indent}    {fence_start}
{textwrap.indent(content_without, '    ')}
{indent}    {fence_end}
"""


def on_config(config, **kwargs):
    config.markdown_extensions.append(MyExtension())


class MyExtension(Extension):
    def extendMarkdown(self, md):  # noqa: N802
        md.preprocessors.register(MyPreprocessor(), 'mypreprocessor', 100)


class MyPreprocessor(Preprocessor):
    def run(self, lines):
        markdown = '\n'.join(lines)
        markdown = _config_example_regex.sub(_config_example_replace, markdown)
        markdown = _code_tab_regex.sub(_code_tab_replace, markdown)
        return markdown.split('\n')
