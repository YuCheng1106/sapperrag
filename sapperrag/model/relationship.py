"""A package containing the 'Relationship' model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, List, Dict

from .identified import Identified


@dataclass
class Relationship(Identified):
    """A relationship between two entities. This is a generic relationship, and can be used to represent any type of relationship between any two entities."""

    source: str
    """The source entity name."""

    target: str
    """The target entity name."""

    type: Optional[str] = None
    """The type of the relationship (optional)."""

    name: Optional[str] = None
    """The name of the relationship (optional)."""

    weight: Optional[float] = 1.0
    """The edge weight."""

    description: Optional[str] = None
    """A description of the relationship (optional)."""

    description_embedding: Optional[List[float]] = None
    """The semantic embedding for the relationship description (optional)."""

    text_unit_ids: Optional[List[str]] = None
    """List of text unit IDs in which the relationship appears (optional)."""

    document_ids: Optional[List[str]] = None
    """List of document IDs in which the relationship appears (optional)."""

    attributes: Optional[Dict[str, Any]] = None
    """Additional attributes associated with the relationship (optional). To be included in the search prompt"""

    @classmethod
    def from_dict(
        cls,
        d: Dict[str, Any],
        id_key: str = "id",
        short_id_key: str = "short_id",
        type_key: str = "type",
        source_key: str = "source",
        target_key: str = "target",
        description_key: str = "description",
        weight_key: str = "weight",
        text_unit_ids_key: str = "text_unit_ids",
        document_ids_key: str = "document_ids",
        attributes_key: str = "attributes",
    ) -> "Relationship":
        """Create a new relationship from the dict data."""
        return Relationship(
            id=d[id_key],
            short_id=d.get(short_id_key),
            type=d.get(type_key),
            source=d[source_key],
            target=d[target_key],
            description=d.get(description_key),
            weight=d.get(weight_key, 1.0),
            text_unit_ids=d.get(text_unit_ids_key),
            document_ids=d.get(document_ids_key),
            attributes=d.get(attributes_key),
        )
