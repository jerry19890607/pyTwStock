import datetime
import argparse

#Local lib
import crawl

# EPS, ROE, 股東持股比例
def main():
    parser = argparse.ArgumentParser(description='Crawl data at different way')
    parser.add_argument('day', type=int, nargs='*',
                        help='Crawl tw stock after hour info (format: YYYY MM DD), default is today')
    parser.add_argument('-afterHours', '--a', type=int, nargs='*',
                        help='Crawl tw stock after hour info (format: [TWStockNumber] YYYY MM DD), default is today')
    parser.add_argument('-closeInfo', '--c', type=int, nargs='*',
                        help='Crawl tw stock daily close info (format: YYYY MM DD), default is today')
    parser.add_argument('-financial', '--f', type=int, nargs='*',
                        help='Crawl tw stock 營業收入資訊 (format: YYYY MM DD), default is today')

    time = datetime.datetime.now()
    print("更新時間:" + str(time.hour)+":"+str(time.minute))

    args = parser.parse_args()
    print('[DBG] ' + str(args))
    print('')

    # Ex: python3.7 daily.py --a 2330 20200922
    #     python3.7 daily.py --a 20200922
    if args.a:
        if len(args.a) == 1:
            SearchNum = None
            first_day = datetime.datetime.strptime(str(args.a[0]), '%Y%m%d')
            first_day = first_day.strftime("%Y%m%d")
        elif len(args.a) == 2:
            SearchNum = args.a[0]
            first_day = datetime.datetime.strptime(str(args.a[1]), '%Y%m%d')
            first_day = first_day.strftime("%Y%m%d")
        else:
            pass
            return

        #print(SearchNum)
        #print(first_day)
        results = crawl.crawl_after_hours(SearchNum, first_day)

    # Ex: python3.7 daily.py --c 20200922 2330
    #     python3.7 daily.py --c 20200922 (Default list)
    elif args.c:
        if len(args.c) == 1:
            stockNum = None
            first_day = datetime.datetime.strptime(str(args.c[0]), '%Y%m%d')
            first_day = first_day.strftime("%Y%m%d")
        elif len(args.c) >= 2:
            stockNum = args.c[1:]
            first_day = datetime.datetime.strptime(str(args.c[0]), '%Y%m%d')
            first_day = first_day.strftime("%Y%m%d")
        else:
            pass
            return

        #print(stockNum)
        #print(first_day)
        results = crawl.stock_crawler(stockNum, first_day)

    # Ex: python3.7 daily.py --f 2020 2 1
    #     python3.7 daily.py --f 2020 2 2
    #     python3.7 daily.py --f 2020 2 3
    #     python3.7 daily.py --f 2020 2 3 (stockNum)
    #     python3.7 daily.py --f 2020 2 4 stockNum
    elif args.f:
        if len(args.f) == 3:
            year = args.f[0]
            season = args.f[1]
            typeNum = args.f[2]
            stockNum = None
        if len(args.f) == 4:
            year = args.f[0]
            season = args.f[1]
            typeNum = args.f[2]
            stockNum = args.f[3]

        results = crawl.financial_statement(year, season, typeNum, stockNum)

    else:
        parser.error('Date should be assigned with (YYYY MM DD) or none')
        return

    if results.empty:
        print('Data incorrect')
    else:
        print(results)

if __name__ == '__main__':
    main()
