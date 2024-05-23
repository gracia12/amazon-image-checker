from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional

import airtable.config
from airtable.ab_test_record import ABTestRecord

SQLQuery = str
ASIN = str


@dataclass
class ImageVariation:
    variant: str
    link: str
    height: int
    width: int

    # implement hash to allow for set operations
    def __hash__(self):
        # convert dataclass to string
        self_str = str(asdict(self))
        return hash(self_str)


@dataclass
class ProductRead:
    asin: ASIN
    read_time: datetime
    image_variations: List[ImageVariation]
    listing_price: Optional[float]
    merchant: str
    is_active: Optional[bool]


@dataclass
class CredentialsSPApi:
    lwa_app_id: str
    lwa_client_secret: str
    sp_api_access_key: str
    sp_api_refresh_token: str
    sp_api_secret_key: str
    sp_api_role_arn: str


@dataclass
class ABTestRun:
    test_id: int
    run_time: datetime
    variation: str
    merchant: str
    run_id: int = None
    feed_id: int = None

    @staticmethod
    def from_record(ab_test_record: ABTestRecord):
        return ABTestRun(
            test_id=ab_test_record.fields[airtable.config.TEST_ID_FIELD], run_time=datetime.utcnow(),
            variation=ab_test_record.current_variation(),
            merchant=ab_test_record.fields[airtable.config.MERCHANT_FIELD])


@dataclass
class ProductReadDiff(ProductRead):
    def __init__(self, current: ProductRead, last: ProductRead | None = None):
        if last:
            assert current.asin == last.asin and current.read_time > last.read_time
        self.asin = current.asin
        self.read_time = current.read_time
        self.merchant = current.merchant
        self.image_variations = ProductReadDiff._calculate_variants_with_diff(
            current, last) if last else current.image_variations
        if last:
            if last.listing_price and current.listing_price and current.listing_price != last.listing_price:
                self.listing_price = current.listing_price
            else:
                self.listing_price = None
            if last.is_active is not None and current.is_active is not None and current.is_active != last.is_active:
                self.is_active = current.is_active
            else:
                self.is_active = None
        else:
            self.listing_price = current.listing_price
            self.is_active = current.is_active

    @staticmethod
    def _calculate_variants_with_diff(current: ProductRead, last: ProductRead) -> List[ImageVariation]:
        return [variant for variant in current.image_variations if variant not in last.image_variations]

    def has_diff(self) -> bool:
        return bool(self.image_variations) or bool(self.listing_price) or bool(self.is_active)
