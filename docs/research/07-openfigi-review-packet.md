# OpenFIGI 自动解析 复核包(升级:支持任意 ETF)

> 本轮升级把标的解析从 SOXX 专用扩展到任意 ETF。数据源仍是 LLMQuant(不变)。
> 复核重点:**OpenFIGI 自动把 name/ISIN 解析成 ticker 是否正确**(这是新增的信任假设)。

## A. 设计(两级解析,人工优先)
1. **SOXX** 命中人工核对映射表 → 直接用(最可信,已多轮复核)。
2. 其余成分股 → **OpenFIGI**(免费权威源)按 ISIN/CUSIP 解析:
   - 取 `exchCode=US`(美国综合)的条目的 ticker;
   - 证券类型含 fund/money market → 归**现金**(不查 13F);
   - 解析不上(如纯衍生品)→ 标 `UNRESOLVED`,**绝不臆测**。
3. OpenFIGI 返回真实映射、非模型生成;结果本地缓存。人工表优先级 > OpenFIGI。

## B. 请重点核验的风险点
- **双类股**:GOOGL vs GOOG、FOX/FOXA、BRK.A/BRK.B —— 取的是不是正确那一类?
- **ADR / 外资**:有没有取成非美国上市版本?
- **现金分类**:货基→现金是否得当?有无把真股票误判成现金、或反之?
- **UNRESOLVED**:被标未解析的,是不是确实无法映射(而非本应能解析)?

