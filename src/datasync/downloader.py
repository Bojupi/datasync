import copy
import itertools
from pathlib import Path
from typing import List, Optional

import pandas as pd
import tushare as ts

from .utils import parse_json


class TSDownloader:
    """
    Tushare数据下载器
    """

    pro = ts.pro_api()

    def __init__(self):
        self.apis = parse_json(Path(__file__).resolve().parent / "api.json")
        self.schema = parse_json(Path(__file__).resolve().parent / "schema.json")

    def _request(self, api: str, nmap: dict, cols: List[str], **kwargs) -> Optional[pd.DataFrame]:
        """调用指定API并处理分页请求，返回合并后的数据"""
        all_data = []
        offset_unit = kwargs.get("offset", None)
        kwargs["offset"] = 0

        while True:
            data = eval("self." + api)(**kwargs)
            data.rename(columns=nmap, inplace=True)
            all_data.append(data[cols])
            if offset_unit is None or len(data) <= offset_unit:
                break
            kwargs["offset"] += offset_unit

        return pd.concat(all_data, ignore_index=True)

    def _set_api(self, name: str, date: Optional[str], code: Optional[str]) -> List[dict]:
        """根据API配置生成请求参数组合"""
        api = copy.deepcopy(self.apis[name])

        for key, value in api.items():
            if isinstance(value, str):
                api[key] = value.format(date=date, code=code)
                api[key] = api[key].split("||")
            else:
                api[key] = [value]

        apis = []
        for i in itertools.product(*[api[key] for key in api.keys()]):
            apis.append(dict(zip(api.keys(), i)))
        return apis

    def _transfrom(self, data: Optional[pd.DataFrame], name: str) -> Optional[pd.DataFrame]:
        """根据schema.json中定义对数据进行类型转换"""
        bool_map = {'Y': True, 'N': False,
                    '1': True, '0': False, 1: True, 0: False}
        bool_col = [k for k in self.schema[name].keys() if self.schema[name][k] == "bool"]
        for c in bool_col:
            data[c] = data[c].map(bool_map)
        return data.astype(self.schema[name])

    def download(self, name: str, date: Optional[str]=None, code: Optional[str]=None) -> Optional[pd.DataFrame]:
        """下载指定数据"""
        api = self._set_api(name, date, code)
        if isinstance(api, list):
            data = pd.concat([df.astype(object) for df in (self._request(**a) for a in api)])
        else:
            data = self._request(**api)
        return self._transfrom(data, name).drop_duplicates().reset_index(drop=True)
