import logging
import re
from typing import List, Set, Dict

try: 
    from . import languages
    from .settings import args, config
    from .sub_block import SubBlock, ParsingException
except: 
    from subcleaner import languages
    from subcleaner.settings import args, config
    from subcleaner.sub_block import SubBlock, ParsingException

try: 
    from libs import langdetect as langdetect
except:
    import subcleaner.langdetect as langdetect
from pathlib import Path

try: from ..langdetect import LangDetectException
except: from subcleaner.langdetect import LangDetectException

logger = logging.getLogger(__name__)


class Subtitle:
    blocks: List[SubBlock]
    ad_blocks: Set[SubBlock]
    warning_blocks: Set[SubBlock]
    language: str
    file: Path
    short_path: Path

    def __init__(self, subtitle_file: Path) -> None:
        self.file = subtitle_file
        self.blocks = []
        self.ad_blocks = set()
        self.warning_blocks = set()

        file_content = read_file(self.file)
        self._parse_file_content(file_content)

        for i in range(len(self.blocks)):
            self.blocks[i].current_index = i
        try:
            self.short_path = self.file.relative_to(config.relative_base)
        except ValueError:
            self.short_path = self.file

        if not self:
            raise FileContentException(self.file)

        if args.language:
            self.language = args.language
        else:
            self.determine_language()

        if args.destroy_list:
            self.mark_blocks_for_deletion(args.destroy_list)

    def warn(self, block: SubBlock):
        if block not in self.ad_blocks:
            self.warning_blocks.add(block)

    def ad(self, block: SubBlock):
        try:
            self.warning_blocks.remove(block)
        except KeyError:
            pass
        self.ad_blocks.add(block)
        if "-->" in block.content:
            logger.warning(f"potential malformed subtitle blocks in removed block {block.original_index}.")

    def _parse_file_content(self, file_content: str) -> None:
        file_content = file_content.replace("—>", "-->")
        current_line = 0
        line_lookup: Dict[str, int] = {}
        for line in file_content.split("\n"):
            current_line += 1
            if "-->" in line:
                line_lookup[line] = current_line
        file_content = re.sub(r'\n\s*\n', '\n', file_content)
        file_content = file_content.strip()
        file_content_lines = file_content.split("\n")
        self._breakup_block(file_content_lines, line_lookup)

    def _breakup_block(self, lines: [str], line_lookup: Dict[str, int]) -> None:
        last_break = 0
        start_index = 0
        for i in range(len(lines)):
            line = lines[i]
            if not SubBlock.is_sub_block_header(line) or i == len(lines)-1 or SubBlock.is_sub_block_header(lines[i+1]):
                continue
            start_index = i + 1
            if i == 0:
                last_break = i
                break

            previous_line = lines[i - 1]
            if previous_line[0].isnumeric():
                last_break = i - 1
            else:
                last_break = i
            break
        if last_break > 1:
            e = ParsingException(1, "incorrectly formatted subtitle block")
            e.subtitle_file = self.file
            e.file_line = line_lookup.get(lines[last_break], None)
            if not e.file_line:
                e.file_line = line_lookup.get(lines[last_break + 1], None)
            logger.warning(str(e))

        #logger.warning(lines)
        for i in range(start_index, len(lines)):
            line = lines[i]
            previous_line = lines[i-1]
            if not SubBlock.is_sub_block_header(line) or i == len(lines)-1 or SubBlock.is_sub_block_header(lines[i+1]):
                continue

            if previous_line[0].isnumeric():
                next_break = i - 1
            else:
                next_break = i

            try:
                block = SubBlock("\n".join(lines[last_break:next_break]), len(self.blocks) + 1)
            except ParsingException as e:
                e.subtitle_file = self.file
                e.file_line = line_lookup.get(lines[last_break], None)
                if not e.file_line:
                    e.file_line = line_lookup.get(lines[last_break+1], None)
                logger.warning(e)
                self.blocks[-1].content += "\n\n" + "\n".join(lines[last_break:next_break])
                continue

            if block.content:
                self.blocks.append(block)
            if "-->" in block.content:
                self.warn(block)
                block.hints.append("malformed_block")
            last_break = next_break
        try:
            block = SubBlock("\n".join(lines[last_break:]), len(self.blocks) + 1)
        except ParsingException as e:
            e.subtitle_file = self.file
            e.file_line = line_lookup.get(lines[last_break], None)
            try:
                if not e.file_line:
                    e.file_line = line_lookup.get(lines[last_break + 1], None)
            except:
                pass
            logger.warning(e)
            try: self.blocks[-1].content += "\n\n" + "\n".join(lines[last_break:])
            except: pass
            return
        if block.content:
            self.blocks.append(block)
        if "-->" in block.content:
            self.warn(block)
            block.hints.append("malformed_block")

    def mark_blocks_for_deletion(self, purge_list: List[int]) -> None:
        for index in purge_list:
            if index-1 >= len(self.blocks):
                continue
            self.blocks[index-1].regex_matches = 3

    def language_is_correct(self) -> bool:
        if self.language == "und":
            return True  # unknown language.
        language_code_2 = languages.get_2letter_code(self.language)

        if not language_code_2:
            return True  # unknown language.

        sub_content: str = ""
        for block in self.blocks:
            sub_content += block.content

        if len(sub_content) < 500:
            return True  # not enough content to estimate language.
        try:
            detected_language = langdetect.detect_langs(sub_content)[0]
        except LangDetectException as e:
            logger.warning(f"{self} can't be analyzed by language detector.")
            return True

        return detected_language.lang == language_code_2 and detected_language.prob > 0.8

    def determine_language(self) -> None:
        if config.default_language:
            self.language = config.default_language
            return

        self.language = "und"

        for suffix in self.file.suffixes[max(-3, -len(self.file.suffixes)): -1]:
            parsed_lang = suffix.replace(":", "-").replace("_", "-").split("-")[0][1:]
            if languages.is_language(parsed_lang):
                self.language = parsed_lang
                return

        sub_content: str = ""
        for block in self.blocks:
            sub_content += block.content
        if len(sub_content) < 500:
            return
        try:
            detected_language = langdetect.detect_langs(sub_content)[0]
        except LangDetectException:
            logger.warning(f"{self} can't be analyzed by language detector.")
            return

        if detected_language.prob > 0.9:
            self.language = detected_language.lang

    def to_content(self) -> str:
        content = ""
        for block in self.blocks:
            content += f"{block.current_index}\n" \
                       f"{block}\n" \
                       f"\n"

            if "-->" in block.content:
                logger.warning(f"potential malformed subtitle blocks in block {block.current_index}.")
        return content[:-1]

    def get_warning_indexes(self) -> List[str]:
        l: List[str] = []
        for block in self.warning_blocks:
            l.append(str(block.current_index))
        return l

    def reindex(self):
        index = 1
        for block in self.blocks:
            block.current_index = index
            index += 1
        for block in self.ad_blocks:
            block.current_index = None

    def __str__(self) -> str:
        return str(self.file)

    def __len__(self) -> int:
        return len(self.blocks)

    def __bool__(self) -> bool:
        for block in self.blocks:
            if block.content:
                return True
        return False


