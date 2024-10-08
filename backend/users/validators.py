from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.regex_helper import _lazy_re_compile


class UsernameValidator(UnicodeUsernameValidator):
    """Проверка имени пользователя."""

    second_regex = r'[\w.@+-]+'

    def __init__(
            self, regex=None, second_regex=None, message=None, code=None,
            inverse_match=None, flags=None
    ):
        super().__init__(regex, message, code, inverse_match, flags)
        if second_regex is not None:
            self.second_regex = second_regex
        self.second_regex = _lazy_re_compile(self.second_regex)
