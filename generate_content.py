from datetime import timedelta
import os
import pandas as pd
import config as conf

class ContentGenerator:
    def __init__(self):
        self.order_table = pd.DataFrame()

    def _get_produce_qty(self, demand_date, order_type, produce_prefix):
        _order_table = self.order_table
        demand_date = str(demand_date)
        # 這裡不論NEW_SCHEDULE_DATE是多少，都會計算在內。以後如果會有多期別的purchase order，需要再更新
        _order_table = _order_table[(_order_table[conf.DEMAND_DATE] == demand_date)&(_order_table[conf.DEMAND_TYPE] == order_type)&(_order_table[conf.ASSEMBLY_ITEM_NUMBER].str.startswith(produce_prefix))]
        return f"{round(_order_table[conf.ASSEMBLY_ITEN_QTY].sum()):,}"

    def _write_produce_qty(self, demand_date, order_type, produce_prefix):
        content = "\t\t\t\t" + order_type + "的齊套數為" + self._get_produce_qty(demand_date, order_type, produce_prefix) + "\n"
        return content

    def _write_each_data(self, data_name):
        content = "\t" + data_name + ":\n\n"
        data_path = conf.RESULT_PATH + "\\" + data_name

        # 找出order_table的檔案名稱，如果沒有就報錯
        all_file_name = os.listdir(data_path)
        order_table_name = ""
        for file_name in all_file_name:
            if file_name.startswith(conf.ORDER_TABLE_PREFIX):
                order_table_name = file_name
        if order_table_name == "":
            raise Exception("order_table not found.")
        
        self.order_table = pd.read_csv(data_path + "\\" + order_table_name)
        #處理期別
        self.order_table[conf.NEW_SCHEDULE_DATE] = pd.to_datetime(self.order_table[conf.NEW_SCHEDULE_DATE], errors='coerce')
        self.order_table = self.order_table.dropna(subset=[conf.NEW_SCHEDULE_DATE])
        self.order_table[conf.DEMAND_DATE] = pd.to_datetime(self.order_table[conf.DEMAND_DATE])
        first_date = min(self.order_table[conf.DEMAND_DATE])
        last_date = max(self.order_table[conf.DEMAND_DATE])


        # 記錄特定prefix的成品
        for produce_prefix in ["", "60MB"]:
            if produce_prefix == "":
                content = content + "\t\t如果考慮全部成品:\n"
            else:
                content = content + "\t\t如果只考慮" + produce_prefix + "的成品:\n"
            date = first_date
            while date <= last_date:
                content = content + "\t\t\tDemand Date 為"+ str(date) + "時的單:\n"
                for order_type in ["WORK ORDER DEMAND", "FORECAST"]:
                    content = content + self._write_produce_qty(date, order_type, produce_prefix)
                date = date + timedelta(days=7)

            content = content + "\n"
        content = content + "\n"
        return content
    

    # def _save_all_data_folder(self):
    #     "記錄所有資料的資料夾名稱"
    #     all_file_name = os.listdir(conf.RESULT_PATH)
    #     return all_file_name
        
    def get_mail_content(self):
        content = "Hi Ivy:\n附件為此次資料結果:\n\n"

        # 紀錄所有資料的名稱
        all_file_name = os.listdir(conf.RESULT_PATH)
        for data_name in all_file_name:
            content = content + self._write_each_data(data_name)

        content = content + "Best Regards,\nJohnny Ma"
        return content


if __name__ == '__main__':
    content_generator = ContentGenerator()
    content = content_generator.get_mail_content()
    print(content)