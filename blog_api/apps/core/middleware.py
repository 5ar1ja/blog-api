from django.utils import translation
from django.conf import settings
import pytz
from django.utils import timezone

class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = None

        # 1. User profile language
        if request.user.is_authenticated and hasattr(request.user, 'language') and request.user.language:
            language = request.user.language
        
        # 2. URL query parameter
        if not language:
            lang_param = request.GET.get('lang')
            if lang_param and any(lang_param == code for code, _ in settings.LANGUAGES):
                language = lang_param
        
        # 3. Accept-Language HTTP header
        if not language:
            accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE')
            if accept_lang:
                # Naive parsing, taking the first valid language
                langs = [lang.split(';')[0].split('-')[0].strip() for lang in accept_lang.split(',')]
                for lang in langs:
                    if any(lang == code for code, _ in settings.LANGUAGES):
                        language = lang
                        break

        # 4. Default language
        if not language:
            language = settings.LANGUAGE_CODE

        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
        
        # Activate User Timezone
        if request.user.is_authenticated and hasattr(request.user, 'timezone') and request.user.timezone:
            try:
                timezone.activate(pytz.timezone(request.user.timezone))
            except pytz.UnknownTimeZoneError:
                pass
                
        response = self.get_response(request)
        
        translation.deactivate()
        timezone.deactivate()
        
        return response
