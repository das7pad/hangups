"""Parser for message formatting markup."""

import pathlib
import re

from reparser import Parser, Token, MatchGroup

from hangups import hangouts_pb2


# Common regex patterns
B_LEFT = r'(?:(?<=[^a-zA-Z0-9])|(?<=^))'  # Lookbehind
B_RIGHT = r'(?:(?=[^a-zA-Z0-9])|(?=$))'   # Lookahead

# Regex patterns used by token definitions
MARKDOWN_END = r'(?<![\s\\]){tag}' + B_RIGHT
MARKDOWN_START = B_LEFT + r'(?<!\\){tag}(?!\s)(?!{tag})(?=.+%s)' % MARKDOWN_END
markdown_link = r'(?<!\\)\[(?P<link>.+?)\]\((?P<url>.+?)\)'
HTML_END = r'(?i)</{tag}>'
HTML_START = r'(?i)<{tag}>(?=.+%s)' % HTML_END
html_link = r'(?i)<a\s+href=[\'"](?P<url>.+?)[\'"]\s*>(?P<link>.+?)</a>'
html_img = r'(?i)<img\s+src=[\'"](?P<url>.+?)[\'"]\s*/?>'
html_newline = r'(?i)<br\s*/?>'
newline = r'\n|\r\n'


def _get_tld_regex():
    """get a regex for all public registered top level domains

    Returns:
        str: the regex
    """
    path = pathlib.Path(__file__).with_name('dist') / 'tld.names.regex'
    raw = path.read_text()
    return '(' + raw.strip().replace('\n', '|') + ')'


# Based on URL regex pattern by John Gruber
# (https://gist.github.com/gruber/8891611)
# and a top level domain list
_DOMAINS = _get_tld_regex()
_BALANCED_PARENS = r'\([^\s()]*?\([^\s()]+\)[^\s()]*?\)'
AUTO_LINK = (
    (r'(?i)\b('
     r'(?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:domains)/)'
     r'(?:[^\s()<>{}\[\]]+|balanced_parens|\([^\s]+?\))+'
     r'(?:balanced_parens|\([^\s]+?\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’])|'
     r'(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:domains)\b/?(?!@)))')
    .replace('domains', _DOMAINS).replace('balanced_parens', _BALANCED_PARENS))
# cleanup
del _get_tld_regex
del _DOMAINS
del _BALANCED_PARENS

# Precompiled regex for matching protocol part of URL
url_proto_regex = re.compile(r'(?i)^[a-z][\w-]+:/{1,3}')

# Precompiled regex for removing backslash before escaped Markdown tags
markdown_unescape_regex = re.compile(r'\\([*_~=`\[])')


def markdown(tag):
    """Return start and end regex pattern sequences for simple Markdown tag."""
    return (MARKDOWN_START.format(tag=tag), MARKDOWN_END.format(tag=tag))


def html(tag):
    """Return sequence of start and end regex patterns for simple HTML tag"""
    return (HTML_START.format(tag=tag), HTML_END.format(tag=tag))


def url_complete(url):
    """If URL doesn't start with protocol, prepend it with http://"""
    return url if url_proto_regex.search(url) else 'http://' + url


class Tokens:
    """Groups of tokens to be used by ChatMessageParser"""
    basic = [
        Token('link', AUTO_LINK, link_target=MatchGroup('start',
                                                        func=url_complete)),
        Token('br', newline, text='\n',
              segment_type=hangouts_pb2.SEGMENT_TYPE_LINE_BREAK)
    ]

    markdown = [
        Token('md_bi1', *markdown(r'\*\*\*'), is_bold=True, is_italic=True),
        Token('md_bi2', *markdown(r'___'), is_bold=True, is_italic=True),
        Token('md_b1', *markdown(r'\*\*'), is_bold=True),
        Token('md_b2', *markdown(r'__'), is_bold=True),
        Token('md_i1', *markdown(r'\*'), is_italic=True),
        Token('md_i2', *markdown(r'_'), is_italic=True),
        Token('md_pre3', *markdown(r'```'), skip=True),
        Token('md_pre2', *markdown(r'``'), skip=True),
        Token('md_pre1', *markdown(r'`'), skip=True),
        Token('md_s', *markdown(r'~~'), is_strikethrough=True),
        Token('md_u', *markdown(r'=='), is_underline=True),
        Token('md_link', markdown_link, text=MatchGroup('link'),
              link_target=MatchGroup('url', func=url_complete))
    ]

    html = [
        Token('html_b1', *html(r'b'), is_bold=True),
        Token('html_b2', *html(r'strong'), is_bold=True),
        Token('html_i1', *html(r'i'), is_italic=True),
        Token('html_i2', *html(r'em'), is_italic=True),
        Token('html_s1', *html(r's'), is_strikethrough=True),
        Token('html_s2', *html(r'strike'), is_strikethrough=True),
        Token('html_s3', *html(r'del'), is_strikethrough=True),
        Token('html_u1', *html(r'u'), is_underline=True),
        Token('html_u2', *html(r'ins'), is_underline=True),
        Token('html_u3', *html(r'mark'), is_underline=True),
        Token('html_pre', *html(r'pre'), skip=True),
        Token('html_link', html_link, text=MatchGroup('link'),
              link_target=MatchGroup('url', func=url_complete)),
        Token('html_img', html_img, text=MatchGroup('url'),
              link_target=MatchGroup('url', func=url_complete)),
        Token('html_br', html_newline, text='\n',
              segment_type=hangouts_pb2.SEGMENT_TYPE_LINE_BREAK)
    ]


class ChatMessageParser(Parser):
    """Chat message parser"""
    def __init__(self,
                 tokens=tuple(Tokens.markdown + Tokens.html + Tokens.basic)):
        # we add default tokens here.
        # pylint: disable=dangerous-default-value
        super().__init__(tokens)

    def preprocess(self, text):
        """Preprocess text before parsing"""
        # Replace two consecutive spaces with space and non-breakable space
        # (this is how original Hangouts client does it to preserve multiple
        # spaces)
        return text.replace('  ', ' \xa0')

    def postprocess(self, text):
        """Postprocess text after parsing"""
        # Remove backslash before escaped Markdown tags
        return markdown_unescape_regex.sub(r'\1', text)
