from datetime import timedelta

try: 
	from libs.subcleaner.sub_block import SubBlock
	from libs.subcleaner.subtitle import Subtitle
except:
	from subcleaner.sub_block import SubBlock
	from subcleaner.subtitle import Subtitle


def detect_wedged(subtitle: Subtitle) -> None:
    if len(subtitle.blocks) < 3:
        return
    for index in range(0, len(subtitle.blocks)):
        block: SubBlock = subtitle.blocks[index]

        if index == 0:
            post_block: SubBlock = subtitle.blocks[index + 1]
            if post_block.regex_matches >= 3:
                if (post_block.start_time - block.end_time) < timedelta(seconds=1):
                    if block in subtitle.warning_blocks:
                        subtitle.ad(block)
                    else:
                        subtitle.warn(block)
                else:
                    subtitle.warn(block)
                block.hints.append("wedged_block")
            continue

        if index == len(subtitle.blocks) - 1:
            pre_block: SubBlock = subtitle.blocks[index - 1]
            if pre_block.regex_matches < 3:
                continue
            block.hints.append("wedged_block")
            if (block.start_time - pre_block.end_time) > timedelta(seconds=1):
                subtitle.warn(block)
                continue

            if block in subtitle.warning_blocks:
                subtitle.ad(block)
            else:
                subtitle.warn(block)
            continue

        pre_block: SubBlock = subtitle.blocks[index - 1]
        post_block: SubBlock = subtitle.blocks[index + 1]

        if pre_block.regex_matches >= 3 and post_block.regex_matches >= 3:
            if (post_block.start_time - block.end_time) < timedelta(seconds=1) and \
                    (block.start_time - pre_block.end_time) < timedelta(seconds=1):
                subtitle.ad(block)
                block.hints.append("wedged_block")
                continue
            if block.regex_matches == 2:
                subtitle.ad(block)
                block.hints.append("wedged_block")
                continue
            else:
                subtitle.warn(block)
                block.hints.append("wedged_block")
                continue
