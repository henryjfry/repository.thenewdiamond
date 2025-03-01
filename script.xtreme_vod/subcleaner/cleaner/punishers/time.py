import datetime
from datetime import timedelta

try: 
	from libs.subcleaner.subtitle import Subtitle
except:
	from subcleaner.subtitle import Subtitle


def punish_quick_first_block(subtitle: Subtitle) -> None:
    block = subtitle.blocks[0]
    if block.start_time < timedelta(seconds=1):
        block.regex_matches += 1
        block.hints.append("quick_start")


def punish_short_duration(subtitle: Subtitle) -> None:
    for block in subtitle.blocks:
        if block.end_time - block.start_time < datetime.timedelta(milliseconds=250):
            block.regex_matches += 1
            block.hints.append("short duration")

        if block.end_time - block.start_time < datetime.timedelta(milliseconds=100):
            block.regex_matches += 1
            block.hints.append("very short duration")
