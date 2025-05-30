"""
Module to handle blocking of requests from providers
Set PRE_TERM_BLOCK to True when you want to force providers from making requests using the requests package
"""
import inspect

import requests

from resources.lib.modules.exceptions import PreemptiveCancellation

PRE_TERM_BLOCK = False


def _monkey_check(method):
	def do_method(*args, **kwargs):
		"""
		Wrapper method
		:param args: args
		:param kwargs: kwargs
		:return: func results
		"""
		if (
			any(True for i in inspect.stack() if "providerModules" in i[1])
			or any(True for i in inspect.stack() if "providers" in i[1])
		) and PRE_TERM_BLOCK:
			raise PreemptiveCancellation('Pre-emptive termination has stopped this request')

		return method(*args, **kwargs)

	return do_method


# Monkey patch the common requests calls

requests.get = _monkey_check(requests.get)
requests.post = _monkey_check(requests.post)
requests.head = _monkey_check(requests.head)
requests.delete = _monkey_check(requests.delete)
requests.put = _monkey_check(requests.put)

requests.Session.get = _monkey_check(requests.Session.get)
requests.Session.post = _monkey_check(requests.Session.post)
requests.Session.head = _monkey_check(requests.Session.head)
requests.Session.delete = _monkey_check(requests.Session.delete)
requests.Session.put = _monkey_check(requests.Session.put)
