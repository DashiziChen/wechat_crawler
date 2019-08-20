import xlrd
import json

def excel2json(filename):
    """
    转json
    :param filename: excel文件名
    :return: None
    """
    key = ["news_code", "news_title", "launch_time", "news_author", "news_content", "news_media", "news_url",
        "news_reads", "news_comments", "news_reposts", "news_likes", "news_org"]
    EXCEL_DATA = xlrd.open_workbook(filename)
    table = EXCEL_DATA.sheets()[0]
    COUNT_ROW = table.nrows
    COUNT_COL = table.ncols
    # 读取excel写入json文件
    arr_big = []
    for i in range(1, COUNT_ROW):
        dict_key_value = {}
        for j in range(0, COUNT_COL):
            each_key = key[j]
            each_value = str(table.cell(i, j).value)
            dict_key_value[each_key] = each_value
        arr_big.append(dict_key_value)
    json_string = json.dumps(arr_big, ensure_ascii=False)
    file_pra_txt = open(filename.replace('xlsx', 'json'), 'w', encoding='utf8')
    file_pra_txt.write(json_string)
    file_pra_txt.close()
    print('生成json文件成功!')


if __name__ == '__main__':
    # 源excel文件绝对路径
    PATH_TARGET_EXCEL = '公众号爬取1.xlsx'
    # 目标json文件路径，可以直接配置成工程中的路径，覆盖写入
    PATH_TARGET_JSONFILE = '微信公众号1.json'
