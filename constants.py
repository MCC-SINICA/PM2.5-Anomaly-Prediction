DATASET_FILES = ['epa_tw_14_direction.csv',
                 'epa_tw_15_direction.csv',
                 'epa_tw_16_direction.csv',
                 'epa_tw_17_direction.csv',
                 'epa_tw_18_direction.csv',
                 'epa_tw_19_direction.csv'
                ]
# size of 73
ALL_SITENAMES = [
    '三義', '三重', '中壢', '中山', '二林', '仁武', '冬山', '前金', '前鎮', '南投',
    '古亭', '善化', '嘉義', '土城', '埔里', '基隆', '士林', '大同', '大園', '大寮',
    '大里', '安南', '宜蘭', '小港', '屏東', '崙背', '左營', '平鎮', '彰化', '復興',
    '忠明', '恆春', '斗六', '新店', '新港', '新營', '新竹', '新莊', '朴子', '松山',
    '板橋', '林口', '林園', '桃園', '楠梓', '橋頭', '永和', '汐止', '沙鹿', '淡水',
    '湖口', '潮州', '竹山', '竹東', '線西', '美濃', '臺南', '臺東', '臺西', '花蓮',
    '苗栗', '菜寮', '萬華', '萬里', '西屯', '觀音', '豐原', '金門', '關山', '陽明',
    '頭份', '馬公', '馬祖', '鳳山', '麥寮', '龍潭', '富貴角'
    ]

SITENAMES = [
 '陽明', '萬里', '淡水', '基隆', '士林', '林口', '三重', '中山', '菜寮', '大園', '汐止', '大同', '松山', '萬華',
 '觀音', '新莊', '古亭', '永和', '板橋', '桃園', '土城', '新店', '平鎮', '中壢', '湖口', '龍潭', '新竹', '竹東',
 '宜蘭', '頭份', '冬山', '苗栗', '三義', '豐原', '沙鹿', '西屯', '忠明', '線西', '大里', '彰化', '花蓮', '埔里',
 '二林', '南投', '麥寮', '竹山', '崙背', '臺西', '斗六', '新港', '嘉義', '朴子', '新營', '善化', '關山', '安南',
 '臺南', '美濃', '臺東', '橋頭', '楠梓', '仁武', '屏東', '左營', '前金', '鳳山', '前鎮', '復興', '小港', '大寮',
 '潮州', '林園', '恆春'
 ]

FEATURE_COLS = ['SO2', 'CO', 'NO', 'NO2', 'NOx', 'O3', 'PM10', 'PM2.5',
                'RAINFALL', 'RH', 'AMB_TEMP', 'WIND_cos', 'WIND_sin',
                'month', 'day', 'hour' 
                ]

SUMMER_MONTHS = [4,5,6,7,8,9] # 1 is Junary

FIELD = [
    "sitename", 
    "best_rmse",
    "epoch",
    "timestamp"
]