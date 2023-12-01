from rest_framework import serializers


class CacheSerializer:
    _log_file = "log_cache.txt"
    _msg_log = "****Error in Cache serializer class: "

    def __init__(self, serializer, data,  cache_name, many=False,):
        if issubclass(serializer, serializers.Serializer):
            self._serializer = serializer
        else:
            f = open(self._log_file, "a+")
            f.write(
                self._msg_log + "should be passing serializer instance from serializer class in kwargs ****\n")
            f.close()
            raise serializers.ValidationError({"error": "Can't retrieve your data. Please try again later or contact to technical support"})

        self._data = data
        self._many = many
        self._cache_name = cache_name

    def _get_from_cache(self):
        # get_cached_name = cache.get(self._cache_name)
        #
        # if get_cached_name is None:
        #     get_cached_name = self._serializer(self._data, many=self._many).data
        #     cache.set(self._cache_name, get_cached_name)

        return self._serializer(self._data, many=self._many).data

    def get_from_cache(self):
        return self._get_from_cache()

