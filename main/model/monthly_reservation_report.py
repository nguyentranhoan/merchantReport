import sqlalchemy.engine
from typing import List


class Place(object):
    place_id: int
    booked: int
    used: int
    amount_of_pending: int
    amount_of_canceled: int
    amount_of_rejected: int
    amount_of_accepted: int
    amount_of_completed: int
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
                 amount_of_pending: int,
                 amount_of_canceled: int,
                 amount_of_rejected: int,
                 amount_of_accepted: int,
                 amount_of_completed: int,
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
        self.amount_of_pending = amount_of_pending
        self.amount_of_canceled = amount_of_canceled
        self.amount_of_rejected = amount_of_rejected
        self.amount_of_accepted = amount_of_accepted
        self.amount_of_completed = amount_of_completed
        self.user_booked = user_booked
        self.user_used = user_used
        self.province_name = province_name
        self.deal_title = deal_title
        self.place_name = place_name
        self.business_name = business_name


class MonthlyReservationReport(object):
    reservation_id: int
    places: List[Place]

    def __init__(self, reservation_id: int, places: List[Place]):
        self.deal_id = reservation_id
        self.places = places
