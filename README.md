# datasync

<p align="center">
  <img src="demo.gif" alt="演示" width="800">
</p>

datasync是一个用于本地化与同步[Tushare数据](https://tushare.pro/)的工具。在投研过程中，频繁从数据源重复抓取数据不仅效率较低下，还会消耗调用额度。因此，更合理的方式是将所需数据一次性下载到本地，后续有需要时直接从硬盘读取。本项目即为此目的而设计，支持本地化Tushare数据并有组织地存储为[Parquet](https://en.wikipedia.org/wiki/Apache_Parquet)文件（该格式体积小、读取高效，可通过pandas的[`pd.read_parquet(filters=)`](https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html)或[duckdb](https://github.com/duckdb/duckdb)便捷查询与处理）。

## 上手指南

### 安装

下载代码到本地后，需要在./src/datasync/downloader.py中配置Tushare Token<span style="color:gray; font-style:normal">（建议使用积分5000及以上的账户，如不足5000积分，也可以通过调整./src/datasync/update.py中的参数，或修改api.json和schema.json中的字段信息来使用本项目）</span>：

```python
pro = ts.pro_api("YOUR TOKEN")
```

本项目使用[uv](https://github.com/astral-sh/uv)进行环境管理。关于uv的安装与配置，请参考其官方文档说明。在激活uv环境后，在项目目录下运行以下命令即可完成环境配置并安装datasync：

```shell
uv sync
```

如不使用uv进行环境管理，也可以通过以下命令直接安装：

```shell
pip install .
```

### 使用

数据同步命令（参数可选）：

```shell
python -m datasync [-i <YYYY-MM-DD>] [-p <DIR>]
```

## 说明

数据本地初始化后的数据组织结构大致如下：

```
.
├── calendar.parquet        # 交易日历
├── fund                    # 基金
│   ├── adj                 # 基金复权因子
│   ├── info.parquet        # 基金基本信息
│   ├── nav                 # 基金净值
│   └── prcvol              # 基金量价
├── index                   # 指数
│   ├── prcvol              # 指数量价
│   └── weight              # 指数成分股权重
├── stock                   # 股票
│   ├── adj                 # 股票复权因子
│   ├── balance             # 股票资产负债表
│   ├── cashflow            # 股票现金流量表
│   ├── income              # 股票利润表
│   ├── indicator           # 股票财务指标数据
│   ├── info.parquet        # 股票基本信息
│   ├── prcvol              # 股票量价
│   ├── report              # 股票券商盈利预测数据
│   ├── swind.parquet       # 股票申万行业分类
│   └── value               # 股票每日（估值）指标
├── swind                   # 申万行业
│   └── prcvol              # 申万行业量价
└── state.json              # 历史更新状态记录
```