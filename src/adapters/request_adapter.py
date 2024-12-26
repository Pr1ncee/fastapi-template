import logging
from typing import Union

from httpx import Response, AsyncClient

from src.core.exceptions import ClientError, ServerError
from src.enums.http_method_enum import HTTPMethodEnum

logger = logging.getLogger(__name__)


class RequestService:
    @staticmethod
    async def make_request(
        url: str,
        headers: dict = None,
        data: dict = None,
        method: HTTPMethodEnum = HTTPMethodEnum.GET,
        params: dict = None,
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
            f"Sending external HTTP request",
            extra={"method": method, "url": url, "data": data, "params": params}
        )
        async with AsyncClient() as client:
            match method:
                case HTTPMethodEnum.GET:
                    response = await client.get(url=url, headers=headers, params=params)
                case HTTPMethodEnum.POST:
                    response = await client.post(
                        url=url, json=data, headers=headers, params=params
                    )
                case HTTPMethodEnum.PUT:
                    response = await client.put(
                        url=url, json=data, headers=headers, params=params
                    )
                case HTTPMethodEnum.DELETE:
                    response = await client.delete(
                        url=url, headers=headers, params=params
                    )
        if raise_for_status:
            RequestService.raise_for_status(
                status_code=response.status_code, response_text=response.text
            )
        return response

    @staticmethod
    async def make_form_encoded_request(
        url: str,
        headers: dict = None,
        data: dict = None,
        method: Union[HTTPMethodEnum.POST, HTTPMethodEnum.PUT] = HTTPMethodEnum.POST,
        params: dict = None,
        raise_for_status: bool = True,
    ):
        """
        Method for executing POST and PUT requests with form-encoded data.
        Usage scenario:
            A request should be sent with base64 encoding

        :param url: URL to send request to.
        :param headers: Headers to pass within request.
        :param data: JSON payload to pass within request.
        :param method: HTTP method.
        :param params: Query params to pass within a request.
        :param raise_for_status: Flag indicating whether to raise exception in case URI returned any error code.
        :return: Response from URI.
        """
        logger.info(
            f"Sending external HTTP request",
            extra={"method": method, "url": url, "data": data, "params": params}
        )
        async with AsyncClient() as client:
            match method:
                case HTTPMethodEnum.POST:
                    response = await client.post(
                        url=url, data=data, headers=headers, params=params
                    )
                case HTTPMethodEnum.PUT:
                    response = await client.put(
                        url=url, data=data, headers=headers, params=params
                    )
        if raise_for_status:
            RequestService.raise_for_status(
                status_code=response.status_code, response_text=response.text
            )
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
        if 400 <= status_code < 500:
            logger.error(error_msg, extra=extra)
            raise ClientError(
                content={
                    "message": "External service error!",
                    "metadata": response_text,
                }
            )
        elif 500 <= status_code < 600:
            logger.error(error_msg, extra=extra)
            raise ServerError(
                content={
                    "message": "External service error!",
                    "metadata": response_text,
                }
            )
