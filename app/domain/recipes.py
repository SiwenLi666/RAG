from typing import Any, Dict
from app.domain.base import DomainAdapter
from app.storage.models import Document


class RecipeDomainAdapter(DomainAdapter):
    """
    Domain adapter for recipe dataset.
    All cookbook-specific logic lives here.
    """

    def extract_id(self, raw: Dict[str, Any]) -> str:
        """
        Extract Mongo-style ID safely.
        """
        raw_id = raw.get("_id")

        if isinstance(raw_id, dict) and "$oid" in raw_id:
            return raw_id["$oid"]

        if raw_id:
            return str(raw_id)

        # Fallback (should not happen normally)
        return str(hash(str(raw)))

    def build_text(self, raw: Dict[str, Any]) -> str:
        """
        Build the searchable text for retrieval.
        We combine relevant fields into one string.
        """

        parts = []

        if raw.get("name"):
            parts.append(str(raw["name"]))

        if raw.get("ingredients"):
            parts.append(str(raw["ingredients"]))

        if raw.get("description"):
            parts.append(str(raw["description"]))

        return "\n".join(parts)

    def build_metadata(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store structured metadata for rendering.
        We keep raw fields but explicitly select relevant ones.
        """

        return {
            "name": raw.get("name"),
            "ingredients": raw.get("ingredients"),
            "url": raw.get("url"),
            "image": raw.get("image"),
            "cookTime": raw.get("cookTime"),
            "prepTime": raw.get("prepTime"),
            "recipeYield": raw.get("recipeYield"),
            "source": raw.get("source"),
            "datePublished": raw.get("datePublished"),
        }

    def render(self, document: Document) -> Dict[str, Any]:
        """
        Control how recipe is returned in API response.
        """

        metadata = document.metadata

        return {
            "id": document.id,
            "name": metadata.get("name"),
            "ingredients": metadata.get("ingredients"),
            "url": metadata.get("url"),
            "cookTime": metadata.get("cookTime"),
            "prepTime": metadata.get("prepTime"),
            "recipeYield": metadata.get("recipeYield"),
            "source": metadata.get("source"),
        }
