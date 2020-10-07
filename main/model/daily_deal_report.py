from typing import List


class Place(object):
    place_id: int
    booked: int
    used: int
    user_booked: int
    user_used: int
    province_name: str
    deal_title: str
    place_name: str
    business_name: str

    def __init__(self,
                 place_id: int,
                 booked: int,
                 used: int,
                 user_booked: int,
                 user_used: int,
                 province_name: str,
                 deal_title: str,
                 place_name: str,
                 business_name: str
                 ) \
            -> None:
        self.place_id = place_id
        self.booked = booked
        self.used = used
        self.user_booked = user_booked
        self.user_used = user_used
        self.province_name = province_name
        self.deal_title = deal_title
        self.place_name = place_name
        self.business_name = business_name


class DailyDealReport(object):
    deal_id: int
    places: List[Place]

    def __init__(self, deal_id: int, places: List[Place]):
        self.deal_id = deal_id
        self.places = places
