from app.domain.base import DomainAdapter
from app.storage.models import Document


class StructuredTextAdapter(DomainAdapter):

    def normalize(self, raw_record: dict) -> Document:

        doc_id = raw_record.get("_id", {}).get("$oid")

        name = raw_record.get("name") or raw_record.get("title", "")

        ingredients = raw_record.get("ingredients", "")
        description = raw_record.get("description", "")

        full_text = f"{name}\n{ingredients}\n{description}"

        metadata = {
            "name": name
        }

        return Document(
            id=doc_id,
            text=full_text,
            metadata=metadata
        )
