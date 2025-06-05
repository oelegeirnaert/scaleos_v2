import logging

from scaleos.events import models as event_models
from scaleos.shared.views import page_or_list_page

logger = logging.getLogger(__name__)


def event(request, event_public_key=None):
    return page_or_list_page(
        request,
        event_models.Event,
        event_public_key,
    )

def concept(request, concept_public_key):
    return page_or_list_page(request, event_models.Concept, concept_public_key)
