import logging

import pytest
from django.test import RequestFactory
from django_htmx.middleware import HtmxDetails

from scaleos.shared import views_htmx as shared_htmx

logger = logging.getLogger(__name__)


class TestHtmxUtils:
    def test_do_htmx_get_checks_valid(self, rf: RequestFactory):
        """
        Test that do_htmx_get_checks does not raise
        an error when it's a valid HTMX request.
        """
        request = rf.get("/some-url/", HTTP_HX_REQUEST="true")
        request.htmx = HtmxDetails(request)

        try:
            shared_htmx.do_htmx_get_checks(request)
        except NotImplementedError:
            pytest.fail("do_htmx_get_checks raised an exception for a valid request")

    def test_do_htmx_get_checks_invalid(self, rf: RequestFactory, caplog):
        """
        Test that do_htmx_get_checks raises an error when it's not a HTMX request.
        """
        request = rf.get("/some-url/")
        caplog.set_level(logging.ERROR)
        request.htmx = HtmxDetails(request)
        request.htmx.is_htmx = False

        with pytest.raises(NotImplementedError) as excinfo:
            shared_htmx.do_htmx_get_checks(request)

        assert "this is not a HTMX request" in str(excinfo.value)
        assert "this is not a HTMX request" in caplog.text

    def test_do_htmx_post_checks_valid(self, rf: RequestFactory):
        """
        Test that do_htmx_post_checks does not
        raise an error for a valid HTMX POST request.
        """
        request = rf.post("/some-url/", HTTP_HX_REQUEST="true")
        request.htmx = HtmxDetails(request)
        try:
            shared_htmx.do_htmx_post_checks(request)
        except NotImplementedError:
            pytest.fail("do_htmx_post_checks raised an exception for a valid request")

    def test_do_htmx_post_checks_not_htmx(self, rf: RequestFactory, caplog):
        """
        Test that do_htmx_post_checks raises an
        error for a non-HTMX POST request.
        """
        request = rf.post("/some-url/")
        caplog.set_level(logging.ERROR)
        request.htmx = HtmxDetails(request)
        request.htmx.is_htmx = False

        with pytest.raises(NotImplementedError) as excinfo:
            shared_htmx.do_htmx_post_checks(request)
        assert "this is not a HTMX request" in str(excinfo.value)
        assert "this is not a HTMX request" in caplog.text

    def test_do_htmx_post_checks_not_post(self, rf: RequestFactory, caplog):
        """
        Test that do_htmx_post_checks raises an error for a non-POST HTMX request.
        """
        request = rf.get("/some-url/", HTTP_HX_REQUEST="true")
        request.htmx = HtmxDetails(request)

        caplog.set_level(logging.ERROR)
        with pytest.raises(NotImplementedError) as excinfo:
            shared_htmx.do_htmx_post_checks(request)

        assert "this is not a POST request" in str(excinfo.value)
        assert "this is not a POST request" in caplog.text
