import pandas as pd

def process_get_report():
    df = pd.read_csv('/opt/airflow/dags/data/raw_restaurant_data.csv')
    # df.dropna(subset=['name_res', 'address'], how='all', inplace=True)

    df['name_res'].fillna('Unknown', inplace=True)
    df['kind_res'].fillna('Unknown', inplace=True)
    df['address'].fillna('Unknown', inplace=True)
    df['open_time'].fillna('Unknown', inplace=True)
    df['number_rating'].fillna('0', inplace=True)

    def clean_number_rating(value):
        if isinstance(value, str):
            if '+' in value:
                return int(value.replace('+', ''))  
            else:
                return int(value) 
        return pd.NA 
    df['number_rating'] = df['number_rating'].apply(clean_number_rating)
    
    # phan vung theo quan
    noi = ['Hoàng Mai', 'Long Biên', 'Thanh Xuân', 'Bắc Từ Liêm', 'Ba Đình', 'Cầu Giấy', 'Đống Đa', 'Hai Bà Trưng', 'Hoàn Kiếm', 'Hà Đông', 'Tây Hồ', 'Nam Từ Liêm']
    ngoai = ['Bắc Hà', 'Chương Mỹ', 'Đan Phượng', 'Đông Anh', 'Gia Lâm', 'Hoài Đức', 'Mê Linh', 'Phú Xuyên', 'Quốc Oai', 'Sóc Sơn', 'Thanh Trì', 'Thanh Oai', 'Từ Liêm']
    districts = noi + ngoai

    def get_district(address):
        for district in districts:
            if district in address:
                return district
        return 'Unknown'

    df['district'] = df['address'].apply(get_district)
    
    df['store_id'] = range(1, len(df) + 1)  
    df.set_index('store_id', inplace=True) 
    df.to_csv("/opt/airflow/dags/data/clean_data_restaurant.csv")

# ======== Phân tích để gửi báo cáo ==================
    district_counts = df['district'].value_counts()
    average_star = df.groupby('district')['star'].mean().round(2)
    total_ratings = df.groupby('district')['number_rating'].sum()

    # xử lý khoảng giá
    def parse_cost_range(cost_range):
        try:
            parts = str(cost_range).split(' - ')
            if len(parts) == 2:
                min_cost = float(parts[0].replace('.', '').strip())
                max_cost = float(parts[1].replace('.', '').strip())
                return min_cost, max_cost
        except ValueError:
            return None, None

    df[['min_cost', 'max_cost']] = df['cost_res'].apply(lambda x: pd.Series(parse_cost_range(x)))
    df['price_range'] = df['max_cost'] - df['min_cost']

    # chỉ tính tb trên các cửa hàng k bỏ trống khoảng giá để hạn chế lệch dl
    valid_df = df[(df['min_cost'] > 0) & (df['max_cost'] > 0)]
    average_min_cost = valid_df.groupby('district')['min_cost'].mean()
    average_max_cost = valid_df.groupby('district')['max_cost'].mean()

    average_cost_df = pd.DataFrame({
        'average_min_cost': average_min_cost,
        'average_max_cost': average_max_cost
    })

    # Convert về định dạng cũ "min cost - max cost"
    def format_cost_range(row):
        return '{:,.0f} - {:,.0f}'.format(row['average_min_cost'], row['average_max_cost'])

    average_cost_df['Average Cost Range'] = average_cost_df.apply(format_cost_range, axis=1)
    average_cost_df = average_cost_df.reset_index()

    report_df = pd.DataFrame({
        'Số lượng cửa hàng': district_counts,
        'Đánh giá trung bình': average_star,
        'Tổng số lượt đánh giá': total_ratings
    })

    # merge
    report_df = report_df.merge(average_cost_df[['district', 'Average Cost Range']], left_index=True, right_on='district', how='left')
    report_df = report_df[['district', 'Số lượng cửa hàng', 'Đánh giá trung bình', 'Tổng số lượt đánh giá', 'Average Cost Range']]
    report_df.columns = ['Khu vực', 'Số lượng cửa hàng', 'Đánh giá trung bình (/5)', 'Số lượng đánh giá (+)', 'Khoảng giá trung bình (Vnđ)']

    # print(report_df)
    return report_df