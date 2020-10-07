from common.controller import get, router
from service.daily_deal_service import DailyDealService


@router('/report/merchant/daily', tags=['daily_deal'])
class DailyDeal:

    def __init__(self, daily_deal: DailyDealService) -> None:
        super().__init__()
        self.daily_deal = daily_deal

    @get("/deal/{business_id}")
    def daily_deal(self, business_id: int):
        return self.daily_deal.get(business_id=business_id)

