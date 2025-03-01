import re
from typing import List, Tuple

try: 
	from libs.subcleaner import regex_lists
	from libs.subcleaner.sub_block import SubBlock
	from libs.subcleaner.subtitle import Subtitle
except:
	from subcleaner import regex_lists
	from subcleaner.sub_block import SubBlock
	from subcleaner.subtitle import Subtitle


def punish_regex_matches(subtitle: Subtitle) -> None:
    for block in subtitle.blocks:
        _run_regex_on_block(block, regex_lists.get_purge_regex(subtitle.language), 3)
        _run_regex_on_block(block, regex_lists.get_warning_regex(subtitle.language), 1)


def _run_regex_on_block(block: SubBlock, regex_list: List[Tuple[str, str]], punishment: int) -> None:
    clean_content = " ".join(block.content.replace("-\n", "-").split())
    for regex in regex_list:
        try:
            result = re.findall(regex[1], clean_content, flags=re.IGNORECASE | re.UNICODE)
        except re.error as e:
            raise ValueError(f"regex {regex[0]} is miss configured: {e.msg}")
        if result:
            block.regex_matches += punishment * len(result)
            for i in range(0, len(result)):
                block.hints.append(regex[0])
