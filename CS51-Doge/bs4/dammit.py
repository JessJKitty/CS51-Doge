# -*- coding: utf-8 -*-
"""Beautiful Soup bonus library: Unicode, Dammit

This class forces XML data into a standard format (usually to UTF-8 or
Unicode).  It is heavily based on code from Mark Pilgrim's Universal
Feed Parser. It does not rewrite the XML or HTML to reflect a new
encoding; that's the tree builder's job.
"""

import codecs
from htmlentitydefs import codepoint2name
import re
import warnings

# Autodetects character encodings. Very useful.
# Download from http://chardet.feedparser.org/
#  or 'apt-get install python-chardet'
#  or 'easy_install chardet'
try:
    import chardet
    #import chardet.constants
    #chardet.constants._debug = 1
except ImportError:
    chardet = None

# Available from http://cjkpython.i18n.org/.
try:
    import iconv_codec
except ImportError:
    pass

xml_encoding_re = re.compile(
    '^<\?.*encoding=[\'"](.*?)[\'"].*\?>'.encode(), re.I)
html_meta_re = re.compile(
    '<\s*meta[^>]+charset\s*=\s*["\']?([^>]*?)[ /;\'">]'.encode(), re.I)

class EntitySubstitution(object):

    """Substitute XML or HTML entities for the corresponding characters."""

    def _populate_class_variables():
        lookup = {}
        reverse_lookup = {}
        characters_for_re = []
        for codepoint, name in list(codepoint2name.items()):
            character = unichr(codepoint)
            if codepoint != 34:
                # There's no point in turning the quotation mark into
                # &quot;, unless it happens within an attribute value, which
                # is handled elsewhere.
                characters_for_re.append(character)
                lookup[character] = name
            # But we do want to turn &quot; into the quotation mark.
            reverse_lookup[name] = character
        re_definition = "[%s]" % "".join(characters_for_re)
        return lookup, reverse_lookup, re.compile(re_definition)
    (CHARACTER_TO_HTML_ENTITY, HTML_ENTITY_TO_CHARACTER,
     CHARACTER_TO_HTML_ENTITY_RE) = _populate_class_variables()

    CHARACTER_TO_XML_ENTITY = {
        "'": "apos",
        '"': "quot",
        "&": "amp",
        "<": "lt",
        ">": "gt",
        }

    BARE_AMPERSAND_OR_BRACKET = re.compile("([<>]|"
                                           "&(?!#\d+;|#x[0-9a-fA-F]+;|\w+;)"
                                           ")")

    @classmethod
    def _substitute_html_entity(cls, matchobj):
        entity = cls.CHARACTER_TO_HTML_ENTITY.get(matchobj.group(0))
        return "&%s;" % entity

    @classmethod
    def _substitute_xml_entity(cls, matchobj):
        """Used with a regular expression to substitute the
        appropriate XML entity for an XML special character."""
        entity = cls.CHARACTER_TO_XML_ENTITY[matchobj.group(0)]
        return "&%s;" % entity

    @classmethod
    def quoted_attribute_value(self, value):
        """Make a value into a quoted XML attribute, possibly escaping it.

         Most strings will be quoted using double quotes.

          Bob's Bar -> "Bob's Bar"

         If a string contains double quotes, it will be quoted using
         single quotes.

          Welcome to "my bar" -> 'Welcome to "my bar"'

         If a string contains both single and double quotes, the
         double quotes will be escaped, and the string will be quoted
         using double quotes.

          Welcome to "Bob's Bar" -> "Welcome to &quot;Bob's bar&quot;
        """
        quote_with = '"'
        if '"' in value:
            if "'" in value:
                # The string contains both single and double
                # quotes.  Turn the double quotes into
                # entities. We quote the double quotes rather than
                # the single quotes because the entity name is
                # "&quot;" whether this is HTML or XML.  If we
                # quoted the single quotes, we'd have to decide
                # between &apos; and &squot;.
                replace_with = "&quot;"
                value = value.replace('"', replace_with)
            else:
                # There are double quotes but no single quotes.
                # We can use single quotes to quote the attribute.
                quote_with = "'"
        return quote_with + value + quote_with

    @classmethod
    def substitute_xml(cls, value, make_quoted_attribute=False):
        """Substitute XML entities for special XML characters.

        :param value: A string to be substituted. The less-than sign will
          become &lt;, the greater-than sign will become &gt;, and any
          ampersands that are not part of an entity defition will
          become &amp;.

        :param make_quoted_attribute: If True, then the string will be
         quoted, as befits an attribute value.
        """
        # Escape angle brackets, and ampersands that aren't part of
        # entities.
        value = cls.BARE_AMPERSAND_OR_BRACKET.sub(
            cls._substitute_xml_entity, value)

        if make_quoted_attribute:
            value = cls.quoted_attribute_value(value)
        return value

    @classmethod
    def substitute_html(cls, s):
        """Replace certain Unicode characters with named HTML entities.

        This differs from data.encode(encoding, 'xmlcharrefreplace')
        in that the goal is to make the result more readable (to those
        with ASCII displays) rather than to recover from
        errors. There's absolutely nothing wrong with a UTF-8 string
        containg a LATIN SMALL LETTER E WITH ACUTE, but replacing that
        character with "&eacute;" will make it more readable to some
        people.
        """
        return cls.CHARACTER_TO_HTML_ENTITY_RE.sub(
            cls._substitute_html_entity, s)


