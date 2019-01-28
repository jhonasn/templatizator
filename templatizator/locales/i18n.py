import gettext
from locale import getdefaultlocale as get_locale
from os import environ
from templatizator.domain.helper import OS

language = None
if 'LANGUAGE' in environ:
    language = environ['LANGUAGE']
if not language:
    language = get_locale()[0]

translate = gettext.translation('base', OS.get_path('templatizator/locales'),
                                languages=[language], fallback=True)
_ = translate.gettext
