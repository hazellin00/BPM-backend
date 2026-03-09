"""
臨床數據導入工具

將 cleaned_diet_data1.csv 匯入 Supabase dietary_knowledge_base 表
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

# 載入環境變數
load_dotenv()

# 初始化 Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("❌ 錯誤: 缺少 Supabase 環境變數")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def import_csv_to_supabase(csv_path: str, table_name: str = "dietary_knowledge_base"):
    """
    匯入 CSV 到 Supabase

    Args:
        csv_path: CSV 檔案路徑
        table_name: 目標資料表名稱
    """
    print(f"📁 讀取 CSV: {csv_path}")

    try:
        # 讀取 CSV
        df = pd.read_csv(csv_path)
        print(f"✅ 讀取成功,共 {len(df)} 筆資料")
        print(f"📊 欄位: {list(df.columns)}")

        # 清理數據 (處理 NaN)
        df = df.fillna("")

        # 轉換為字典列表
        records = df.to_dict("records")

        # 分批匯入 (每次 100 筆,避免超時)
        batch_size = 100
        total_batches = (len(records) + batch_size - 1) // batch_size

        print(f"\n🚀 開始匯入,分為 {total_batches} 批次...")

        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            batch_num = (i // batch_size) + 1

            try:
                response = supabase.table(table_name).insert(batch).execute()
                print(f"✅ 批次 {batch_num}/{total_batches} 完成 ({len(batch)} 筆)")
            except Exception as e:
                print(f"❌ 批次 {batch_num} 失敗: {e}")
                print(f"   錯誤樣本: {batch[0]}")

        print(f"\n🎉 匯入完成!總計 {len(records)} 筆資料")

    except FileNotFoundError:
        print(f"❌ 錯誤: 找不到檔案 {csv_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 匯入失敗: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # CSV 檔案路徑
    csv_file = os.path.join(os.path.dirname(__file__), "..", "cleaned_diet_data1.csv")

    print("=" * 60)
    print("🏥 VitalGuard - 臨床數據匯入工具")
    print("=" * 60)

    # 執行匯入
    import_csv_to_supabase(csv_file)

    print("\n💡 提示: 請確認 Supabase 中 dietary_knowledge_base 表已正確創建")
    print("   必要欄位: patient_id, age, bmi, bp_category, recommended_calories, etc.")