class UnicodeDammit:
    """A class for detecting the encoding of a *ML document and
    converting it to a Unicode string. If the source encoding is
    windows-1252, can replace MS smart quotes with their HTML or XML
    equivalents."""

    # This dictionary maps commonly seen values for "charset" in HTML
    # meta tags to the corresponding Python codec names. It only covers
    # values that aren't in Python's aliases and can't be determined
    # by the heuristics in find_codec.
    CHARSET_ALIASES = {"macintosh": "mac-roman",
                       "x-sjis": "shift-jis"}

    ENCODINGS_WITH_SMART_QUOTES = [
        "windows-1252",
        "iso-8859-1",
        "iso-8859-2",
        ]

    def __init__(self, markup, override_encodings=[],
                 smart_quotes_to=None, is_html=False):
        self.declared_html_encoding = None
        self.smart_quotes_to = smart_quotes_to
        self.tried_encodings = []
        self.contains_replacement_characters = False

        if markup == '' or isinstance(markup, unicode):
            self.markup = markup
            self.unicode_markup = unicode(markup)
            self.original_encoding = None
            return

        new_markup, document_encoding, sniffed_encoding = \
            self._detectEncoding(markup, is_html)
        self.markup = new_markup

        u = None
        if new_markup != markup:
            # _detectEncoding modified the markup, then converted it to
            # Unicode and then to UTF-8. So convert it from UTF-8.
            u = self._convert_from("utf8")
            self.original_encoding = sniffed_encoding

        if not u:
            for proposed_encoding in (
                override_encodings + [document_encoding, sniffed_encoding]):
                if proposed_encoding is not None:
                    u = self._convert_from(proposed_encoding)
                    if u:
                        break

        # If no luck and we have auto-detection library, try that:
        if not u and chardet and not isinstance(self.markup, unicode):
            u = self._convert_from(chardet.detect(self.markup)['encoding'])

        # As a last resort, try utf-8 and windows-1252:
        if not u:
            for proposed_encoding in ("utf-8", "windows-1252"):
                u = self._convert_from(proposed_encoding)
                if u:
                    break

        # As an absolute last resort, try the encodings again with
        # character replacement.
        if not u:
            for proposed_encoding in (
                override_encodings + [
                    document_encoding, sniffed_encoding, "utf-8", "windows-1252"]):
                if proposed_encoding != "ascii":
                    u = self._convert_from(proposed_encoding, "replace")
                if u is not None:
                    warnings.warn(
                        UnicodeWarning(
                            "Some characters could not be decoded, and were "
                            "replaced with REPLACEMENT CHARACTER."))
                    self.contains_replacement_characters = True
                    break

        # We could at this point force it to ASCII, but that would
        # destroy so much data that I think giving up is better
        self.unicode_markup = u
        if not u:
            self.original_encoding = None

    def _sub_ms_char(self, match):
        """Changes a MS smart quote character to an XML or HTML
        entity, or an ASCII character."""
        orig = match.group(1)
        if self.smart_quotes_to == 'ascii':
            sub = self.MS_CHARS_TO_ASCII.get(orig).encode()
        else:
            sub = self.MS_CHARS.get(orig)
            if type(sub) == tuple:
                if self.smart_quotes_to == 'xml':
                    sub = '&#x'.encode() + sub[1].encode() + ';'.encode()
                else:
                    sub = '&'.encode() + sub[0].encode() + ';'.encode()
            else:
                sub = sub.encode()
        return sub

    def _convert_from(self, proposed, errors="strict"):
        proposed = self.find_codec(proposed)
        if not proposed or (proposed, errors) in self.tried_encodings:
            return None
        self.tried_encodings.append((proposed, errors))
        markup = self.markup

        # Convert smart quotes to HTML if coming from an encoding
        # that might have them.
        if (self.smart_quotes_to is not None
            and proposed.lower() in self.ENCODINGS_WITH_SMART_QUOTES):
            smart_quotes_re = r"([\x80-\x9f])"
            smart_quotes_compiled = re.compile(smart_quotes_re)
            markup = smart_quotes_compiled.sub(self._sub_ms_char, markup)

        try:
            #print "Trying to convert document to %s (errors=%s)" % (
            #    proposed, errors)
            u = self._to_unicode(markup, proposed, errors)
            self.markup = u
            self.original_encoding = proposed
        except Exception:
            #print "That didn't work!"
            #print e
            return None
        #print "Correct encoding: %s" % proposed
        return self.markup

    def _to_unicode(self, data, encoding, errors="strict"):
        '''Given a string and its encoding, decodes the string into Unicode.
        %encoding is a string recognized by encodings.aliases'''

        # strip Byte Order Mark (if present)
        if (len(data) >= 4) and (data[:2] == '\xfe\xff') \
               and (data[2:4] != '\x00\x00'):
            encoding = 'utf-16be'
            data = data[2:]
        elif (len(data) >= 4) and (data[:2] == '\xff\xfe') \
                 and (data[2:4] != '\x00\x00'):
            encoding = 'utf-16le'
            data = data[2:]
        elif data[:3] == '\xef\xbb\xbf':
            encoding = 'utf-8'
            data = data[3:]
        elif data[:4] == '\x00\x00\xfe\xff':
            encoding = 'utf-32be'
            data = data[4:]
        elif data[:4] == '\xff\xfe\x00\x00':
            encoding = 'utf-32le'
            data = data[4:]
        newdata = unicode(data, encoding, errors)
        return newdata

    def _detectEncoding(self, xml_data, is_html=False):
        """Given a document, tries to detect its XML encoding."""
        xml_encoding = sniffed_xml_encoding = None
        try:
            if xml_data[:4] == r'\x4c\x6f\xa7\x94':
                # EBCDIC
                xml_data = self._ebcdic_to_ascii(xml_data)
            elif xml_data[:4] == r'\x00\x3c\x00\x3f':
                # UTF-16BE
                sniffed_xml_encoding = 'utf-16be'
                xml_data = unicode(xml_data, 'utf-16be').encode('utf-8')
            elif (len(xml_data) >= 4) and (xml_data[:2] == r'\xfe\xff') \
                     and (xml_data[2:4] != r'\x00\x00'):
                # UTF-16BE with BOM
                sniffed_xml_encoding = 'utf-16be'
                xml_data = unicode(xml_data[2:], 'utf-16be').encode('utf-8')
            elif xml_data[:4] == r'\x3c\x00\x3f\x00':
                # UTF-16LE
                sniffed_xml_encoding = 'utf-16le'
                xml_data = unicode(xml_data, 'utf-16le').encode('utf-8')
            elif (len(xml_data) >= 4) and (xml_data[:2] == r'\xff\xfe') and \
                     (xml_data[2:4] != r'\x00\x00'):
                # UTF-16LE with BOM
                sniffed_xml_encoding = 'utf-16le'
                xml_data = unicode(xml_data[2:], 'utf-16le').encode('utf-8')
            elif xml_data[:4] == r'\x00\x00\x00\x3c':
                # UTF-32BE
                sniffed_xml_encoding = 'utf-32be'
                xml_data = unicode(xml_data, 'utf-32be').encode('utf-8')
            elif xml_data[:4] == r'\x3c\x00\x00\x00':
                # UTF-32LE
                sniffed_xml_encoding = 'utf-32le'
                xml_data = unicode(xml_data, 'utf-32le').encode('utf-8')
            elif xml_data[:4] == r'\x00\x00\xfe\xff':
                # UTF-32BE with BOM
                sniffed_xml_encoding = 'utf-32be'
                xml_data = unicode(xml_data[4:], 'utf-32be').encode('utf-8')
            elif xml_data[:4] == r'\xff\xfe\x00\x00':
                # UTF-32LE with BOM
                sniffed_xml_encoding = 'utf-32le'
                xml_data = unicode(xml_data[4:], 'utf-32le').encode('utf-8')
            elif xml_data[:3] == r'\xef\xbb\xbf':
                # UTF-8 with BOM
                sniffed_xml_encoding = 'utf-8'
                xml_data = unicode(xml_data[3:], 'utf-8').encode('utf-8')
            else:
                sniffed_xml_encoding = 'ascii'
                pass
        except:
            xml_encoding_match = None
        xml_encoding_match = xml_encoding_re.match(xml_data)
        if not xml_encoding_match and is_html:
            xml_encoding_match = html_meta_re.search(xml_data)
        if xml_encoding_match is not None:
            xml_encoding = xml_encoding_match.groups()[0].decode(
                'ascii').lower()
            if is_html:
                self.declared_html_encoding = xml_encoding
            if sniffed_xml_encoding and \
               (xml_encoding in ('iso-10646-ucs-2', 'ucs-2', 'csunicode',
                                 'iso-10646-ucs-4', 'ucs-4', 'csucs4',
                                 'utf-16', 'utf-32', 'utf_16', 'utf_32',
                                 'utf16', 'u16')):
                xml_encoding = sniffed_xml_encoding
        return xml_data, xml_encoding, sniffed_xml_encoding

    def find_codec(self, charset):
        return self._codec(self.CHARSET_ALIASES.get(charset, charset)) \
               or (charset and self._codec(charset.replace("-", ""))) \
               or (charset and self._codec(charset.replace("-", "_"))) \
               or charset

    def _codec(self, charset):
        if not charset:
            return charset
        codec = None
        try:
            codecs.lookup(charset)
            codec = charset
        except (LookupError, ValueError):
            pass
        return codec

    EBCDIC_TO_ASCII_MAP = None

    def _ebcdic_to_ascii(self, s):
        c = self.__class__
        if not c.EBCDIC_TO_ASCII_MAP:
            emap = (0,1,2,3,156,9,134,127,151,141,142,11,12,13,14,15,
                    16,17,18,19,157,133,8,135,24,25,146,143,28,29,30,31,
                    128,129,130,131,132,10,23,27,136,137,138,139,140,5,6,7,
                    144,145,22,147,148,149,150,4,152,153,154,155,20,21,158,26,
                    32,160,161,162,163,164,165,166,167,168,91,46,60,40,43,33,
                    38,169,170,171,172,173,174,175,176,177,93,36,42,41,59,94,
                    45,47,178,179,180,181,182,183,184,185,124,44,37,95,62,63,
                    186,187,188,189,190,191,192,193,194,96,58,35,64,39,61,34,
                    195,97,98,99,100,101,102,103,104,105,196,197,198,199,200,
                    201,202,106,107,108,109,110,111,112,113,114,203,204,205,
                    206,207,208,209,126,115,116,117,118,119,120,121,122,210,
                    211,212,213,214,215,216,217,218,219,220,221,222,223,224,
                    225,226,227,228,229,230,231,123,65,66,67,68,69,70,71,72,
                    73,232,233,234,235,236,237,125,74,75,76,77,78,79,80,81,
                    82,238,239,240,241,242,243,92,159,83,84,85,86,87,88,89,
                    90,244,245,246,247,248,249,48,49,50,51,52,53,54,55,56,57,
                    250,251,252,253,254,255)
            import string
            c.EBCDIC_TO_ASCII_MAP = string.maketrans(
            ''.join(map(chr, list(range(256)))), ''.join(map(chr, emap)))
        return s.translate(c.EBCDIC_TO_ASCII_MAP)

    # A partial mapping of ISO-Latin-1 to HTML entities/XML numeric entities.
    MS_CHARS = {r'\x80': ('euro', '20AC'),
                r'\x81': ' ',
                r'\x82': ('sbquo', '201A'),
                r'\x83': ('fnof', '192'),
                r'\x84': ('bdquo', '201E'),
                r'\x85': ('hellip', '2026'),
                r'\x86': ('dagger', '2020'),
                r'\x87': ('Dagger', '2021'),
                r'\x88': ('circ', '2C6'),
                r'\x89': ('permil', '2030'),
                r'\x8A': ('Scaron', '160'),
                r'\x8B': ('lsaquo', '2039'),
                r'\x8C': ('OElig', '152'),
                r'\x8D': '?',
                r'\x8E': ('#x17D', '17D'),
                r'\x8F': '?',
                r'\x90': '?',
                r'\x91': ('lsquo', '2018'),
                r'\x92': ('rsquo', '2019'),
                r'\x93': ('ldquo', '201C'),
                r'\x94': ('rdquo', '201D'),
                r'\x95': ('bull', '2022'),
                r'\x96': ('ndash', '2013'),
                r'\x97': ('mdash', '2014'),
                r'\x98': ('tilde', '2DC'),
                r'\x99': ('trade', '2122'),
                r'\x9a': ('scaron', '161'),
                r'\x9b': ('rsaquo', '203A'),
                r'\x9c': ('oelig', '153'),
                r'\x9d': '?',
                r'\x9e': ('#x17E', '17E'),
                r'\x9f': ('Yuml', ''),}

    # A parochial partial mapping of ISO-Latin-1 to ASCII. Contains
    # horrors like stripping diacritical marks to turn á into a, but also
    # contains non-horrors like turning “ into ".
    MS_CHARS_TO_ASCII = {
        r'\x80' : 'EUR',
        r'\x81' : ' ',
        r'\x82' : ',',
        r'\x83' : 'f',
        r'\x84' : ',,',
        r'\x85' : '...',
        r'\x86' : '+',
        r'\x87' : '++',
        r'\x88' : '^',
        r'\x89' : '%',
        r'\x8a' : 'S',
        r'\x8b' : '<',
        r'\x8c' : 'OE',
        r'\x8d' : '?',
        r'\x8e' : 'Z',
        r'\x8f' : '?',
        r'\x90' : '?',
        r'\x91' : "'",
        r'\x92' : "'",
        r'\x93' : '"',
        r'\x94' : '"',
        r'\x95' : '*',
        r'\x96' : '-',
        r'\x97' : '--',
        r'\x98' : '~',
        r'\x99' : '(TM)',
        r'\x9a' : 's',
        r'\x9b' : '>',
        r'\x9c' : 'oe',
        r'\x9d' : '?',
        r'\x9e' : 'z',
        r'\x9f' : 'Y',
        r'\xa0' : ' ',
        r'\xa1' : '!',
        r'\xa2' : 'c',
        r'\xa3' : 'GBP',
        r'\xa4' : '$', #This approximation is especially parochial--this is the
                       #generic currency symbol.
        r'\xa5' : 'YEN',
        r'\xa6' : '|',
        r'\xa7' : 'S',
        r'\xa8' : '..',
        r'\xa9' : '',
        r'\xaa' : '(th)',
        r'\xab' : '<<',
        r'\xac' : '!',
        r'\xad' : ' ',
        r'\xae' : '(R)',
        r'\xaf' : '-',
        r'\xb0' : 'o',
        r'\xb1' : '+-',
        r'\xb2' : '2',
        r'\xb3' : '3',
        r'\xb4' : ("'", 'acute'),
        r'\xb5' : 'u',
        r'\xb6' : 'P',
        r'\xb7' : '*',
        r'\xb8' : ',',
        r'\xb9' : '1',
        r'\xba' : '(th)',
        r'\xbb' : '>>',
        r'\xbc' : '1/4',
        r'\xbd' : '1/2',
        r'\xbe' : '3/4',
        r'\xbf' : '?',
        r'\xc0' : 'A',
        r'\xc1' : 'A',
        r'\xc2' : 'A',
        r'\xc3' : 'A',
        r'\xc4' : 'A',
        r'\xc5' : 'A',
        r'\xc6' : 'AE',
        r'\xc7' : 'C',
        r'\xc8' : 'E',
        r'\xc9' : 'E',
        r'\xca' : 'E',
        r'\xcb' : 'E',
        r'\xcc' : 'I',
        r'\xcd' : 'I',
        r'\xce' : 'I',
        r'\xcf' : 'I',
        r'\xd0' : 'D',
        r'\xd1' : 'N',
        r'\xd2' : 'O',
        r'\xd3' : 'O',
        r'\xd4' : 'O',
        r'\xd5' : 'O',
        r'\xd6' : 'O',
        r'\xd7' : '*',
        r'\xd8' : 'O',
        r'\xd9' : 'U',
        r'\xda' : 'U',
        r'\xdb' : 'U',
        r'\xdc' : 'U',
        r'\xdd' : 'Y',
        r'\xde' : 'b',
        r'\xdf' : 'B',
        r'\xe0' : 'a',
        r'\xe1' : 'a',
        r'\xe2' : 'a',
        r'\xe3' : 'a',
        r'\xe4' : 'a',
        r'\xe5' : 'a',
        r'\xe6' : 'ae',
        r'\xe7' : 'c',
        r'\xe8' : 'e',
        r'\xe9' : 'e',
        r'\xea' : 'e',
        r'\xeb' : 'e',
        r'\xec' : 'i',
        r'\xed' : 'i',
        r'\xee' : 'i',
        r'\xef' : 'i',
        r'\xf0' : 'o',
        r'\xf1' : 'n',
        r'\xf2' : 'o',
        r'\xf3' : 'o',
        r'\xf4' : 'o',
        r'\xf5' : 'o',
        r'\xf6' : 'o',
        r'\xf7' : '/',
        r'\xf8' : 'o',
        r'\xf9' : 'u',
        r'\xfa' : 'u',
        r'\xfb' : 'u',
        r'\xfc' : 'u',
        r'\xfd' : 'y',
        r'\xfe' : 'b',
        r'\xff' : 'y',
        }

    # A map used when removing rogue Windows-1252/ISO-8859-1
    # characters in otherwise UTF-8 documents.
    #
    # Note that \x81, \x8d, \x8f, \x90, and \x9d are undefined in
    # Windows-1252.
    WINDOWS_1252_TO_UTF8 = {
        0x80 : r'\xe2\x82\xac', # €
        0x82 : r'\xe2\x80\x9a', # ‚
        0x83 : r'\xc6\x92',     # ƒ
        0x84 : r'\xe2\x80\x9e', # „
        0x85 : r'\xe2\x80\xa6', # …
        0x86 : r'\xe2\x80\xa0', # †
        0x87 : r'\xe2\x80\xa1', # ‡
        0x88 : r'\xcb\x86',     # ˆ
        0x89 : r'\xe2\x80\xb0', # ‰
        0x8a : r'\xc5\xa0',     # Š
        0x8b : r'\xe2\x80\xb9', # ‹
        0x8c : r'\xc5\x92',     # Œ
        0x8e : r'\xc5\xbd',     # Ž
        0x91 : r'\xe2\x80\x98', # ‘
        0x92 : r'\xe2\x80\x99', # ’
        0x93 : r'\xe2\x80\x9c', # “
        0x94 : r'\xe2\x80\x9d', # ”
        0x95 : r'\xe2\x80\xa2', # •
        0x96 : r'\xe2\x80\x93', # –
        0x97 : r'\xe2\x80\x94', # —
        0x98 : r'\xcb\x9c',     # ˜
        0x99 : r'\xe2\x84\xa2', # ™
        0x9a : r'\xc5\xa1',     # š
        0x9b : r'\xe2\x80\xba', # ›
        0x9c : r'\xc5\x93',     # œ
        0x9e : r'\xc5\xbe',     # ž
        0x9f : r'\xc5\xb8',     # Ÿ
        0xa0 : r'\xc2\xa0',     #  
        0xa1 : r'\xc2\xa1',     # ¡
        0xa2 : r'\xc2\xa2',     # ¢
        0xa3 : r'\xc2\xa3',     # £
        0xa4 : r'\xc2\xa4',     # ¤
        0xa5 : r'\xc2\xa5',     # ¥
        0xa6 : r'\xc2\xa6',     # ¦
        0xa7 : r'\xc2\xa7',     # §
        0xa8 : r'\xc2\xa8',     # ¨
        0xa9 : r'\xc2\xa9',     # ©
        0xaa : r'\xc2\xaa',     # ª
        0xab : r'\xc2\xab',     # «
        0xac : r'\xc2\xac',     # ¬
        0xad : r'\xc2\xad',     # ­
        0xae : r'\xc2\xae',     # ®
        0xaf : r'\xc2\xaf',     # ¯
        0xb0 : r'\xc2\xb0',     # °
        0xb1 : r'\xc2\xb1',     # ±
        0xb2 : r'\xc2\xb2',     # ²
        0xb3 : r'\xc2\xb3',     # ³
        0xb4 : r'\xc2\xb4',     # ´
        0xb5 : r'\xc2\xb5',     # µ
        0xb6 : r'\xc2\xb6',     # ¶
        0xb7 : r'\xc2\xb7',     # ·
        0xb8 : r'\xc2\xb8',     # ¸
        0xb9 : r'\xc2\xb9',     # ¹
        0xba : r'\xc2\xba',     # º
        0xbb : r'\xc2\xbb',     # »
        0xbc : r'\xc2\xbc',     # ¼
        0xbd : r'\xc2\xbd',     # ½
        0xbe : r'\xc2\xbe',     # ¾
        0xbf : r'\xc2\xbf',     # ¿
        0xc0 : r'\xc3\x80',     # À
        0xc1 : r'\xc3\x81',     # Á
        0xc2 : r'\xc3\x82',     # Â
        0xc3 : r'\xc3\x83',     # Ã
        0xc4 : r'\xc3\x84',     # Ä
        0xc5 : r'\xc3\x85',     # Å
        0xc6 : r'\xc3\x86',     # Æ
        0xc7 : r'\xc3\x87',     # Ç
        0xc8 : r'\xc3\x88',     # È
        0xc9 : r'\xc3\x89',     # É
        0xca : r'\xc3\x8a',     # Ê
        0xcb : r'\xc3\x8b',     # Ë
        0xcc : r'\xc3\x8c',     # Ì
        0xcd : r'\xc3\x8d',     # Í
        0xce : r'\xc3\x8e',     # Î
        0xcf : r'\xc3\x8f',     # Ï
        0xd0 : r'\xc3\x90',     # Ð
        0xd1 : r'\xc3\x91',     # Ñ
        0xd2 : r'\xc3\x92',     # Ò
        0xd3 : r'\xc3\x93',     # Ó
        0xd4 : r'\xc3\x94',     # Ô
        0xd5 : r'\xc3\x95',     # Õ
        0xd6 : r'\xc3\x96',     # Ö
        0xd7 : r'\xc3\x97',     # ×
        0xd8 : r'\xc3\x98',     # Ø
        0xd9 : r'\xc3\x99',     # Ù
        0xda : r'\xc3\x9a',     # Ú
        0xdb : r'\xc3\x9b',     # Û
        0xdc : r'\xc3\x9c',     # Ü
        0xdd : r'\xc3\x9d',     # Ý
        0xde : r'\xc3\x9e',     # Þ
        0xdf : r'\xc3\x9f',     # ß
        0xe0 : r'\xc3\xa0',     # à
        0xe1 : r'\xa1',     # á
        0xe2 : r'\xc3\xa2',     # â
        0xe3 : r'\xc3\xa3',     # ã
        0xe4 : r'\xc3\xa4',     # ä
        0xe5 : r'\xc3\xa5',     # å
        0xe6 : r'\xc3\xa6',     # æ
        0xe7 : r'\xc3\xa7',     # ç
        0xe8 : r'\xc3\xa8',     # è
        0xe9 : r'\xc3\xa9',     # é
        0xea : r'\xc3\xaa',     # ê
        0xeb : r'\xc3\xab',     # ë
        0xec : r'\xc3\xac',     # ì
        0xed : r'\xc3\xad',     # í
        0xee : r'\xc3\xae',     # î
        0xef : r'\xc3\xaf',     # ï
        0xf0 : r'\xc3\xb0',     # ð
        0xf1 : r'\xc3\xb1',     # ñ
        0xf2 : r'\xc3\xb2',     # ò
        0xf3 : r'\xc3\xb3',     # ó
        0xf4 : r'\xc3\xb4',     # ô
        0xf5 : r'\xc3\xb5',     # õ
        0xf6 : r'\xc3\xb6',     # ö
        0xf7 : r'\xc3\xb7',     # ÷
        0xf8 : r'\xc3\xb8',     # ø
        0xf9 : r'\xc3\xb9',     # ù
        0xfa : r'\xc3\xba',     # ú
        0xfb : r'\xc3\xbb',     # û
        0xfc : r'\xc3\xbc',     # ü
        0xfd : r'\xc3\xbd',     # ý
        0xfe : r'\xc3\xbe',     # þ
        }

    MULTIBYTE_MARKERS_AND_SIZES = [
        (0xc2, 0xdf, 2), # 2-byte characters start with a byte C2-DF
        (0xe0, 0xef, 3), # 3-byte characters start with E0-EF
        (0xf0, 0xf4, 4), # 4-byte characters start with F0-F4
        ]

    FIRST_MULTIBYTE_MARKER = MULTIBYTE_MARKERS_AND_SIZES[0][0]
    LAST_MULTIBYTE_MARKER = MULTIBYTE_MARKERS_AND_SIZES[-1][1]

    @classmethod
    def detwingle(cls, in_bytes, main_encoding="utf8",
                  embedded_encoding="windows-1252"):
        """Fix characters from one encoding embedded in some other encoding.

        Currently the only situation supported is Windows-1252 (or its
        subset ISO-8859-1), embedded in UTF-8.

        The input must be a bytestring. If you've already converted
        the document to Unicode, you're too late.

        The output is a bytestring in which `embedded_encoding`
        characters have been converted to their `main_encoding`
        equivalents.
        """
        if embedded_encoding.replace('_', '-').lower() not in (
            'windows-1252', 'windows_1252'):
            raise NotImplementedError(
                "Windows-1252 and ISO-8859-1 are the only currently supported "
                "embedded encodings.")

        if main_encoding.lower() not in ('utf8', 'utf-8'):
            raise NotImplementedError(
                "UTF-8 is the only currently supported main encoding.")

        byte_chunks = []

        chunk_start = 0
        pos = 0
        while pos < len(in_bytes):
            byte = in_bytes[pos]
            if not isinstance(byte, int):
                # Python 2.x
                byte = ord(byte)
            if (byte >= cls.FIRST_MULTIBYTE_MARKER
                and byte <= cls.LAST_MULTIBYTE_MARKER):
                # This is the start of a UTF-8 multibyte character. Skip
                # to the end.
                for start, end, size in cls.MULTIBYTE_MARKERS_AND_SIZES:
                    if byte >= start and byte <= end:
                        pos += size
                        break
            elif byte >= 0x80 and byte in cls.WINDOWS_1252_TO_UTF8:
                # We found a Windows-1252 character!
                # Save the string up to this point as a chunk.
                byte_chunks.append(in_bytes[chunk_start:pos])

                # Now translate the Windows-1252 character into UTF-8
                # and add it as another, one-byte chunk.
                byte_chunks.append(cls.WINDOWS_1252_TO_UTF8[byte])
                pos += 1
                chunk_start = pos
            else:
                # Go on to the next character.
                pos += 1
        if chunk_start == 0:
            # The string is unchanged.
            return in_bytes
        else:
            # Store the final chunk.
            byte_chunks.append(in_bytes[chunk_start:])
        return r''.join(byte_chunks)

