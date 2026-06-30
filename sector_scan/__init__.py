"""sector_scan — Sector Smart Money Scan 工具.

围绕"用 agent 做 skill 满足量化投资需求"这一中心,从 SOXX 做起。
分层(便于逐层迭代,互不牵连):
    config   - 配置 / 密钥(只从环境读)
    data     - LLMQuant Data 接口封装(真实数据来源)
    resolve  - 标的解析:holding_name/cusip/isin -> ticker(零运行时猜测)
    (后续) scan/compute/render/brain ...

铁律见仓库根 CLAUDE.md:准确、可读、可信、防幻觉;慢慢来、可回退。
"""

__version__ = "0.0.1"
