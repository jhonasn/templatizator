import gettext
from locale import getdefaultlocale as get_locale

language = get_locale()[0]

translate = gettext.translation('base', 'locales', languages=[language], fallback=True)
_ = translate.gettext
