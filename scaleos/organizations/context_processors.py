import logging

from scaleos.organizations.models import Organization

logger = logging.getLogger(__name__)


def organization_context(request):
    if request is None:
        return {}

    logger.debug("loading organization_context")
    the_organization_id = request.session.get("active_organization_id", None)
    logger.debug("Do we have a logged in company? %s", the_organization_id)
    if the_organization_id:
        try:
            organization = Organization.objects.get(id=the_organization_id)
            return {
                "active_organization": organization,
                "is_organization_owner": organization.is_owner(request.user),
                "is_organization_employee": organization.is_employee(request.user),
            }
        except Organization.DoesNotExist:
            the_organization_id = None
            request.session["active_organization_id"] = None

    logger.debug("returning none")
    return {}
