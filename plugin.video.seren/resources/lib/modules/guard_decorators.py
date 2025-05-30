from functools import wraps


def guard_against_none(return_type=None, *exclude_arguments):
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			for idx, a in enumerate(args[1:]):
				if idx in exclude_arguments:
					continue
				if a is None:
					return return_type() if return_type is not None else None
			return func(*args, **kwargs)

		return wrapper

	return decorator


def guard_against_none_or_empty(return_type=None, *exclude_arguments):
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			for idx, a in enumerate(args[1:]):
				if idx in exclude_arguments:
					continue
				if a is None or len(a) == 0:
					return return_type() if return_type is not None else None
			return func(*args, **kwargs)

		return wrapper

	return decorator
