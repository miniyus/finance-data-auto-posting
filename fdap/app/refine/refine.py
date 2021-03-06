from typing import List, Dict, Union
from fdap.app.opendart.finance_data import FinanceData
from fdap.app.opendart.opendart_data import AcntCollection
from fdap.contracts.service import Service
from fdap.app.refine.refine_data import RefineData
from fdap.app.refine.refine_data import RefineCollection
from fdap.app.kiwoom.basic_info import BasicInfo


class Refine(Service):
    _basic_info: List[BasicInfo]
    _acnt: Dict[str, AcntCollection]
    _refine_data: List[RefineData]

    def __init__(self):
        super().__init__()
        self._basic_info = []
        self._acnt = {}
        self._refine_data = []
        self._logger.info('init: %s', __name__)

    def refine_multiple(self, basic_info: List[BasicInfo], acnt: Dict[str, AcntCollection]) -> Union[
        RefineCollection, List[RefineData]
    ]:
        self._basic_info = basic_info
        self._acnt = acnt

        for stock in basic_info:
            if stock.code in acnt:
                self._refine_data.append(self.refine_single(stock, acnt[stock.code]))
        return RefineCollection(self.get_refined_data())

    def refine_single(self, basic_info: BasicInfo, acnt: AcntCollection) -> RefineData:
        refine_data = RefineData()

        refine_data.basic_info = basic_info

        finance_data = FinanceData()
        refine_data.finance_data = finance_data.map(acnt)

        self._logger.debug('stock_code:{}'.format(basic_info.code))

        issue_cnt = int((basic_info.capital * 100000000) / basic_info.current_price)
        refine_data.finance_data.calculate_flow_rate()
        refine_data.finance_data.calculate_debt_rate()
        refine_data.finance_data.calculate_pbr(basic_info.current_price, issue_cnt)
        refine_data.finance_data.calculate_per(basic_info.current_price, issue_cnt)
        refine_data.finance_data.calculate_roe(basic_info.current_price, issue_cnt)

        return refine_data

    def get_refined_data(self) -> List[RefineData]:
        return self._refine_data
