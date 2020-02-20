import pytest


@pytest.fixture(autouse=True)
def no_requests(request, monkeypatch):
    def _no_requests(*args, **kwargs):
        calling_test = f'{request.module.__name__}.{request.function.__name__}'
        raise AssertionError(
            f'External requests should be mocked. Check "{calling_test}"'
        )
    monkeypatch.setattr('requests.sessions.Session.request', _no_requests)

