from injector import inject, singleton

from common.utils import get_current_time
from component.database import MasterDatabase
from model.daily_reservation_report import DailyReservationReport, Place


@inject
@singleton
class DailyReservationService:

    def __init__(self, master_database: MasterDatabase):
        super().__init__()
        self.master_database = master_database

    def insert(self, business_id, time_from, time_end, created_at):
        with self.master_database.session() as db:
            # DELETE PREVIOUS DATA
            db.execute(
                f"""DELETE FROM 
                    fact_merchant_program_daily_report_for_reservation
                WHERE 
                    fact_merchant_program_daily_report_for_reservation.business_id = {business_id}
                    AND fact_merchant_program_daily_report_for_reservation.created_at = {created_at}""")
            # db.commit()
            books = db.execute(
                f"""SELECT 
                        dim_3_booked_reservation.business_id, 
                        dim_3_booked_reservation.place_id,
                        dim_3_booked_reservation.deal_reservation_id,
                        SUM (
                              CASE
                              WHEN dim_3_booked_reservation.reservation_code is not null THEN
                             1
                              ELSE
                             0
                              END
                           ) AS "booked",
                        SUM (
                              CASE
                              WHEN dim_3_booked_reservation.reservation_code is not null AND dim_3_booked_reservation.status = 'completed'  THEN
                             1
                              ELSE
                             0
                              END
                           ) AS "used",
                        SUM (
                              CASE
                              WHEN dim_3_booked_reservation.status = 'pending' THEN
                             1
                              ELSE
                             0
                              END
                           ) AS "amount_of_pending",
                        SUM (
                              CASE
                              WHEN dim_3_booked_reservation.status = 'canceled' THEN
                             1
                              ELSE
                             0
                              END
                           ) AS "amount_of_canceled",
                        SUM (
                              CASE
                              WHEN dim_3_booked_reservation.status = 'rejected' THEN
                             1
                              ELSE
                             0
                              END
                           ) AS "amount_of_rejected",
                        SUM (
                              CASE
                              WHEN dim_3_booked_reservation.status = 'accepted' THEN
                             1
                              ELSE
                             0
                              END
                           ) AS "amount_of_accepted",
                        SUM (
                              CASE
                              WHEN dim_3_booked_reservation.status = 'completed' THEN
                             1
                              ELSE
                             0
                              END
                           ) AS "amount_of_completed",
                        COUNT (DISTINCT dim_3_booked_reservation.user_id) AS user_booked
                        FROM dim_3_booked_reservation
                        WHERE dim_3_booked_reservation.created_at BETWEEN {time_from} AND {time_end} 
                        AND dim_3_booked_reservation.business_id = {business_id}
                        GROUP BY
                        dim_3_booked_reservation.business_id,
                        dim_3_booked_reservation.place_id,
                        dim_3_booked_reservation.deal_reservation_id;""").fetchall()

            uses = db.execute(
                f"""WITH u AS (SELECT 
                                dim_3_booked_reservation.user_id, 
                                dim_3_booked_reservation.status, 
                                dim_3_booked_reservation.business_id, 
                                dim_3_booked_reservation.place_id, 
                                dim_3_booked_reservation.deal_reservation_id
                            FROM dim_3_booked_reservation
                            WHERE dim_3_booked_reservation.created_at BETWEEN {time_from} AND {time_end} 
                                AND dim_3_booked_reservation.business_id = {business_id} 
                            GROUP BY dim_3_booked_reservation.business_id, 
                                dim_3_booked_reservation.place_id, 
                                dim_3_booked_reservation.deal_reservation_id, 
                                dim_3_booked_reservation.user_id, 
                                dim_3_booked_reservation.status)
        
                            SELECT 
                                business_id, 
                                place_id, 
                                deal_reservation_id,
                                sum(case when status = 'completed'
                                    then 1
                                    else 
                                    0 end) as "user_used"
                            FROM u
                            GROUP BY business_id, 
                                place_id, 
                                deal_reservation_id;""").fetchall()

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
                        if book.business_id == use.business_id and book.place_id == use.place_id and book.deal_reservation_id == use.deal_reservation_id and book.place_id == province.id:
                            db.execute(
                                f"""INSERT INTO
                                fact_merchant_program_daily_report_for_reservation( 
                                    business_id, 
                                    place_id, 
                                    deal_reservation_id,
                                    province_id, 
                                    booked, 
                                    used, 
                                    amount_of_pending, 
                                    amount_of_canceled, 
                                    amount_of_rejected, 
                                    amount_of_accepted, 
                                    amount_of_completed, 
                                    user_booked, 
                                    user_used, 
                                    created_at)
                                VALUES( {book.business_id}, 
                                        {book.place_id}, 
                                        {book.deal_reservation_id},
                                        {province.province_id}, 
                                        {book.booked}, 
                                        {book.used},  
                                        {book.amount_of_pending}, 
                                        {book.amount_of_canceled}, 
                                        {book.amount_of_rejected}, 
                                        {book.amount_of_accepted}, 
                                        {book.amount_of_completed}, 
                                        {book.user_booked}, 
                                        {use.user_used}, 
                                        {created_at})""")
                            db.commit()

    def get(self, business_id: int):
        current_date, set_date_from, set_date_end, created_at, time_from, time_end, month_from, month_end = get_current_time()
        self.insert(business_id, time_from, time_end, created_at)
        with self.master_database.session() as db:
            list_place = []
            list_daily_reservation = []
            deals = db.execute(
                f""" WITH tmp AS (
                SELECT 
                    fact_merchant_program_daily_report_for_reservation.*, 
                    dim_business.name as business_name, 
                    dim_2_province_place.name as place_name,
                    dim_province.name as province_name,
                    dim_deal_reservation.title as deal_reservation_title
                FROM 
                    fact_merchant_program_daily_report_for_reservation 
                    JOIN dim_business ON fact_merchant_program_daily_report_for_reservation.business_id = dim_business.id
                    JOIN dim_2_province_place ON fact_merchant_program_daily_report_for_reservation.place_id = dim_2_province_place.id
                    JOIN dim_province ON fact_merchant_program_daily_report_for_reservation.province_id = dim_province.id
                    JOIN dim_deal ON fact_merchant_program_daily_report_for_reservation.deal_reservation_id = dim_deal_reservation.id
                WHERE 
                    fact_merchant_program_daily_report_for_reservation.business_id = {business_id}
                    AND fact_merchant_program_daily_report_for_reservation.created_at = {created_at})
        
                SELECT * FROM tmp""").fetchall()

            for deal in deals:
                places = db.execute(
                    f"""
                SELECT 
                    fact_merchant_program_daily_report_for_reservation.place_id,
                    fact_merchant_program_daily_report_for_reservation.province_id,
                    fact_merchant_program_daily_report_for_reservation.booked,
                    fact_merchant_program_daily_report_for_reservation.used,
                    fact_merchant_program_daily_report_for_reservation.amount_of_pending,
                    fact_merchant_program_daily_report_for_reservation.amount_of_canceled,
                    fact_merchant_program_daily_report_for_reservation.amount_of_rejected,
                    fact_merchant_program_daily_report_for_reservation.amount_of_accepted,
                    fact_merchant_program_daily_report_for_reservation.amount_of_completed,
                    fact_merchant_program_daily_report_for_reservation.user_booked,
                    fact_merchant_program_daily_report_for_reservation.user_used,
                    fact_merchant_program_daily_report_for_reservation.created_at, 
                    dim_business.name as business_name, 
                    dim_2_province_place.name as place_name,
                    dim_province.name as province_name,
                    dim_deal_reservation.title as deal_reservation_title
                FROM 
                    fact_merchant_program_daily_report_for_reservation 
                    JOIN dim_business ON fact_merchant_program_daily_report_for_reservation.business_id = dim_business.id
                    JOIN dim_2_province_place ON fact_merchant_program_daily_report_for_reservation.place_id = dim_2_province_place.id
                    JOIN dim_province ON fact_merchant_program_daily_report_for_reservation.province_id = dim_province.id
                    JOIN dim_deal_reservation ON fact_merchant_program_daily_report_for_reservation.deal_reservation_id = dim_deal_reservation.id
                WHERE 
                    fact_merchant_program_daily_report_for_reservation.deal_reservation_id = {deal.deal_reservation_id}
                ORDER BY 
                    fact_merchant_program_daily_report_for_reservation.business_id,
                    fact_merchant_program_daily_report_for_reservation.place_id,
                    fact_merchant_program_daily_report_for_reservation.deal_reservation_id""").fetchall()
                for place in places:
                    if place.place_id == deal.place_id:
                        list_place.append(Place(place_id=place.place_id,
                                                booked=place.booked,
                                                used=place.used,
                                                amount_of_pending=place.amount_of_pending,
                                                amount_of_canceled=place.amount_of_canceled,
                                                amount_of_rejected=place.amount_of_rejected,
                                                amount_of_accepted=place.amount_of_accepted,
                                                amount_of_completed=place.amount_of_completed,
                                                user_booked=place.user_booked,
                                                user_used=place.user_used,
                                                province_name=place.province_name,
                                                deal_title=place.deal_reservation_title,
                                                place_name=place.place_name,
                                                business_name=place.business_name))
                list_daily_reservation.append(
                    DailyReservationReport(reservation_id=deal.deal_reservation_id, places=list_place))
            return list_daily_reservation
