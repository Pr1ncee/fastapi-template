import logging

from httpx import AsyncClient, Response, codes

from src.adapters.enums.http_method_enum import HTTPMethodEnum
from src.core.exceptions import ClientError, ServerError

logger = logging.getLogger(__name__)


class RequestService:
    @staticmethod
    async def make_request(
        url: str,
        headers: dict | None = None,
        data: dict | None = None,
        method: HTTPMethodEnum = HTTPMethodEnum.GET,
        params: dict | None = None,
        raise_for_status: bool = True,
    ) -> Response:
        """
        Method for executing HTTP requests with specified URI.
        :param url: URL to send request to.
        :param headers: Headers to pass within request.
        :param data: JSON payload to pass within request.
        :param method: HTTP method.
        :param params: Query params to pass within a request.
        :param raise_for_status: Flag indicating whether to raise exception in case URI returned any error code.
        :return: Response from URI.
        """
        logger.info(
            "Sending external HTTP request",
            extra={"method": method, "url": url, "data": data, "params": params},
        )
        async with AsyncClient() as client:
            match method:
                case HTTPMethodEnum.GET:
                    response = await client.get(url=url, headers=headers, params=params)
                case HTTPMethodEnum.POST:
                    response = await client.post(url=url, json=data, headers=headers, params=params)
                case HTTPMethodEnum.PUT:
                    response = await client.put(url=url, json=data, headers=headers, params=params)
                case HTTPMethodEnum.DELETE:
                    response = await client.delete(url=url, headers=headers, params=params)
        if raise_for_status:
            RequestService.raise_for_status(status_code=response.status_code, response_text=response.text)
        return response

    @staticmethod
    def raise_for_status(status_code: int, response_text: str) -> None:
        """
        Utility function to raise errors in case URI returned error code
        :param status_code: status code returned by URI
        :param response_text: response body returned by URI
        :return: None
        """
        error_msg, extra = "The request failed!", {"e": response_text}
        if codes.BAD_REQUEST <= status_code < codes.INTERNAL_SERVER_ERROR:
            logger.error(error_msg, extra=extra)
            raise ClientError(
                content={
                    "message": "External service error!",
                    "metadata": response_text,
                },
            )
        if codes.INTERNAL_SERVER_ERROR <= status_code <= codes.NETWORK_AUTHENTICATION_REQUIRED:
            logger.error(error_msg, extra=extra)
            raise ServerError(
                content={
                    "message": "External service error!",
                    "metadata": response_text,
                },
            )
