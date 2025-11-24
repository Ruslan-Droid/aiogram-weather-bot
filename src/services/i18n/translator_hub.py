from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub


class TranslatorHubFactory:
    DIR_PATH = "locales"

    def __init__(self, config):
        self.config = config

    def create(self) -> TranslatorHub:
        return TranslatorHub(
            {
                "ru": ("ru", "en"),
                "en": ("en", "ru")
            },
            [
                self._create_ru_translator(),
                self._create_en_translator(),
            ],
            root_locale=self.config.i18n.default_locale,
        )

    def _create_ru_translator(self) -> FluentTranslator:
        return FluentTranslator(
            locale="ru",
            translator=FluentBundle.from_files(
                locale="ru-RU",
                filenames=[f"{self.DIR_PATH}/ru/txt.ftl"],
                use_isolating=False,
            ),
        )

    def _create_en_translator(self) -> FluentTranslator:
        return FluentTranslator(
            locale="en",
            translator=FluentBundle.from_files(
                locale="en-US",
                filenames=[f"{self.DIR_PATH}/en/txt.ftl"],
                use_isolating=False,
            ),
        )
