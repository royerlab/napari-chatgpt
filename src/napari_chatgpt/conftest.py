import openai
import pytest
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


@pytest.fixture(autouse=True)
def retry_on_openai_rate_limit_error(request) -> None:
    retry_decorator = retry(stop=stop_after_attempt(10),
                            wait=wait_fixed(20),
                            retry=retry_if_exception_type(openai.RateLimitError))

    test_callable = retry_decorator(request.node.obj)
    request.node.obj = test_callable