## C. XLK 完整解析表(逐条核)
### XLK(The Technology Select Sector SPDR Fund) 解析审计 — 共 72 行
股票 68 / 现金 3 / 未解析 1
| # | 名称 | ISIN | →Ticker | 分类 |
|---|---|---|---|---|
| 1 | NVIDIA Corp | US67066G1040 | NVDA | equity |
| 2 | Microsoft Corp | US5949181045 | MSFT | equity |
| 3 | Apple Inc | US0378331005 | AAPL | equity |
| 4 | Broadcom Inc | US11135F1012 | AVGO | equity |
| 5 | Palantir Technologies Inc | US69608A1088 | PLTR | equity |
| 6 | Oracle Corp | US68389X1054 | ORCL | equity |
| 7 | Cisco Systems Inc | US17275R1023 | CSCO | equity |
| 8 | International Business Machines Corp | US4592001014 | IBM | equity |
| 9 | Advanced Micro Devices Inc | US0079031078 | AMD | equity |
| 10 | Salesforce Inc | US79466L3024 | CRM | equity |
| 11 | AppLovin Corp | US03831W1080 | APP | equity |
| 12 | ServiceNow Inc | US81762P1021 | NOW | equity |
| 13 | Intuit Inc | US4612021034 | INTU | equity |
| 14 | Micron Technology Inc | US5951121038 | MU | equity |
| 15 | QUALCOMM Inc | US7475251036 | QCOM | equity |
| 16 | Lam Research Corp | US5128073062 | LRCX | equity |
| 17 | Texas Instruments Inc | US8825081040 | TXN | equity |
| 18 | Applied Materials Inc | US0382221051 | AMAT | equity |
| 19 | Accenture PLC | IE00B4BNMY34 | ACN | equity |
| 20 | Amphenol Corp | US0320951017 | APH | equity |
| 21 | Arista Networks Inc | US0404132054 | ANET | equity |
| 22 | Adobe Inc | US00724F1012 | ADBE | equity |
| 23 | Intel Corp | US4581401001 | INTC | equity |
| 24 | KLA Corp | US4824801009 | KLAC | equity |
| 25 | Palo Alto Networks Inc | US6974351057 | PANW | equity |
| 26 | Crowdstrike Holdings Inc | US22788C1053 | CRWD | equity |
| 27 | Analog Devices Inc | US0326541051 | ADI | equity |
| 28 | Cadence Design Systems Inc | US1273871087 | CDNS | equity |
| 29 | Synopsys Inc | US8716071076 | SNPS | equity |
| 30 | Motorola Solutions Inc | US6200763075 | MSI | equity |
| 31 | Autodesk Inc | US0527691069 | ADSK | equity |
| 32 | TE Connectivity PLC | IE000IVNQZ81 | TEL | equity |
| 33 | Corning Inc | US2193501051 | GLW | equity |
| 34 | NXP Semiconductors NV | NL0009538784 | NXPI | equity |
| 35 | Fortinet Inc | US34959E1091 | FTNT | equity |
| 36 | Roper Technologies Inc | US7766961061 | ROP | equity |
| 37 | Workday Inc | US98138H1014 | WDAY | equity |
| 38 | Seagate Technology Holdings PLC | IE00BKVD2N49 | STX | equity |
| 39 | Datadog Inc | US23804L1035 | DDOG | equity |
| 40 | Monolithic Power Systems Inc | US6098391054 | MPWR | equity |
| 41 | Dell Technologies Inc | US24703L2025 | DELL | equity |
| 42 | Western Digital Corp | US9581021055 | WDC | equity |
| 43 | Fair Isaac Corp | US3032501047 | FICO | equity |
| 44 | Microchip Technology Inc | US5950171042 | MCHP | equity |
| 45 | Cognizant Technology Solutions Corp | US1924461023 | CTSH | equity |
| 46 | Hewlett Packard Enterprise Co | US42824C1099 | HPE | equity |
| 47 | Keysight Technologies Inc | US49338L1035 | KEYS | equity |
| 48 | Teledyne Technologies Inc | US8793601050 | TDY | equity |
| 49 | HP Inc | US40434L1052 | HPQ | equity |
| 50 | PTC Inc | US69370C1009 | PTC | equity |
| 51 | Super Micro Computer Inc | US86800U3023 | SMCI | equity |
| 52 | NetApp Inc | US64110D1046 | NTAP | equity |
| 53 | First Solar Inc | US3364331070 | FSLR | equity |
| 54 | VeriSign Inc | US92343E1029 | VRSN | equity |
| 55 | Jabil Inc | US4663131039 | JBL | equity |
| 56 | Tyler Technologies Inc | US9022521051 | TYL | equity |
| 57 | Teradyne Inc | US8807701029 | TER | equity |
| 58 | CDW Corp/DE | US12514G1085 | CDW | equity |
| 59 | State Street Global Advisors | US8574927062 | — | cash |
| 60 | ON Semiconductor Corp | US6821891057 | ON | equity |
| 61 | Gartner Inc | US3666511072 | IT | equity |
| 62 | Trimble Inc | US8962391004 | TRMB | equity |
| 63 | GoDaddy Inc | US3802371076 | GDDY | equity |
| 64 | F5 Inc | US3156161024 | FFIV | equity |
| 65 | Gen Digital Inc | US6687711084 | GEN | equity |
| 66 | Zebra Technologies Corp | US9892071054 | ZBRA | equity |
| 67 | Skyworks Solutions Inc | US83088M1027 | SWKS | equity |
| 68 | Akamai Technologies Inc | US00971T1016 | AKAM | equity |
| 69 | EPAM Systems Inc | US29414B1044 | EPAM | equity |
| 70 | State Street Global Advisors | US8574927062 | — | cash |
| 71 | State Street Global Advisors | US8574927062 | — | cash |
| 72 | Chicago Mercantile Exchange | None | — | unresolved |

