from common.controller import get, router
from service.monthly_deal_service import MonthlyDealService


@router('/report/merchant/monthly', tags=['monthly_deal'])
class DailyDeal:

    def __init__(self, monthly_deal: MonthlyDealService) -> None:
        super().__init__()
        self.monthly_deal = monthly_deal

    @get("/deal/{business_id}")
    def monthly_deal(self, business_id: int):
        return self.monthly_deal.get(business_id=business_id)
