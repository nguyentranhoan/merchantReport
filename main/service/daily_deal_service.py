from injector import inject, singleton
from common.exception import NotFoundException
from common.utils import get_current_time
from component.database import MasterDatabase
from model.daily_deal_report import DailyDealReport, Place


@inject
@singleton
class DailyDealService:

    def __init__(self, master_database: MasterDatabase):
        super().__init__()
        self.master_database = master_database

    def insert(self, business_id, time_from, time_end, created_at):
        with self.master_database.session() as db:
            # DELETE PREVIOUS DATA
            db.execute(
                f"""DELETE FROM 
                    fact_merchant_program_daily_report_for_deal
                WHERE 
                    fact_merchant_program_daily_report_for_deal.business_id = {business_id}
                    AND fact_merchant_program_daily_report_for_deal.created_at = {created_at}""")
            # db.commit()
            books = db.execute(
                f"""SELECT 
                    dim_3_booked_deal.business_id, 
                    dim_3_booked_deal.place_id, 
                    dim_3_booked_deal.deal_id, 
                    COUNT( dim_3_booked_deal.id ) as booked, 
                    COUNT(DISTINCT dim_3_booked_deal.user_id) as user_booked,
                    SUM (
                            CASE
                            WHEN dim_3_booked_deal.status = 'completed' THEN
                            1
                            ELSE
                            0
                            END
                            ) AS "used" 
                FROM 
                    dim_3_booked_deal 
                WHERE 
                    dim_3_booked_deal.created_at between {time_from * 1000} AND {time_end * 1000}
                    AND dim_3_booked_deal.business_id = {business_id}  
                GROUP BY
                    dim_3_booked_deal.deal_id, 
                    dim_3_booked_deal.place_id, 
                    dim_3_booked_deal.business_id""").fetchall()

            uses = db.execute(
                f"""WITH u AS (SELECT 
                    dim_3_booked_deal.user_id, 
                    dim_3_booked_deal.status, 
                    dim_3_booked_deal.business_id, 
                    dim_3_booked_deal.place_id, 
                    dim_3_booked_deal.deal_id
                FROM 
                    dim_3_booked_deal
                WHERE 
                    dim_3_booked_deal.created_at BETWEEN {time_from * 1000} AND {time_end * 1000} 
                    AND dim_3_booked_deal.business_id = {business_id} 
                GROUP BY dim_3_booked_deal.business_id, 
                    dim_3_booked_deal.place_id, 
                    dim_3_booked_deal.deal_id, 
                    dim_3_booked_deal.user_id, 
                    dim_3_booked_deal.status)
        
                SELECT 
                    business_id, 
                    place_id, 
                    deal_id,
                    SUM( CASE 
                        WHEN 
                            status = 'completed'
                            THEN 1
                            ELSE 
                            0 
                            END ) as "user_used"
                FROM u
                GROUP BY business_id, 
                    place_id, 
                    deal_id;""").fetchall()

            provinces = db.execute(f"""
                        SELECT  
                            dim_2_province_place.id,
                            dim_2_province_place.province_id,
                            dim_province.name
                        FROM 
                            dim_2_province_place JOIN dim_province ON dim_2_province_place.province_id = dim_province.id
                        GROUP BY 
                            dim_2_province_place.id,
                            dim_2_province_place.province_id,
                            dim_province.name""").fetchall()

            # execute
            for book in books:
                for use in uses:
                    for province in provinces:
                        if book.business_id == use.business_id and book.place_id == use.place_id and book.deal_id == use.deal_id and book.place_id == province.id:
                            db.execute(
                                f"""INSERT INTO 
                                        fact_merchant_program_daily_report_for_deal(
                                        business_id, 
                                        place_id,
                                        province_id, 
                                        deal_id, 
                                        booked, 
                                        used, 
                                        user_booked, 
                                        user_used, 
                                        created_at) 
                                VALUES(
                                        {book.business_id}, 
                                        {book.place_id},
                                        {province.province_id}, 
                                        {book.deal_id}, 
                                        {book.booked}, 
                                        {book.used}, 
                                        {book.user_booked}, 
                                        {use.user_used}, 
                                        {created_at})""")
                            db.commit()

    def get(self, business_id: int):
        current_date, set_date_from, set_date_end, created_at, time_from, time_end, month_from, month_end = get_current_time()
        self.insert(business_id, time_from, time_end, created_at)
        with self.master_database.session() as db:
            list_place = []
            list_daily_deal = []
            tmp = db.execute(f""" SELECT {1} 
                        FROM 
                            dim_deal 
                            RIGHT JOIN fact_merchant_program_daily_report_for_deal
                            ON dim_deal.id = fact_merchant_program_daily_report_for_deal.deal_id   
                        WHERE 
                            dim_deal.expire_at < {created_at}
                            AND fact_merchant_program_daily_report_for_deal.business_id = {business_id}""").fetchall()
            is_deal_valid = True
            for deal in tmp:
                if deal is not None:
                    is_deal_valid = False
            if is_deal_valid is False:
                raise NotFoundException(message='All deals have expired')
            else:
                deals = db.execute(
                    f""" WITH tmp AS (
                    SELECT 
                        fact_merchant_program_daily_report_for_deal.*, 
                        dim_business.name as business_name, 
                        dim_2_province_place.name as place_name,
                        dim_province.name as province_name,
                        dim_deal.title as deal_title
                    FROM 
                        fact_merchant_program_daily_report_for_deal 
                        JOIN dim_business ON fact_merchant_program_daily_report_for_deal.business_id = dim_business.id
                        JOIN dim_2_province_place ON fact_merchant_program_daily_report_for_deal.place_id = dim_2_province_place.id
                        JOIN dim_province ON fact_merchant_program_daily_report_for_deal.province_id = dim_province.id
                        JOIN dim_deal ON fact_merchant_program_daily_report_for_deal.deal_id = dim_deal.id
                    WHERE 
                        fact_merchant_program_daily_report_for_deal.business_id = {business_id}
                        AND fact_merchant_program_daily_report_for_deal.created_at = {created_at})
            
                    SELECT * FROM tmp""").fetchall()

                for deal in deals:
                    places = db.execute(
                        f"""
                    SELECT 
                        fact_merchant_program_daily_report_for_deal.place_id,
                        fact_merchant_program_daily_report_for_deal.province_id,
                        fact_merchant_program_daily_report_for_deal.booked,
                        fact_merchant_program_daily_report_for_deal.used,
                        fact_merchant_program_daily_report_for_deal.user_booked,
                        fact_merchant_program_daily_report_for_deal.user_used,
                        fact_merchant_program_daily_report_for_deal.created_at, 
                        dim_business.name as business_name, 
                        dim_2_province_place.name as place_name,
                        dim_province.name as province_name,
                        dim_deal.title as deal_title
                    FROM 
                        fact_merchant_program_daily_report_for_deal 
                        JOIN dim_business ON fact_merchant_program_daily_report_for_deal.business_id = dim_business.id
                        JOIN dim_2_province_place ON fact_merchant_program_daily_report_for_deal.place_id = dim_2_province_place.id
                        JOIN dim_province ON fact_merchant_program_daily_report_for_deal.province_id = dim_province.id
                        JOIN dim_deal ON fact_merchant_program_daily_report_for_deal.deal_id = dim_deal.id
                    WHERE 
                        fact_merchant_program_daily_report_for_deal.deal_id = {deal.deal_id}
                    ORDER BY 
                        fact_merchant_program_daily_report_for_deal.business_id,
                        fact_merchant_program_daily_report_for_deal.place_id,
                        fact_merchant_program_daily_report_for_deal.deal_id""").fetchall()
                    for place in places:
                        if place.place_id == deal.place_id:
                            list_place.append(Place(place_id=place.place_id,
                                                    booked=place.booked,
                                                    used=place.used,
                                                    user_booked=place.user_booked,
                                                    user_used=place.user_used,
                                                    province_name=place.province_name,
                                                    deal_title=place.deal_title,
                                                    place_name=place.place_name,
                                                    business_name=place.business_name))
                    list_daily_deal.append(DailyDealReport(deal_id=deal.deal_id, places=list_place))
            return list_daily_deal
