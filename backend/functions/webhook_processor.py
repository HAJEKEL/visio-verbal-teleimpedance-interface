# webhook_manager.py

import os
import json
import logging
from urllib.parse import urlparse
from fastapi import HTTPException


class WebhookProcessor:
    """
    A class to manage webhook URLs, including registration, unregistration, and listing.
    """

    WEBHOOKS_FILE = "webhooks/webhook_urls.json"

    def __init__(self):
        self.webhooks_file = self.WEBHOOKS_FILE
        self.webhook_urls = self.load_webhooks()

    def ensure_webhooks_file(self):
        """
        Ensures that the webhooks file exists.
        """
        if not os.path.exists(self.webhooks_file):
            os.makedirs(os.path.dirname(self.webhooks_file), exist_ok=True)
            with open(self.webhooks_file, 'w') as f:
                json.dump([], f)

    def load_webhooks(self):
        """
        Loads the list of webhook URLs from the webhooks file.
        """
        self.ensure_webhooks_file()
        try:
            with open(self.webhooks_file, 'r') as f:
                webhooks = json.load(f)
                logging.info("Webhook URLs loaded successfully.")
                return webhooks
        except json.JSONDecodeError as e:
            logging.error(f"Error reading webhooks file: {e}")
            return []

    def save_webhooks(self):
        """
        Saves the current list of webhook URLs to the webhooks file.
        """
        try:
            with open(self.webhooks_file, 'w') as f:
                json.dump(self.webhook_urls, f)
                logging.info("Webhook URLs saved successfully.")
        except Exception as e:
            logging.error(f"Error saving webhooks: {e}")

    def validate_webhook_url(self, webhook_url):
        """
        Validates the webhook URL.

        Parameters:
            webhook_url (str): The URL to validate.

        Returns:
            bool: True if valid, raises HTTPException if invalid.
        """
        parsed_url = urlparse(webhook_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logging.error(f"Invalid webhook URL: {webhook_url}")
            raise HTTPException(status_code=400, detail="Invalid webhook URL")
        return True

    def register_webhook(self, webhook_url):
        """
        Registers a webhook URL if it is valid and not already registered.

        Parameters:
            webhook_url (str): The URL to register.

        Returns:
            str: Confirmation message about the registration status.
        """
        self.validate_webhook_url(webhook_url)
        if webhook_url not in self.webhook_urls:
            self.webhook_urls.append(webhook_url)
            self.save_webhooks()
            logging.info(f"Webhook registered: {webhook_url}")
            return f"Webhook registered successfully: {webhook_url}"
        else:
            logging.info(f"Webhook already registered: {webhook_url}")
            return f"Webhook already registered: {webhook_url}"

    def unregister_webhook(self, webhook_url):
        """
        Unregisters a webhook URL if it is currently registered.

        Parameters:
            webhook_url (str): The URL to unregister.

        Returns:
            str: Confirmation message about the unregistration status.
        """
        self.validate_webhook_url(webhook_url)
        if webhook_url in self.webhook_urls:
            self.webhook_urls.remove(webhook_url)
            self.save_webhooks()
            logging.info(f"Webhook unregistered: {webhook_url}")
            return f"Webhook unregistered successfully: {webhook_url}"
        else:
            logging.error(f"Webhook URL not found: {webhook_url}")
            raise HTTPException(status_code=404, detail="Webhook URL not found")

    def list_webhooks(self):
        """
        Lists all currently registered webhook URLs.

        Returns:
            list: A list containing the registered webhook URLs.
        """
        logging.info("Listing registered webhook URLs.")
        return self.webhook_urls
