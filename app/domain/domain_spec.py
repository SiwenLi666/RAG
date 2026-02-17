class DomainSpec:
    """
    All genre-specific logic lives here.
    Only this file should change if switching domains.
    """

    DOMAIN_NAME = "recipes"

    PRIMARY_TEXT_FIELDS = ["name", "ingredients"]

    OUTPUT_FIELDS = ["name", "ingredients", "url"]

    @staticmethod
    def render(document: dict) -> dict:
        """
        Controls what fields are returned to user.
        """
        return {
            key: document.get(key)
            for key in DomainSpec.OUTPUT_FIELDS
        }
