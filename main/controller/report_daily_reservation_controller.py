from common.controller import get, router
from service.daily_reservation_service import DailyReservationService


@router('/report/merchant/daily', tags=['daily_reservation'])
class DailyDeal:

    def __init__(self, daily_reservation: DailyReservationService) -> None:
        super().__init__()
        self.daily_reservation = daily_reservation

    @get("/reservation/{business_id}")
    def daily_reservation(self, business_id: int):
        return self.daily_reservation.get(business_id=business_id)
