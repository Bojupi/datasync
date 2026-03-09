import json
import time
from pathlib import Path
from typing import Union, Optional, List, Dict
from datetime import datetime, timedelta

import pandas as pd

from .wrappers import retry
from .utils import parse_json
from .downloader import TSDownloader


class UpdatePipline:
    """
    用于管理全量和增量数据下载、保存及状态更新
    """

    def __init__(self, downloader, path: Union[Path, str] = "../db"):
        self.downloader = downloader
        self.path = Path(path)
        self.state = self._load_state()

    def _load_state(self) -> dict:
        """从state.json中读取各表截至上一次更新的最新日期"""
        state_path = self.path / "state.json"
        if state_path.exists():
            return parse_json(state_path)
        return {}

    def _update_state(self, name: str, date: str):
        """将各表在本次更新的最新日期更新存回state.json中"""
        self.state[name] = date
        state_path = self.path / "state.json"
        with open(state_path, 'w') as f:
            json.dump(self.state, f, indent=4)

    def _save_data(self, data: Optional[pd.DataFrame], parent_path: Path, name: str, merge: bool = False):
        """将数据保存为parquet文件（根据需要与已有数据合并）"""
        parent_path.mkdir(parents=True, exist_ok=True)
        data_path = parent_path / name

        if merge and data_path.exists():
            existing = pd.read_parquet(data_path)
            data = pd.concat([existing, data]).drop_duplicates()

        data.to_parquet(data_path, index=False)

    def run_ftask(self, name: str):
        """全量更新"""
        data = self.downloader.download(name)
        path = Path(self.path, *(name.split('_')))
        self._save_data(data, path.parent, path.with_suffix(".parquet").name)
        print(f"\033[33m[{'-'.join(name.upper().split('_'))}]\033[0m-\033[32mUPDATED.\033[0m")

    @retry()
    def run_itask(self, name: str, date: str):
        """增量更新"""
        data = self.downloader.download(name, date=date)
        path = Path(self.path, *(name.split('_')))
        self._save_data(data, path, date[:-2] + ".parquet", merge=True)
        self._update_state(name, date)
        print(f"\033[33m[{'-'.join(name.upper().split('_'))}]\033[0m-\033[34m{date}\033[0m-\033[32mUPDATED.\033[0m")
        time.sleep(0.1)

    def run(
        self,
        ftask: List[str] = ["calendar", "stock_info", "fund_info", "stock_swind"],
        itask: Dict[str, int] = {
            "stock_prcvol": 1, "stock_adj": 1, "stock_value": 1, "stock_balance": 0, "stock_income": 0, "stock_cashflow": 0, "stock_indicator": 0, "stock_report": 0,
            "fund_prcvol": 1, "fund_nav": 1, "fund_adj": 1,
            "index_prcvol": 1, "index_weight": 0, "swind_prcvol": 1
        },
        init_date: str = "2010-01-01"
    ):
        """
        若运行时间晚于晚上10点，则更新数据至当日，否则更新数据至上一日
        （注：`init_date`仅在初始化数据库时有效，后续更新中无效）
        """
        for ft in ftask:
            self.run_ftask(ft)

        if datetime.now().hour > 22:
            end_date = datetime.today().strftime("%Y%m%d")
        else:
            end_date = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")

        for it, open_only in itask.items():
            calendar = pd.read_parquet(self.path/"calendar.parquet").sort_values("date")
            if it in self.state:
                mask = (calendar["date"] > self.state[it]) & (calendar["date"] <= end_date)
            else:
                mask = (calendar["date"] > init_date) & (calendar["date"] <= end_date)
            update_date = calendar.loc[mask]
            if open_only:
                update_date = update_date[update_date.is_open]
            for d in update_date["date"]:
                self.run_itask(it, d.strftime("%Y%m%d"))


def run_update(init_date: Optional[str], path: Optional[str]):
    td = TSDownloader()
    pipline = UpdatePipline(td, path=path)
    pipline.run(init_date=init_date)