import logging
import uuid

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

from scaleos.events import models as event_models

logger = logging.getLogger(__name__)


def is_valid_uuid(value, version=4):
    try:
        uuid_obj = uuid.UUID(value, version=version)
    except (ValueError, TypeError):
        return False
    return str(uuid_obj) == value.lower()


def show_single_item(request, context, context_key, model, public_key):
    logger.debug("show a single item on a page")
    if not is_valid_uuid(str(public_key)):
        msg = _("this is not a valid key")
        messages.error(request, msg)
        return redirect("home")

    the_object = get_object_or_404(
        model,
        public_key=public_key,
    )

    if isinstance(the_object, event_models.Concept):
        organizer = getattr(the_object, "organizer", None)
        if organizer and getattr(organizer, "website", None):
            context["website"] = organizer.website

    if isinstance(the_object, event_models.Event):
        concept = getattr(the_object, "concept", None)
        if concept and getattr(concept, "organizer", None):
            organizer = getattr(concept, "organizer", None)
            if organizer:
                context["website"] = organizer.website

    logger.debug("Context in: %s", context_key)
    context[context_key] = the_object

    template_used = the_object.page_template
    logger.debug("Templated used: %s", template_used)
    return render(
        request,
        template_used,
        context,
    )


def show_alternative_resultset(
    request,
    context,
    context_key,
    model,
    alternative_resultset,
):
    logger.debug(
        "showing the alternative resultset with %s results",
        alternative_resultset.count(),
    )
    logger.debug("Context in: %s", context_key)
    context[context_key] = alternative_resultset
    template_used = model.list_template()
    logger.debug("Templated used: %s", template_used)
    return render(
        request,
        template_used,
        context,
    )


def page_or_list_page(request, model, public_key=None, alternative_resultset=None):
    logger.setLevel(logging.DEBUG)
    logger.debug("Public Key %s", public_key)
    logger.debug("alternative resultset %s", alternative_resultset)

    context = {}
    context_key = str(model._meta.model_name)  # noqa: SLF001

    if public_key:
        return show_single_item(request, context, context_key, model, public_key)

    context_key = f"{context_key}_list"

    if alternative_resultset:
        return show_alternative_resultset(
            request,
            context,
            context_key,
            model,
            alternative_resultset,
        )

    if request.user.is_authenticated:
        user = request.user

        if hasattr(user, context_key):
            logger.debug("Context in: %s", context_key)
            the_list = getattr(user, context_key)
            total = the_list.count()
            logger.debug("We have %s items", total)
            if total == 0:
                msg_trans = _("you do not have any")
                msg = f"{msg_trans} {model._meta.verbose_name_plural}".capitalize()  # noqa: SLF001
                logger.info(msg)
                messages.info(request, msg)
            context[context_key] = the_list
            template_used = model.list_template()
            logger.debug("Templated used: %s", template_used)
            return render(
                request,
                template_used,
                context,
            )
        logger.warning("user model has no attribute %s", context_key)

    msg = _("we cannot find what you are looking for")
    messages.error(request, msg)
    return redirect("home")
