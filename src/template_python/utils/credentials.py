from base64 import b64decode, b64encode
import random
import string
import zlib
from base64 import urlsafe_b64decode, urlsafe_b64encode
from functools import cached_property

import template_python


class SecureText:
    def __init__(self):
        pass

    @property
    def __seed(self) -> int:
        """Generates a seed value based on the package name, using ASCII values of its characters.

        The seed is a unique integer based on the structure and content of the package name.

        Returns:
            int: The generated seed value.
        """
        letter_collection: str = (
            string.ascii_letters + string.digits + string.punctuation
        )
        lib_name: str = template_python.__name__

        _num_value = [
            (letter_collection.index(letter) + 1) * (idx + 1)
            for idx, letter in enumerate(lib_name)
        ]
        return int(sum(_num_value) ** len(lib_name))

    @cached_property
    def __text_soup(self) -> str:
        """Generates a randomized string from ASCII letters, digits, and punctuation."""
        letter_base = list(string.ascii_letters + string.digits + string.punctuation)
        random.seed(self.__seed)
        random.shuffle(letter_base)
        return "".join(letter_base)

    def obscure(self, text: str) -> str:
        """Encrypts text with rotation based on values from text_soup."""
        values = self.__text_soup

        def rotate_list(text: str, num: int) -> str:
            return text[num:] + text[:num]

        text = urlsafe_b64encode(zlib.compress(text.encode(), 9)).decode()
        letter_collection: str = (
            string.ascii_letters + string.digits + string.punctuation
        )
        result = ""
        for i, letter in enumerate(text):
            mapper = {
                k: v for k, v in zip(letter_collection, rotate_list(text=values, num=i))
            }
            result += mapper[letter]
        return result

    def unobscure(self, obscured: str) -> str:
        """Unobscures text by rotating characters based on an index."""
        values = self.__text_soup

        def rotate_list(text: str, num: int) -> str:
            return text[num:] + text[:num]

        original = ""
        letter_collection: str = (
            string.ascii_letters + string.digits + string.punctuation
        )
        for i, letter in enumerate(obscured):
            mapper = {
                v: k for k, v in zip(letter_collection, rotate_list(text=values, num=i))
            }
            original += mapper[letter]
        return zlib.decompress(urlsafe_b64decode(original.encode())).decode()

    @staticmethod
    def b64encode(text: str) -> str:
        """Encode string using base64"""
        return b64encode(text.encode()).decode()

    @staticmethod
    def b64decode(text: str) -> str:
        """Decode b64 encoded string"""
        return b64decode(text.encode()).decode()


secure: SecureText = SecureText()
