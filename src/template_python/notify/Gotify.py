import requests

from ..utils import log

log.debug("Sending No")


def notify(
    url: str, key: str, title: str, message: str = "", priority: int = 2
) -> None:
    log.debug(f"Sending message {title} to Gotify with priority:{priority}")
    resp = requests.post(
        f"{url}/message?token={key}",
        json={"message": message, "priority": priority, "title": title},
    )
    log.info(f"[GOTIFY]Response: {resp}")