## D. QQQ 完整解析表(逐条核)
### QQQ(Invesco QQQ Trust, Series 1) 解析审计 — 共 101 行
股票 101 / 现金 0 / 未解析 0
| # | 名称 | ISIN | →Ticker | 分类 |
|---|---|---|---|---|
| 1 | NVIDIA Corp. | US67066G1040 | NVDA | equity |
| 2 | Apple Inc. | US0378331005 | AAPL | equity |
| 3 | Microsoft Corp. | US5949181045 | MSFT | equity |
| 4 | Amazon.com, Inc. | US0231351067 | AMZN | equity |
| 5 | Tesla, Inc. | US88160R1014 | TSLA | equity |
| 6 | Meta Platforms, Inc. | US30303M1027 | META | equity |
| 7 | Alphabet Inc. | US02079K3059 | GOOGL | equity |
| 8 | Alphabet Inc. | US02079K1079 | GOOG | equity |
| 9 | Broadcom Inc. | US11135F1012 | AVGO | equity |
| 10 | Palantir Technologies Inc. | US69608A1088 | PLTR | equity |
| 11 | Netflix, Inc. | US64110L1061 | NFLX | equity |
| 12 | Costco Wholesale Corp. | US22160K1051 | COST | equity |
| 13 | Advanced Micro Devices, Inc. | US0079031078 | AMD | equity |
| 14 | Micron Technology, Inc. | US5951121038 | MU | equity |
| 15 | Cisco Systems, Inc. | US17275R1023 | CSCO | equity |
| 16 | T-Mobile US, Inc. | US8725901040 | TMUS | equity |
| 17 | Lam Research Corp. | US5128073062 | LRCX | equity |
| 18 | AppLovin Corp. | US03831W1080 | APP | equity |
| 19 | Applied Materials, Inc. | US0382221051 | AMAT | equity |
| 20 | Intuitive Surgical, Inc. | US46120E6023 | ISRG | equity |
| 21 | Linde PLC | IE000S9YS762 | LIN | equity |
| 22 | Shopify Inc. | CA82509L1076 | SHOP | equity |
| 23 | PepsiCo, Inc. | US7134481081 | PEP | equity |
| 24 | Intuit Inc. | US4612021034 | INTU | equity |
| 25 | QUALCOMM Inc. | US7475251036 | QCOM | equity |
| 26 | Amgen Inc. | US0311621009 | AMGN | equity |
| 27 | Intel Corp. | US4581401001 | INTC | equity |
| 28 | Booking Holdings Inc. | US09857L1089 | BKNG | equity |
| 29 | KLA Corp. | US4824801009 | KLAC | equity |
| 30 | Texas Instruments Inc. | US8825081040 | TXN | equity |
| 31 | Gilead Sciences, Inc. | US3755581036 | GILD | equity |
| 32 | Adobe Inc. | US00724F1012 | ADBE | equity |
| 33 | Analog Devices, Inc. | US0326541051 | ADI | equity |
| 34 | Palo Alto Networks, Inc. | US6974351057 | PANW | equity |
| 35 | Honeywell International Inc. | US4385161066 | HONGBP | equity |
| 36 | CrowdStrike Holdings, Inc. | US22788C1053 | CRWD | equity |
| 37 | Vertex Pharmaceuticals Inc. | US92532F1003 | VRTX | equity |
| 38 | Constellation Energy Corp. | US21037T1097 | CEG | equity |
| 39 | Comcast Corp. | US20030N1019 | CMCSA | equity |
| 40 | Automatic Data Processing, Inc. | US0530151036 | ADP | equity |
| 41 | MercadoLibre, Inc. | US58733R1023 | MELI | equity |
| 42 | Starbucks Corp. | US8552441094 | SBUX | equity |
| 43 | ASML Holding N.V. | USN070592100 | ASML | equity |
| 44 | DoorDash, Inc. | US25809K1051 | DASH | equity |
| 45 | Synopsys, Inc. | US8716071076 | SNPS | equity |
| 46 | Cadence Design Systems, Inc. | US1273871087 | CDNS | equity |
| 47 | Marriott International, Inc. | US5719032022 | MAR | equity |
| 48 | Regeneron Pharmaceuticals, Inc. | US75886F1075 | REGN | equity |
| 49 | O'Reilly Automotive, Inc. | US67103H1077 | ORLY | equity |
| 50 | PDD Holdings Inc. | US7223041028 | PDD | equity |
| 51 | Cintas Corp. | US1729081059 | CTAS | equity |
| 52 | Monster Beverage Corp. | US61174X1090 | MNST | equity |
| 53 | Marvell Technology, Inc. | US5738741041 | MRVL | equity |
| 54 | Warner Bros. Discovery, Inc. | US9344231041 | WBD | equity |
| 55 | Mondelez International, Inc. | US6092071058 | MDLZ | equity |
| 56 | CSX Corp. | US1264081035 | CSX | equity |
| 57 | Autodesk, Inc. | US0527691069 | ADSK | equity |
| 58 | American Electric Power Co., Inc. | US0255371017 | AEP | equity |
| 59 | Fortinet, Inc. | US34959E1091 | FTNT | equity |
| 60 | Western Digital Corp. | US9581021055 | WDC | equity |
| 61 | Seagate Technology Holdings PLC | IE00BKVD2N49 | STX | equity |
| 62 | Thomson Reuters Corp. | CA8849038085 | TRI4EUR | equity |
| 63 | Ross Stores, Inc. | US7782961038 | ROST | equity |
| 64 | Airbnb, Inc. | US0090661010 | ABNB | equity |
| 65 | PACCAR Inc. | US6937181088 | PCAR | equity |
| 66 | NXP Semiconductors N.V. | NL0009538784 | NXPI | equity |
| 67 | PayPal Holdings, Inc. | US70450Y1038 | PYPL | equity |
| 68 | IDEXX Laboratories, Inc. | US45168D1046 | IDXX | equity |
| 69 | AstraZeneca PLC | US0463531089 | AZNN | equity |
| 70 | Alnylam Pharmaceuticals, Inc. | US02043Q1076 | ALNY | equity |
| 71 | Electronic Arts Inc. | US2855121099 | EA | equity |
| 72 | Roper Technologies, Inc. | US7766961061 | ROP | equity |
| 73 | Ferrovial SE | NL0015001FS8 | FER | equity |
| 74 | Take-Two Interactive Software, Inc. | US8740541094 | TTWO | equity |
| 75 | Fastenal Co. | US3119001044 | FAST | equity |
| 76 | Workday, Inc. | US98138H1014 | WDAY | equity |
| 77 | Baker Hughes Co. | US05722G1004 | BKR | equity |
| 78 | Axon Enterprise, Inc. | US05464C1018 | AXON | equity |
| 79 | Datadog, Inc. | US23804L1035 | DDOG | equity |
| 80 | Exelon Corp. | US30161N1019 | EXC | equity |
| 81 | Xcel Energy Inc. | US98389B1008 | XEL | equity |
| 82 | Monolithic Power Systems, Inc. | US6098391054 | MPWR | equity |
| 83 | Diamondback Energy, Inc. | US25278X1090 | FANG | equity |
| 84 | Coca-Cola Europacific Partners PLC | GB00BDCPN049 | CCEP | equity |
| 85 | Strategy Inc. | US5949724083 | MSTR | equity |
| 86 | Paychex, Inc. | US7043261079 | PAYX | equity |
| 87 | Cognizant Technology Solutions Corp. | US1924461023 | CTSH | equity |
| 88 | Keurig Dr Pepper Inc. | US49271V1008 | KDP | equity |
| 89 | Copart, Inc. | US2172041061 | CPRT | equity |
| 90 | GE HealthCare Technologies Inc. | US36266G1076 | GEHC | equity |
| 91 | Insmed Inc. | US4576693075 | INSM | equity |
| 92 | Zscaler, Inc. | US98980G1022 | ZS | equity |
| 93 | Microchip Technology Inc. | US5950171042 | MCHP | equity |
| 94 | Old Dominion Freight Line, Inc. | US6795801009 | ODFL | equity |
| 95 | Verisk Analytics, Inc. | US92345Y1064 | VRSK | equity |
| 96 | Kraft Heinz Co. (The) | US5007541064 | KHC | equity |
| 97 | CoStar Group, Inc. | US22160N1090 | CSGP | equity |
| 98 | Atlassian Corp. | US0494681010 | TEAM | equity |
| 99 | Charter Communications, Inc. | US16119P1084 | CHTR | equity |
| 100 | DexCom, Inc. | US2521311074 | DXCM | equity |
| 101 | ARM Holdings PLC | US0420682058 | ARM | equity |

## E. 请复核员回答
1. C、D 两表里有没有**解析错的 ticker**?(尤其双类股/ADR/外资)
2. 现金分类有没有错判?
3. UNRESOLVED 的那些,是否合理(确实无法映射)?
4. 这套'人工表优先 + OpenFIGI 兜底 + 标红不猜'的策略,够不够券商级可信?
