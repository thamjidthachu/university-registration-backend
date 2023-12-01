from rest_framework import serializers


class CacheModel:
    _log_file = "log_cache.txt"
    _msg_log = "****Error in Cache Model class: "

    def __init__(self, **kwargs):

        if 'function' not in kwargs:
            f = open(self._log_file, "a+")
            f.write(self._msg_log + "should be passing function in kwargs ****\n")
            f.close()
            raise serializers.ValidationError(
                {"error": "Can't retrieve your data. Please try again later or contact to technical support"})
        else:
            self._function = kwargs['function']
            if 'params' in kwargs:
                self._params = kwargs['params']
            else:
                self._params = ()

            if 'kwargs' in kwargs:
                self._kwargs = kwargs['kwargs']
            else:
                self._kwargs = {}

        if 'cache_name' not in kwargs:
            f = open(self._log_file, "a+")
            f.write(
                self._msg_log + "should be passing cache_name in kwargs\n****\n")
            f.close()
            raise serializers.ValidationError(
                {"error": "Can't retrieve your data. Please try again later or contact to technical support"})
        else:
            self._cache_name = kwargs['cache_name']

    def _get_from_cache(self):

        # get_cached_name = cache.get(self._cache_name)
        #
        # if get_cached_name is None:

        return self._function(*self._params, **self._kwargs)

        # cache.set(self._cache_name, get_cached_name)

        # return get_cached_name

    def get_from_cache(self):
        return self._get_from_cache()

    @classmethod
    def get_list_cache(cls):
        return  # cache.keys('*')

    @classmethod
    def list_filter(cls, cache_start):
        return  # list(filter(lambda x: x.startswith(cache_start), cls.get_list_cache()))

    @classmethod
    def remove_cache(cls, keys):
        # if isinstance(keys, list):
        #     for key in keys:
        #         cache.delete(key)
        # else:
        #     cache.delete(keys)
        return
