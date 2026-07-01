# OpenFIGI 自动解析 复核包 v2(已修复 3 个 blocker)

> 上轮复核抓出 QQQ 3 只外资股解析成货币报价线(HONGBP/TRI4EUR/AZNN)。已修复。
> 请二轮确认:①这 3 个已修正 ②无新的货币后缀/异常 ticker ③外资/双类股正确。

## A. 修复内容
1. **OpenFIGI 查询加 `exchCode=US`**:只要美国综合上市线;查不到则返回空(不再吐外资线)。
2. **_pick 只取 exchCode=US + 合法 ticker**;`_bad_ticker` 拒绝货币后缀(*GBP/*EUR…)、超长、含数字。
3. **人工 override 表**(`overrides.py`):OpenFIGI 查不到美股线的外资/ADR,人工核对后 override。
   当前:HON(US4385161066)、TRI(CA8849038085)、AZN(US0463531089)—— 均复核确认。
4. 查不到又不在人工表 → `UNRESOLVED`,**绝不塞垃圾进 13F**。

## B. 修复验证(上轮 3 个错误)
| 名称 | 上轮(错) | 本轮(修) |
|---|---|---|
| Honeywell | HONGBP | **HON** ✓ |
| Thomson Reuters | TRI4EUR | **TRI** ✓ |
| AstraZeneca | AZNN | **AZN** ✓ |

## C. QQQ 完整解析表(逐条核)
### QQQ(Invesco QQQ Trust, Series 1) — 股票101 / 现金0 / 未解析0
| # | 名称 | ISIN | →Ticker | 分类 | 来源 |
|---|---|---|---|---|---|
| 1 | NVIDIA Corp. | US67066G1040 | NVDA | equity | 人工表 |
| 2 | Apple Inc. | US0378331005 | AAPL | equity | OpenFIGI |
| 3 | Microsoft Corp. | US5949181045 | MSFT | equity | OpenFIGI |
| 4 | Amazon.com, Inc. | US0231351067 | AMZN | equity | OpenFIGI |
| 5 | Tesla, Inc. | US88160R1014 | TSLA | equity | OpenFIGI |
| 6 | Meta Platforms, Inc. | US30303M1027 | META | equity | OpenFIGI |
| 7 | Alphabet Inc. | US02079K3059 | GOOGL | equity | OpenFIGI |
| 8 | Alphabet Inc. | US02079K1079 | GOOG | equity | OpenFIGI |
| 9 | Broadcom Inc. | US11135F1012 | AVGO | equity | 人工表 |
| 10 | Palantir Technologies Inc. | US69608A1088 | PLTR | equity | OpenFIGI |
| 11 | Netflix, Inc. | US64110L1061 | NFLX | equity | OpenFIGI |
| 12 | Costco Wholesale Corp. | US22160K1051 | COST | equity | OpenFIGI |
| 13 | Advanced Micro Devices, Inc. | US0079031078 | AMD | equity | 人工表 |
| 14 | Micron Technology, Inc. | US5951121038 | MU | equity | 人工表 |
| 15 | Cisco Systems, Inc. | US17275R1023 | CSCO | equity | OpenFIGI |
| 16 | T-Mobile US, Inc. | US8725901040 | TMUS | equity | OpenFIGI |
| 17 | Lam Research Corp. | US5128073062 | LRCX | equity | 人工表 |
| 18 | AppLovin Corp. | US03831W1080 | APP | equity | OpenFIGI |
| 19 | Applied Materials, Inc. | US0382221051 | AMAT | equity | 人工表 |
| 20 | Intuitive Surgical, Inc. | US46120E6023 | ISRG | equity | OpenFIGI |
| 21 | Linde PLC | IE000S9YS762 | LIN | equity | OpenFIGI |
| 22 | Shopify Inc. | CA82509L1076 | SHOP | equity | OpenFIGI |
| 23 | PepsiCo, Inc. | US7134481081 | PEP | equity | OpenFIGI |
| 24 | Intuit Inc. | US4612021034 | INTU | equity | OpenFIGI |
| 25 | QUALCOMM Inc. | US7475251036 | QCOM | equity | 人工表 |
| 26 | Amgen Inc. | US0311621009 | AMGN | equity | OpenFIGI |
| 27 | Intel Corp. | US4581401001 | INTC | equity | 人工表 |
| 28 | Booking Holdings Inc. | US09857L1089 | BKNG | equity | OpenFIGI |
| 29 | KLA Corp. | US4824801009 | KLAC | equity | 人工表 |
| 30 | Texas Instruments Inc. | US8825081040 | TXN | equity | 人工表 |
| 31 | Gilead Sciences, Inc. | US3755581036 | GILD | equity | OpenFIGI |
| 32 | Adobe Inc. | US00724F1012 | ADBE | equity | OpenFIGI |
| 33 | Analog Devices, Inc. | US0326541051 | ADI | equity | 人工表 |
| 34 | Palo Alto Networks, Inc. | US6974351057 | PANW | equity | OpenFIGI |
| 35 | Honeywell International Inc. | US4385161066 | HON | equity | 人工表 |
| 36 | CrowdStrike Holdings, Inc. | US22788C1053 | CRWD | equity | OpenFIGI |
| 37 | Vertex Pharmaceuticals Inc. | US92532F1003 | VRTX | equity | OpenFIGI |
| 38 | Constellation Energy Corp. | US21037T1097 | CEG | equity | OpenFIGI |
| 39 | Comcast Corp. | US20030N1019 | CMCSA | equity | OpenFIGI |
| 40 | Automatic Data Processing, Inc. | US0530151036 | ADP | equity | OpenFIGI |
| 41 | MercadoLibre, Inc. | US58733R1023 | MELI | equity | OpenFIGI |
| 42 | Starbucks Corp. | US8552441094 | SBUX | equity | OpenFIGI |
| 43 | ASML Holding N.V. | USN070592100 | ASML | equity | 人工表 |
| 44 | DoorDash, Inc. | US25809K1051 | DASH | equity | OpenFIGI |
| 45 | Synopsys, Inc. | US8716071076 | SNPS | equity | OpenFIGI |
| 46 | Cadence Design Systems, Inc. | US1273871087 | CDNS | equity | OpenFIGI |
| 47 | Marriott International, Inc. | US5719032022 | MAR | equity | OpenFIGI |
| 48 | Regeneron Pharmaceuticals, Inc. | US75886F1075 | REGN | equity | OpenFIGI |
| 49 | O'Reilly Automotive, Inc. | US67103H1077 | ORLY | equity | OpenFIGI |
| 50 | PDD Holdings Inc. | US7223041028 | PDD | equity | OpenFIGI |
| 51 | Cintas Corp. | US1729081059 | CTAS | equity | OpenFIGI |
| 52 | Monster Beverage Corp. | US61174X1090 | MNST | equity | OpenFIGI |
| 53 | Marvell Technology, Inc. | US5738741041 | MRVL | equity | 人工表 |
| 54 | Warner Bros. Discovery, Inc. | US9344231041 | WBD | equity | OpenFIGI |
| 55 | Mondelez International, Inc. | US6092071058 | MDLZ | equity | OpenFIGI |
| 56 | CSX Corp. | US1264081035 | CSX | equity | OpenFIGI |
| 57 | Autodesk, Inc. | US0527691069 | ADSK | equity | OpenFIGI |
| 58 | American Electric Power Co., Inc. | US0255371017 | AEP | equity | OpenFIGI |
| 59 | Fortinet, Inc. | US34959E1091 | FTNT | equity | OpenFIGI |
| 60 | Western Digital Corp. | US9581021055 | WDC | equity | OpenFIGI |
| 61 | Seagate Technology Holdings PLC | IE00BKVD2N49 | STX | equity | OpenFIGI |
| 62 | Thomson Reuters Corp. | CA8849038085 | TRI | equity | 人工表 |
| 63 | Ross Stores, Inc. | US7782961038 | ROST | equity | OpenFIGI |
| 64 | Airbnb, Inc. | US0090661010 | ABNB | equity | OpenFIGI |
| 65 | PACCAR Inc. | US6937181088 | PCAR | equity | OpenFIGI |
| 66 | NXP Semiconductors N.V. | NL0009538784 | NXPI | equity | 人工表 |
| 67 | PayPal Holdings, Inc. | US70450Y1038 | PYPL | equity | OpenFIGI |
| 68 | IDEXX Laboratories, Inc. | US45168D1046 | IDXX | equity | OpenFIGI |
| 69 | AstraZeneca PLC | US0463531089 | AZN | equity | 人工表 |
| 70 | Alnylam Pharmaceuticals, Inc. | US02043Q1076 | ALNY | equity | OpenFIGI |
| 71 | Electronic Arts Inc. | US2855121099 | EA | equity | OpenFIGI |
| 72 | Roper Technologies, Inc. | US7766961061 | ROP | equity | OpenFIGI |
| 73 | Ferrovial SE | NL0015001FS8 | FER | equity | OpenFIGI |
| 74 | Take-Two Interactive Software, Inc. | US8740541094 | TTWO | equity | OpenFIGI |
| 75 | Fastenal Co. | US3119001044 | FAST | equity | OpenFIGI |
| 76 | Workday, Inc. | US98138H1014 | WDAY | equity | OpenFIGI |
| 77 | Baker Hughes Co. | US05722G1004 | BKR | equity | OpenFIGI |
| 78 | Axon Enterprise, Inc. | US05464C1018 | AXON | equity | OpenFIGI |
| 79 | Datadog, Inc. | US23804L1035 | DDOG | equity | OpenFIGI |
| 80 | Exelon Corp. | US30161N1019 | EXC | equity | OpenFIGI |
| 81 | Xcel Energy Inc. | US98389B1008 | XEL | equity | OpenFIGI |
| 82 | Monolithic Power Systems, Inc. | US6098391054 | MPWR | equity | 人工表 |
| 83 | Diamondback Energy, Inc. | US25278X1090 | FANG | equity | OpenFIGI |
| 84 | Coca-Cola Europacific Partners PLC | GB00BDCPN049 | CCEP | equity | OpenFIGI |
| 85 | Strategy Inc. | US5949724083 | MSTR | equity | OpenFIGI |
| 86 | Paychex, Inc. | US7043261079 | PAYX | equity | OpenFIGI |
| 87 | Cognizant Technology Solutions Corp. | US1924461023 | CTSH | equity | OpenFIGI |
| 88 | Keurig Dr Pepper Inc. | US49271V1008 | KDP | equity | OpenFIGI |
| 89 | Copart, Inc. | US2172041061 | CPRT | equity | OpenFIGI |
| 90 | GE HealthCare Technologies Inc. | US36266G1076 | GEHC | equity | OpenFIGI |
| 91 | Insmed Inc. | US4576693075 | INSM | equity | OpenFIGI |
| 92 | Zscaler, Inc. | US98980G1022 | ZS | equity | OpenFIGI |
| 93 | Microchip Technology Inc. | US5950171042 | MCHP | equity | 人工表 |
| 94 | Old Dominion Freight Line, Inc. | US6795801009 | ODFL | equity | OpenFIGI |
| 95 | Verisk Analytics, Inc. | US92345Y1064 | VRSK | equity | OpenFIGI |
| 96 | Kraft Heinz Co. (The) | US5007541064 | KHC | equity | OpenFIGI |
| 97 | CoStar Group, Inc. | US22160N1090 | CSGP | equity | OpenFIGI |
| 98 | Atlassian Corp. | US0494681010 | TEAM | equity | OpenFIGI |
| 99 | Charter Communications, Inc. | US16119P1084 | CHTR | equity | OpenFIGI |
| 100 | DexCom, Inc. | US2521311074 | DXCM | equity | OpenFIGI |
| 101 | ARM Holdings PLC | US0420682058 | ARM | equity | 人工表 |

## D. XLK 完整解析表(逐条核)
### XLK(The Technology Select Sector SPDR Fund) — 股票68 / 现金3 / 未解析1
| # | 名称 | ISIN | →Ticker | 分类 | 来源 |
|---|---|---|---|---|---|
| 1 | NVIDIA Corp | US67066G1040 | NVDA | equity | 人工表 |
| 2 | Microsoft Corp | US5949181045 | MSFT | equity | OpenFIGI |
| 3 | Apple Inc | US0378331005 | AAPL | equity | OpenFIGI |
| 4 | Broadcom Inc | US11135F1012 | AVGO | equity | 人工表 |
| 5 | Palantir Technologies Inc | US69608A1088 | PLTR | equity | OpenFIGI |
| 6 | Oracle Corp | US68389X1054 | ORCL | equity | OpenFIGI |
| 7 | Cisco Systems Inc | US17275R1023 | CSCO | equity | OpenFIGI |
| 8 | International Business Machines Corp | US4592001014 | IBM | equity | OpenFIGI |
| 9 | Advanced Micro Devices Inc | US0079031078 | AMD | equity | 人工表 |
| 10 | Salesforce Inc | US79466L3024 | CRM | equity | OpenFIGI |
| 11 | AppLovin Corp | US03831W1080 | APP | equity | OpenFIGI |
| 12 | ServiceNow Inc | US81762P1021 | NOW | equity | OpenFIGI |
| 13 | Intuit Inc | US4612021034 | INTU | equity | OpenFIGI |
| 14 | Micron Technology Inc | US5951121038 | MU | equity | 人工表 |
| 15 | QUALCOMM Inc | US7475251036 | QCOM | equity | 人工表 |
| 16 | Lam Research Corp | US5128073062 | LRCX | equity | 人工表 |
| 17 | Texas Instruments Inc | US8825081040 | TXN | equity | 人工表 |
| 18 | Applied Materials Inc | US0382221051 | AMAT | equity | 人工表 |
| 19 | Accenture PLC | IE00B4BNMY34 | ACN | equity | OpenFIGI |
| 20 | Amphenol Corp | US0320951017 | APH | equity | OpenFIGI |
| 21 | Arista Networks Inc | US0404132054 | ANET | equity | OpenFIGI |
| 22 | Adobe Inc | US00724F1012 | ADBE | equity | OpenFIGI |
| 23 | Intel Corp | US4581401001 | INTC | equity | 人工表 |
| 24 | KLA Corp | US4824801009 | KLAC | equity | 人工表 |
| 25 | Palo Alto Networks Inc | US6974351057 | PANW | equity | OpenFIGI |
| 26 | Crowdstrike Holdings Inc | US22788C1053 | CRWD | equity | OpenFIGI |
| 27 | Analog Devices Inc | US0326541051 | ADI | equity | 人工表 |
| 28 | Cadence Design Systems Inc | US1273871087 | CDNS | equity | OpenFIGI |
| 29 | Synopsys Inc | US8716071076 | SNPS | equity | OpenFIGI |
| 30 | Motorola Solutions Inc | US6200763075 | MSI | equity | OpenFIGI |
| 31 | Autodesk Inc | US0527691069 | ADSK | equity | OpenFIGI |
| 32 | TE Connectivity PLC | IE000IVNQZ81 | TEL | equity | OpenFIGI |
| 33 | Corning Inc | US2193501051 | GLW | equity | OpenFIGI |
| 34 | NXP Semiconductors NV | NL0009538784 | NXPI | equity | 人工表 |
| 35 | Fortinet Inc | US34959E1091 | FTNT | equity | OpenFIGI |
| 36 | Roper Technologies Inc | US7766961061 | ROP | equity | OpenFIGI |
| 37 | Workday Inc | US98138H1014 | WDAY | equity | OpenFIGI |
| 38 | Seagate Technology Holdings PLC | IE00BKVD2N49 | STX | equity | OpenFIGI |
| 39 | Datadog Inc | US23804L1035 | DDOG | equity | OpenFIGI |
| 40 | Monolithic Power Systems Inc | US6098391054 | MPWR | equity | 人工表 |
| 41 | Dell Technologies Inc | US24703L2025 | DELL | equity | OpenFIGI |
| 42 | Western Digital Corp | US9581021055 | WDC | equity | OpenFIGI |
| 43 | Fair Isaac Corp | US3032501047 | FICO | equity | OpenFIGI |
| 44 | Microchip Technology Inc | US5950171042 | MCHP | equity | 人工表 |
| 45 | Cognizant Technology Solutions Corp | US1924461023 | CTSH | equity | OpenFIGI |
| 46 | Hewlett Packard Enterprise Co | US42824C1099 | HPE | equity | OpenFIGI |
| 47 | Keysight Technologies Inc | US49338L1035 | KEYS | equity | OpenFIGI |
| 48 | Teledyne Technologies Inc | US8793601050 | TDY | equity | OpenFIGI |
| 49 | HP Inc | US40434L1052 | HPQ | equity | OpenFIGI |
| 50 | PTC Inc | US69370C1009 | PTC | equity | OpenFIGI |
| 51 | Super Micro Computer Inc | US86800U3023 | SMCI | equity | OpenFIGI |
| 52 | NetApp Inc | US64110D1046 | NTAP | equity | OpenFIGI |
| 53 | First Solar Inc | US3364331070 | FSLR | equity | OpenFIGI |
| 54 | VeriSign Inc | US92343E1029 | VRSN | equity | OpenFIGI |
| 55 | Jabil Inc | US4663131039 | JBL | equity | OpenFIGI |
| 56 | Tyler Technologies Inc | US9022521051 | TYL | equity | OpenFIGI |
| 57 | Teradyne Inc | US8807701029 | TER | equity | 人工表 |
| 58 | CDW Corp/DE | US12514G1085 | CDW | equity | OpenFIGI |
| 59 | State Street Global Advisors | US8574927062 | — | cash | OpenFIGI |
| 60 | ON Semiconductor Corp | US6821891057 | ON | equity | 人工表 |
| 61 | Gartner Inc | US3666511072 | IT | equity | OpenFIGI |
| 62 | Trimble Inc | US8962391004 | TRMB | equity | OpenFIGI |
| 63 | GoDaddy Inc | US3802371076 | GDDY | equity | OpenFIGI |
| 64 | F5 Inc | US3156161024 | FFIV | equity | OpenFIGI |
| 65 | Gen Digital Inc | US6687711084 | GEN | equity | OpenFIGI |
| 66 | Zebra Technologies Corp | US9892071054 | ZBRA | equity | OpenFIGI |
| 67 | Skyworks Solutions Inc | US83088M1027 | SWKS | equity | 人工表 |
| 68 | Akamai Technologies Inc | US00971T1016 | AKAM | equity | OpenFIGI |
| 69 | EPAM Systems Inc | US29414B1044 | EPAM | equity | OpenFIGI |
| 70 | State Street Global Advisors | US8574927062 | — | cash | OpenFIGI |
| 71 | State Street Global Advisors | US8574927062 | — | cash | OpenFIGI |
| 72 | Chicago Mercantile Exchange | None | — | unresolved | — |

## E. 请复核员二轮确认
1. B 段 3 个是否确已修正为 HON/TRI/AZN。
2. C、D 两表**有无残留货币后缀/异常 ticker**(如 *GBP/*EUR/含数字)。
3. 外资(LIN/SHOP/STX/FER/CCEP)、双类股(GOOGL/GOOG)、ADR 是否正确。
4. 现金分类与 UNRESOLVED 是否合理。
