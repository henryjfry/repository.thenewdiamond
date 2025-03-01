#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Expected property factory
"""
try: from rebulk import Rebulk  #PATCH
except: from a4kscrapers_wrapper.rebulk import Rebulk  #PATCH

try: from rebulk.remodule import re  #PATCH
except: from a4kscrapers_wrapper.rebulk.remodule import re  #PATCH

try: from rebulk.utils import find_all  #PATCH
except: from a4kscrapers_wrapper.rebulk.utils import find_all  #PATCH


from . import dash, seps


def build_expected_function(context_key):
    """
    Creates a expected property function
    :param context_key:
    :type context_key:
    :param cleanup:
    :type cleanup:
    :return:
    :rtype:
    """

    def expected(input_string, context):
        """
        Expected property functional pattern.
        :param input_string:
        :type input_string:
        :param context:
        :type context:
        :return:
        :rtype:
        """
        ret = []
        for search in context.get(context_key):
            if search.startswith('re:'):
                search = search[3:]
                search = search.replace(' ', '-')
                matches = Rebulk().regex(search, abbreviations=[dash], flags=re.IGNORECASE) \
                    .matches(input_string, context)
                for match in matches:
                    ret.append(match.span)
            else:
                for sep in seps:
                    input_string = input_string.replace(sep, ' ')
                    search = search.replace(sep, ' ')
                for start in find_all(input_string, search, ignore_case=True):
                    end = start + len(search)
                    value = input_string[start:end]
                    ret.append({'start': start, 'end': end, 'value': value})
        return ret

    return expected

