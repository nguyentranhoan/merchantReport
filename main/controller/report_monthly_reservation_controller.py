from common.controller import get, router
from service.monthly_reservation_service import MonthlyReservationService


@router('/report/merchant/monthly', tags=['monthly_reservation'])
class DailyDeal:

    def __init__(self, monthly_reservation: MonthlyReservationService) -> None:
        super().__init__()
        self.monthly_reservation = monthly_reservation

    @get("/reservation/{business_id}")
    def monthly_reservation(self, business_id: int):
        return self.monthly_reservation.get(business_id=business_id)
