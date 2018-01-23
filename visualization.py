# coding: utf-8
from __future__ import print_function,unicode_literals

import time
import datetime
start=time.time()

import pandas as pd
from pandas import DataFrame
import pyhs2
import os


data_range = pd.date_range('2016-01-01','2017-12-31')
df = DataFrame(data_range,columns=['date']).set_index('date')
df['date'] = data_range
start_date = df.asfreq('QS')
end_date = df.asfreq('Q')


sql_code="""
select 
a.busi_type,count(distinct a.user_id) Repurchase
from 
	(select 
	busi_type,user_id,max(gmt_created_time) order_time
	from wedw_dm.weiyi_orders_ful
	where gmt_created_date between '{sd}' and '{ed}'
	and busi_type in ('问诊')
	and actual_amt>0
	group by busi_type,user_id) as a
inner join 
	(select 
	user_id,count(distinct order_id) num,min(gmt_created_time) ever_time
	from wedw_dm.weiyi_orders_ful
	where busi_type in ('问诊')
	and actual_amt>0
	group by user_id) as b 
	on a.user_id=b.user_id
	and b.num>=2
where a.order_time > b.ever_time
group by a.busi_type
""".encode('utf-8')

con = pyhs2.connect(host='10.20.180.190', port=10098, authMechanism="PLAIN",
                    user='tangyao1', password='wy!1118ty', database='wedw_yydm')

for i in range(len(start_date)):
    sd = str(start_date.iloc[i,0].date()).encode('utf-8')
    ed = str(end_date.iloc[i,0].date()).encode('utf-8')
    run_code = sql_code.format(sd=sd,ed=ed)

    cur = con.cursor()
    cur.execute('SET mapreduce.job.queuename=root.yydata')
    cur.execute(run_code)
    column_names = [x['columnName'] for x in cur.getSchema()]
    result = DataFrame(cur.fetchall(), columns=column_names)
    result.set_index(result.columns[0], inplace=True)
    print (sd+'~'+ed)
    print (result,'\n')



end=time.time()
print ( '运行时间:\n',datetime.timedelta(seconds=round(end-start)) )