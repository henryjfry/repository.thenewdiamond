#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
title property
"""

try: from rebulk import Rebulk, Rule, AppendMatch, RemoveMatch, AppendTags  #PATCH
except: from a4kscrapers_wrapper.rebulk import Rebulk, Rule, AppendMatch, RemoveMatch, AppendTags  #PATCH

try: from rebulk.formatters import formatters  #PATCH
except: from a4kscrapers_wrapper.rebulk.formatters import formatters  #PATCH


from .film import FilmTitleRule
from .language import (
    SubtitlePrefixLanguageRule,
    SubtitleSuffixLanguageRule,
    SubtitleExtensionRule,
    NON_SPECIFIC_LANGUAGES
)
from ..common import seps, title_seps
from ..common.comparators import marker_sorted
from ..common.expected import build_expected_function
from ..common.formatters import cleanup, reorder_title
from ..common.pattern import is_disabled
from ..common.validators import seps_surround


def title(config):  # pylint:disable=unused-argument
    """
    Builder for rebulk object.

    :param config: rule configuration
    :type config: dict
    :return: Created Rebulk object
    :rtype: Rebulk
    """
    rebulk = Rebulk(disabled=lambda context: is_disabled(context, 'title'))
    rebulk.rules(TitleFromPosition, PreferTitleWithYear)

    expected_title = build_expected_function('expected_title')

    rebulk.functional(expected_title, name='title', tags=['expected', 'title'],
                      validator=seps_surround,
                      formatter=formatters(cleanup, reorder_title),
                      conflict_solver=lambda match, other: other,
                      disabled=lambda context: not context.get('expected_title'))

    return rebulk


class TitleBaseRule(Rule):
    """
    Add title match in existing matches
    """
    # pylint:disable=unused-argument
    consequence = [AppendMatch, RemoveMatch]

    def __init__(self, match_name, match_tags=None, alternative_match_name=None):
        super().__init__()
        self.match_name = match_name
        self.match_tags = match_tags
        self.alternative_match_name = alternative_match_name

    def hole_filter(self, hole, matches):
        """
        Filter holes for titles.
        :param hole:
        :type hole:
        :param matches:
        :type matches:
        :return:
        :rtype:
        """
        return True

    def filepart_filter(self, filepart, matches):
        """
        Filter filepart for titles.
        :param filepart:
        :type filepart:
        :param matches:
        :type matches:
        :return:
        :rtype:
        """
        return True

    def holes_process(self, holes, matches):
        """
        process holes
        :param holes:
        :type holes:
        :param matches:
        :type matches:
        :return:
        :rtype:
        """
        cropped_holes = []
        group_markers = matches.markers.named('group')
        for group_marker in group_markers:
            path_marker = matches.markers.at_match(group_marker, predicate=lambda m: m.name == 'path', index=0)
            if path_marker and path_marker.span == group_marker.span:
                group_markers.remove(group_marker)

        for hole in holes:
            cropped_holes.extend(hole.crop(group_markers))

        return cropped_holes

    @staticmethod
    def is_ignored(match):
        """
        Ignore matches when scanning for title (hole).

        Full word language and countries won't be ignored if they are uppercase.
        """
        return not (len(match) > 3 and match.raw.isupper()) and match.name in ('language', 'country', 'episode_details')

    def should_keep(self, match, to_keep, matches, filepart, hole, starting):
        """
        Check if this match should be accepted when ending or starting a hole.
        :param match:
        :type match:
        :param to_keep:
        :type to_keep: list[Match]
        :param matches:
        :type matches: Matches
        :param hole: the filepart match
        :type hole: Match
        :param hole: the hole match
        :type hole: Match
        :param starting: true if match is starting the hole
        :type starting: bool
        :return:
        :rtype:
        """
        if match.name in ('language', 'country'):
            # Keep language if exactly matching the hole.
            if len(hole.value) == len(match.raw):
                return True

            # Keep language if other languages exists in the filepart.
            outside_matches = filepart.crop(hole)
            other_languages = []
            for outside in outside_matches:
                other_languages.extend(matches.range(outside.start, outside.end,
                                                     lambda c_match: c_match.name == match.name and
                                                                     c_match not in to_keep and
                                                                     c_match.value not in NON_SPECIFIC_LANGUAGES))

            if not other_languages and (not starting or len(match.raw) <= 3):
                return True

        return False

    def should_remove(self, match, matches, filepart, hole, context):
        """
        Check if this match should be removed after beeing ignored.
        :param match:
        :param matches:
        :param filepart:
        :param hole:
        :return:
        """
        if context.get('type') == 'episode' and match.name == 'episode_details':
            return match.start >= hole.start and match.end <= hole.end
        return True

    def check_titles_in_filepart(self, filepart, matches, context,  # pylint:disable=inconsistent-return-statements
                                 additional_ignored=None):
        """
        Find title in filepart (ignoring language)
        """
        # pylint:disable=too-many-locals,too-many-branches,too-many-statements
        start, end = filepart.span

        holes = matches.holes(start, end + 1, formatter=formatters(cleanup, reorder_title),
                              ignore=self.is_ignored if additional_ignored is None else lambda m: self.is_ignored(
                                  m) or additional_ignored(m),
                              predicate=lambda m: m.value)

        holes = self.holes_process(holes, matches)

        for hole in holes:
            if not hole or (self.hole_filter and not self.hole_filter(hole, matches)):
                continue

            to_remove = []
            to_keep = []

            ignored_matches = matches.range(hole.start, hole.end, self.is_ignored)

            if ignored_matches:
                for ignored_match in reversed(ignored_matches):
                    # pylint:disable=undefined-loop-variable, cell-var-from-loop
                    trailing = matches.chain_before(hole.end, seps, predicate=lambda m: m == ignored_match)
                    if trailing:
                        should_keep = self.should_keep(ignored_match, to_keep, matches, filepart, hole, False)
                        if should_keep:
                            # pylint:disable=unpacking-non-sequence
                            try:
                                append, crop = should_keep
                            except TypeError:
                                append, crop = should_keep, should_keep
                            if append:
                                to_keep.append(ignored_match)
                            if crop:
                                hole.end = ignored_match.start

                for ignored_match in ignored_matches:
                    if ignored_match not in to_keep:
                        starting = matches.chain_after(hole.start, seps,
                                                       predicate=lambda m, im=ignored_match: m == im)
                        if starting:
                            should_keep = self.should_keep(ignored_match, to_keep, matches, filepart, hole, True)
                            if should_keep:
                                # pylint:disable=unpacking-non-sequence
                                try:
                                    append, crop = should_keep
                                except TypeError:
                                    append, crop = should_keep, should_keep
                                if append:
                                    to_keep.append(ignored_match)
                                if crop:
                                    hole.start = ignored_match.end

            for match in ignored_matches:
                if self.should_remove(match, matches, filepart, hole, context):
                    to_remove.append(match)
            for keep_match in to_keep:
                if keep_match in to_remove:
                    to_remove.remove(keep_match)

            if hole and hole.value:
                hole.name = self.match_name
                hole.tags = self.match_tags
                if self.alternative_match_name:
                    # Split and keep values that can be a title
                    titles = hole.split(title_seps, lambda m: m.value)
                    for title_match in list(titles[1:]):
                        previous_title = titles[titles.index(title_match) - 1]
                        separator = matches.input_string[previous_title.end:title_match.start]
                        if len(separator) == 1 and separator == '-' \
                                and previous_title.raw[-1] not in seps \
                                and title_match.raw[0] not in seps:
                            titles[titles.index(title_match) - 1].end = title_match.end
                            titles.remove(title_match)
                        else:
                            title_match.name = self.alternative_match_name

                else:
                    titles = [hole]
                return titles, to_remove

    def _serie_name_filepart(self, matches, fileparts):
        # Try to get show title from subdirectory of a season only directory (Show Name/Season 1/episode_title.avi)
        for index in range(len(fileparts) - 1):
            if index == 0:
                continue
            filepart = fileparts[index]
            filepart_matches = [m for m in matches.range(filepart.start, filepart.end) if not m.private]
            if len(filepart_matches) == 1 and filepart_matches[0].name == 'season' and \
                    (filepart_matches[0].span == filepart.span or
                     filepart_matches[0].parent and filepart_matches[0].parent.span == filepart.span):
                # Filepath match season match exactly
                return fileparts[index + 1]
        return None

    def _serie_name_filepart_match(self, matches, context, serie_name_filepart, to_append, to_remove):
        def serie_name_filepart_ignored(match):
            for tag in match.tags:
                if tag == 'weak' or tag.startswith('weak-'):
                    return True
            return False

        titles = self.check_titles_in_filepart(serie_name_filepart, matches, context, serie_name_filepart_ignored)
        if titles:
            titles, to_remove_c = titles
            if len(titles) == 1:
                to_append.extend(titles)
                to_remove.extend(to_remove_c)
                return titles[0]
        return None

    def _year_fileparts(self, matches, fileparts):
        year_fileparts = []
        for filepart in fileparts:
            year_match = matches.range(filepart.start, filepart.end, lambda match: match.name == 'year', 0)
            if year_match:
                year_fileparts.append(filepart)
        return year_fileparts

    def when(self, matches, context):
        to_append = []
        to_remove = []

        if matches.named(self.match_name, lambda match: 'expected' in match.tags):
            return False

        fileparts = [filepart for filepart in list(marker_sorted(matches.markers.named('path'), matches))
                     if not self.filepart_filter or self.filepart_filter(filepart, matches)]

        serie_name_filepart = self._serie_name_filepart(matches, fileparts)

        serie_name_filepath_match = None
        if serie_name_filepart:
            serie_name_filepath_match = self._serie_name_filepart_match(matches, context, serie_name_filepart,
                                                                        to_append, to_remove)

        # Force inclusion of fileparts containing the year
        year_fileparts = self._year_fileparts(matches, fileparts)

        for filepart in fileparts:
            try:
                year_fileparts.remove(filepart)
            except ValueError:
                pass
            titles = self.check_titles_in_filepart(filepart, matches, context)
            if titles:
                titles, to_remove_c = titles
                if serie_name_filepath_match:
                    for title_match in titles:
                        if title_match.value != serie_name_filepath_match.value:
                            title_match.name = 'episode_title'
                to_append.extend(titles)
                to_remove.extend(to_remove_c)
                break

        # Add title match in all fileparts containing the year.
        for filepart in year_fileparts:
            titles = self.check_titles_in_filepart(filepart, matches, context)
            if titles:
                # pylint:disable=unbalanced-tuple-unpacking
                titles, to_remove_c = titles
                to_append.extend(titles)
                to_remove.extend(to_remove_c)

        if to_append or to_remove:
            return to_append, to_remove
        return False


class TitleFromPosition(TitleBaseRule):
    """
    Add title match in existing matches
    """
    dependency = [FilmTitleRule, SubtitlePrefixLanguageRule, SubtitleSuffixLanguageRule, SubtitleExtensionRule]

    properties = {'title': [None], 'alternative_title': [None]}

    def __init__(self):
        super().__init__('title', ['title'], 'alternative_title')

    def enabled(self, context):
        return not is_disabled(context, 'alternative_title')


class PreferTitleWithYear(Rule):
    """
    Prefer title where filepart contains year.
    """
    dependency = TitleFromPosition
    consequence = [RemoveMatch, AppendTags(['equivalent-ignore'])]

    properties = {'title': [None]}

    def when(self, matches, context):
        with_year_in_group = []
        with_year = []
        titles = matches.named('title')

        for title_match in titles:
            filepart = matches.markers.at_match(title_match, lambda marker: marker.name == 'path', 0)
            if filepart:
                year_match = matches.range(filepart.start, filepart.end, lambda match: match.name == 'year', 0)
                if year_match:
                    group = matches.markers.at_match(year_match, lambda m: m.name == 'group')
                    if group:
                        with_year_in_group.append(title_match)
                    else:
                        with_year.append(title_match)

        to_tag = []
        if with_year_in_group:
            title_values = {title_match.value for title_match in with_year_in_group}
            to_tag.extend(with_year_in_group)
        elif with_year:
            title_values = {title_match.value for title_match in with_year}
            to_tag.extend(with_year)
        else:
            title_values = {title_match.value for title_match in titles}

        to_remove = []
        for title_match in titles:
            if title_match.value not in title_values:
                to_remove.append(title_match)
        if to_remove or to_tag:
            return to_remove, to_tag
        return False