class FileContentException(Exception):
    subtitle_file: str

    def __init__(self, subtitle_file):
        self.subtitle_file = subtitle_file

    def __str__(self) -> str:
        return f"File {self.subtitle_file} is empty."

import sys
if int(sys.version[0]) != 3:
    print('Aborted: Python 3.x required')
    sys.exit(1)

def bomType(file):
    """
    returns file encoding string for open() function

    EXAMPLE:
        bom = bomtype(file)
        open(file, encoding=bom, errors='ignore')
    """
    return "latin-1"
    f = open(file, 'rb')
    b = f.read(4)
    f.close()

    if (b[0:3] == b'\xef\xbb\xbf'):
        return "utf8"

    # Python automatically detects endianess if utf-16 bom is present
    # write endianess generally determined by endianess of CPU
    if ((b[0:2] == b'\xfe\xff') or (b[0:2] == b'\xff\xfe')):
        return "utf16"

    if ((b[0:5] == b'\xfe\xff\x00\x00') 
              or (b[0:5] == b'\x00\x00\xff\xfe')):
        return "utf32"

    # If BOM is not provided, then assume its the codepage
    #     used by your operating system
    #return "cp1252"
    return "latin-1"
    # For the United States its: cp1252


def OpenRead(file):
    #bom = bomType(file)
    #return open(file, 'r', encoding=bom, errors='ignore')
    import codecs
    try: 
        return codecs.open(file, 'r', encoding='utf8')
    except:
        try:
            return codecs.open(file, 'r', encoding='latin1')
        except: 
            bom = bomType(file)
            return open(file, 'r', encoding=bom, errors='ignore')


def read_file(file: Path) -> str:
    file_content: str

    """
    try:
        with file.open("r", encoding="utf-8-sig") as opened_file:
            file_content = opened_file.read()
    except UnicodeDecodeError:
        try:
            with file.open("r", encoding="utf-16-le") as opened_file:
                file_content = opened_file.read()
        except UnicodeError:
                with file.open("r", encoding="cp1252") as opened_file:
                    file_content = opened_file.read()
    """
    try:
        opened_file = OpenRead(file)
        file_content = opened_file.read()
        opened_file.close()
    except UnicodeDecodeError:
        with file.open("r", encoding="utf-16-le") as opened_file:
            file_content = opened_file.read()
    return file_content
