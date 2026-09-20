# Compatibility fix for Python 3.14 + Django BaseContext.__copy__
# In Python 3.14, copy(super()) returns an object that disallows attribute assignment.
try:
    from django.template import context

    def _basecontext_copy(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    context.BaseContext.__copy__ = _basecontext_copy
except Exception:
    pass
