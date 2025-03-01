from pathlib import Path
import logging
from typing import List
try: from .subtitle import Subtitle, ParsingException, FileContentException
except: from subcleaner.subtitle import Subtitle, ParsingException, FileContentException
from libs.subcleaner import cleaner, report_generator, languages, regex_lists
from .settings import args, config

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

files_handled: List[str] = []


def main():
    for file in args.subtitles:
        if file.suffix == ".srt":
            clean_file(file)

    for library in args.libraries:
        clean_directory(library)

    if files_handled == 0:
        logger.error(f"no srt files found.")

    if len(files_handled) > 0:
        if args.end_report and len(files_handled) > 1:
            logger.info("end of run report: \n" + report_generator.generate_end_report())

        logger.info(f"subcleaner finished successfully. {len(files_handled)} files cleaned.")
        if args.silent or args.errors_only:
            print(f"subcleaner finished successfully. {len(files_handled)} files cleaned.")
    else:
        logger.error("subcleaner didn't find any files to clean!")
        if args.silent:
            print("subcleaner didn't find any files to clean!")


def clean_file(subtitle_file: Path) -> None:
    if subtitle_file.name in files_handled:
        return
    logger.info("[---------------------------------------------------------------------------------]")
    try:
        short_file = subtitle_file.relative_to(config.relative_base)
    except ValueError:
        short_file = subtitle_file
    try:
        logger.info(f"loading subtitle: {short_file}")
        subtitle = Subtitle(subtitle_file)
    except (UnicodeDecodeError, ParsingException, FileContentException) as e:
        logger.error(f"subcleaner was unable to decode the file. reason:")
        logger.error(e)
        return
    if not subtitle:
        logger.warning("Subtitle file is empty.")
        return
    if config.require_language_profile and not regex_lists.language_has_profile(subtitle.language):
        logger.warning(f"language '{subtitle.language}' have no regex profile associated with it.")
        logger.warning(f"either create a regex profile for it or disable require_language_profile in the config.")
        return

    logger.info(f"now cleaning subtitle: {subtitle.short_path}")

    if not subtitle.language_is_correct():
        logger.warning(f"the language within the file does not match language: '{subtitle.language}'")

    cleaner.unscramble(subtitle)
    cleaner.find_ads(subtitle)
    cleaner.remove_ads(subtitle)
    if config.fix_overlaps:
        cleaner.fix_overlap(subtitle)

    if len(subtitle.blocks) == 0:
        l = list(subtitle.ad_blocks)
        reasons = l[0].hints
        for block in l[1:]:
            for hint in reasons:
                if hint not in block.hints:
                    reasons.remove(hint)

        logger.error("There might be an issue with the regex, "
                     "because everything in the subtitle would have gotten deleted."
                     "Nothing was altered.")
        if reasons:
            logger.error("all removed blocks had common reasons: " + ", ".join(reasons))
        return

    logger.info(f"Done. Cleaning report:\n{report_generator.generate_report(subtitle)}\n")
    files_handled.append(subtitle_file.name)

    if args.dry_run:
        subtitle.to_content()
        logger.warning("dry run: nothing was altered.")
    else:
        with subtitle_file.open("w", encoding="UTF-8") as file:
            file.write(subtitle.to_content())


def clean_directory(directory: Path) -> None:
    for file in directory.iterdir():
        if file.name.startswith("."):
            continue

        if file.is_dir() and not file.is_symlink():
            clean_directory(file)

        if not file.is_file() or file.suffix != ".srt":
            continue

        if not args.language:
            clean_file(file)
            continue

        for suffix in file.suffixes[max(-3, -len(file.suffixes)):-1]:
            parsed_lang = suffix.replace(":", "-").replace("_", "-").split("-")[0][1:]
            if languages.is_language(parsed_lang) and args.language == parsed_lang:
                clean_file(file)
