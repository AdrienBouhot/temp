import json
import os
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright
from datetime import datetime

# Si tu utilises boto3 pour S3 :
import boto3
# Connexion à DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='eu-west-3')  # adapte la région

# Accès à la table
table = dynamodb.Table('sunweb_access_infos')

def lambda_handler(event, context):
    # Paramètres attendus dans le payload Lambda

    websites = {
        "nl": "https://www.sunweb.nl/wintersport/frankrijk/val-cenis/val-cenis/residence-les-terrasses-de-termignon",
        "be.nl": "https://www.sunweb.be/nl/skivakantie/frankrijk/val-cenis/val-cenis/residence-les-terrasses-de-termignon",
        "be.fr": "https://www.sunweb.be/fr/ski/france/val-cenis/val-cenis/residence-les-terrasses-de-termignon",
        "de": "https://www.sunweb.de/skiurlaub/frankreich/val-cenis/val-cenis/residence-les-terrasses-de-termignon",
        "uk": "https://www.sunweb.co.uk/ski/france/val-cenis/val-cenis/residence-les-terrasses-de-termignon",
        "se": "https://www.sunweb.se/skidresor/frankrike/val-cenis/val-cenis/residence-les-terrasses-de-termignon",
        "dk": "https://www.sunweb.dk/skiferie/frankrig/val-cenis/val-cenis/residence-les-terrasses-de-termignon",
        "fr": "https://www.sunweb.fr/ski/france/val-cenis/val-cenis/residence-les-terrasses-de-termignon"
    }

    access_infos = []

    # Appel fonction principale
    for key, website in websites.items():
        context_item_id, booking_gate_id = collect_context_item_id_and_booking_gate_id(
            website
        )

        print(f"context_item_id: {context_item_id}")
        print(f"booking_gate_id: {booking_gate_id}")

        access_infos.append({
            'website': website, 
            'context_item_id': context_item_id,
            'booking_gate_id': booking_gate_id
            }
        )

        

        if context_item_id is not None and booking_gate_id is not None:
            table.put_item(Item={
                'website': website, 
                'context_item_id': context_item_id,
                'booking_gate_id': booking_gate_id
                }
            )

    return {
        'status': 'success',
        'access_infos': access_infos
    }


def collect_context_item_id_and_booking_gate_id(
    website: str
) -> Tuple[Optional[str], Optional[str]]:
    # --- Même code que ta fonction, sauf :
    # - results_dir DOIT être "/tmp" sur Lambda
    # - upload S3, voir classe plus bas
    context_item_id = None
    booking_gate_id = None

    with sync_playwright() as p:
        browser_options = {
            "headless": True,
            "timeout": 120000
        }

        browser = p.chromium.launch(**browser_options)
        context = browser.new_context()
        page = context.new_page()

        def log_request(request):
            nonlocal context_item_id, booking_gate_id
            if "GetFiltersApi" in request.url:
                parsed_url = urlparse(request.url)
                query_params = parse_qs(parsed_url.query)
                if 'contextitemid' in query_params:
                    context_item_id = query_params['contextitemid'][0]
                if 'bookingGateId' in query_params:
                    booking_gate_id = query_params['bookingGateId'][0]


        page.on("request", log_request)
 
        page.goto(website, timeout=120000)
        page.wait_for_timeout(15000)
        # Essaye de cliquer sur un logement
        try:
            accommodation_links = page.query_selector_all('a[href*="/ski/"]')
            if accommodation_links:
                accommodation_links[0].click()
                page.wait_for_timeout(10000)
        except Exception as e:
            print(f"Erreur lors du clic sur un logement : {e}")

    return context_item_id, booking_gate_id
