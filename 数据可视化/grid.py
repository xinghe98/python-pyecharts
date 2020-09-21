import pandas as pd
import xlrd
import pyecharts.options as opts
from pyecharts.charts import Radar,Bar,Grid,Line,Timeline,HeatMap,Page,Scatter,Funnel,Sunburst

# 雷达图
def randar():
    df = pd.read_csv('./randar.csv')
    data = df.groupby('渠道').size()
    id = data.index.tolist()
    value = data.tolist()
    v1 = [value]
    randar = Radar()
    schem=[]
    for i,j in zip(id,value):
        a = dict(name="{}".format(i),max="{}".format(20))# max_的值根据实际情况定义
        schem.append(a)
    randar.add_schema(schema=schem,splitarea_opt=dict(is_show=True,)).add("",
            data=v1,
            linestyle_opts=opts.LineStyleOpts(color="green"),
        ).set_series_opts(label_opts=opts.LabelOpts(is_show=False)).set_global_opts(
            title_opts=opts.TitleOpts(title="各渠道来源"), legend_opts=opts.LegendOpts()
        )
    return randar


# 柱状图
def bar():
    df = pd.read_excel('./bar.xlsx').set_index('时间')
    t = Timeline()
    for i,j in zip(range(len(df.index.to_list())),df.index.to_list()):
        bar = Bar()
        bar.add_xaxis(df.columns.to_list()).add_yaxis('',df.iloc[i].tolist(),category_gap="70%").reversal_axis()
        bar.set_global_opts(toolbox_opts=opts.ToolboxOpts(is_show=True),title_opts=opts.TitleOpts(title='每日数据总览'))
        t.add(bar,'{}'.format(j))
    return t

# 热力图
def heat():
    df = pd.read_csv('./heat.csv')
    df["注册时间"] = pd.to_datetime(df["注册时间"])
    week = df["注册时间"].dt.weekday #转成周几
    time = df["注册时间"].dt.hour # 转成小时
    bp = pd.DataFrame({'week':week.tolist(),'time':time.tolist()}) #按周几和时间重建DataFrame
    data = pd.DataFrame({'count' : bp.groupby( ['week','time'] ).size()}).reset_index() # 统计每天不同时间点注册人数
    new_data = pd.DataFrame(index=[i for i in range(24)],columns=[i for i in range(7)]).fillna(0)# 新建空表，将已有数据填充进去，没有的则为0
    # print(data)
    for i,j,c in zip(data['time'].tolist(),data['week'].tolist(),data['count'].tolist()):
        new_data.iloc[i,j]=c# 有数据的定位修改数值
    # print(new_data)
    values = [[i, j, int(new_data.iloc[i, j])] for i in range(24) for j in range(7)]# 将完整数据表转为坐标形式
    value = values
    days = ["Saturday", "Friday", "Thursday", "Wednesday", "Tuesday", "Monday", "Sunday"]
    heatmap = HeatMap().add_xaxis([str(i) for i in range(24)]).add_yaxis(
        "不同时间段注册人数",
        [x for x in days],value,
        label_opts=opts.LabelOpts(is_show=True, position="inside")
    ).set_global_opts(title_opts=opts.TitleOpts(title="时间点注册热力图"),
                      visualmap_opts=opts.VisualMapOpts())# 注意：这里为24小时制，具体看情况
    return heatmap


# 折线图
def line():
    df = pd.read_excel('./line.xlsx')
    date = df['时间'].tolist()
    order = df['订单数量'].tolist()
    conust = df['社群数量'].tolist()
    line = Line().add_xaxis(xaxis_data=date).add_yaxis(
            series_name="订单数量",
            label_opts=opts.LabelOpts(margin=25),
            y_axis=order,
            markpoint_opts=opts.MarkPointOpts(
                data=[
                    opts.MarkPointItem(type_="max", name="最大值"),
                    opts.MarkPointItem(type_="min", name="最小值"),
                ]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[opts.MarkLineItem(type_="average", name="平均值")]
            ),
        ).add_yaxis(
            series_name="社群数量",
            label_opts=opts.LabelOpts(margin=19),
            y_axis=conust,
            markpoint_opts=opts.MarkPointOpts(
                data=[opts.MarkPointItem(value=-2, name="周最低", x=1, y=-1.5)]
            ),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                    opts.MarkLineItem(symbol="none", x="90%", y="max"),
                    opts.MarkLineItem(symbol="circle", type_="max", name="最高点"),
                ]
            ),
        ).set_global_opts(
            title_opts=opts.TitleOpts(title="首周数据统计"),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),

        )
    return line


#散点图
def scatter():
    scatter = Scatter()
    data = pd.DataFrame({'count':0},index=['朋友圈','公众号','今日头条/抖音','其他','知乎','b站'])
    scatter.add_xaxis(data.index.tolist()).set_global_opts(
            title_opts=opts.TitleOpts(title="不同时间渠道来源主要分布"),
            visualmap_opts=opts.VisualMapOpts(type_="size", max_=20, min_=0),
        )
    df = pd.read_csv('./randar.csv')
    df['提交时间']=pd.to_datetime(df['提交时间']).dt.day
    time_list = df['提交时间'].sort_values().unique().tolist()
    grouped = df.groupby(['提交时间'])
    for k in time_list:
        con = grouped.get_group(k)['渠道'].value_counts()
        data = pd.DataFrame({'count':0},index=['朋友圈','公众号','今日头条/抖音','其他','知乎','b站'])
        scatter.add_xaxis(data.index.tolist())
        value_list = list(zip(con.index.tolist(),con.values.tolist()))
        for i in value_list:
            x,j = i
            data.loc[x,'count'] = j
            scatter.add_yaxis(str(k),data['count'])
    return scatter


#旭日图
def sunburst():
    df = pd.read_csv('./randar.csv')
    df['提交时间']=pd.to_datetime(df['提交时间']).dt.day
    time = df.groupby('提交时间')
    child = []
    data = []
    for i in time.size().index.tolist():
        k = time.get_group(i)["渠道"].value_counts()
        x = list(zip(k.index.tolist(),k.values.tolist()))
        for t in x:
            name,value = t
            dict = {"name":name,"value": value}
            child.append(dict)
        data_list = {'name':str(i)+"日",'children':child}
        child = []
        data.append(data_list)
    sunburst = Sunburst(init_opts=opts.InitOpts(width="1000px", height="600px"))
    sunburst.add(series_name="", data_pair=data, radius=[0, "90%"],highlight_policy="ancestor",sort_="null",levels=[
                {},
                {
                    "r0": "15%",
                    "r": "35%",
                    "itemStyle": {"borderWidth": 2},
                    "label": {"rotate": "tangential"},
                },
                {"r0": "35%", "r": "70%", "label": {"align": "right"}},
                {
                    "r0": "70%",
                    "r": "72%",
                    "label": {"position": "outside", "padding": 3, "silent": False},
                    "itemStyle": {"borderWidth": 3},
                },
            ],).set_global_opts(title_opts=opts.TitleOpts(title="每天各渠道占比")).set_series_opts(label_opts=opts.LabelOpts(formatter="{b}"))
    return sunburst


# 漏斗图
def funnel():
    df = pd.read_excel('./funnel.xlsx')
    data1=list(df['项目'].tolist())
    data2=list(df['数量'].tolist())
    data = list(zip(data1,data2))
    funnel = Funnel()
    funnel.set_colors(colors=['#28be32','#00FFFF','#FFA500','#836FFF'])
    funnel.add('内容',data,label_opts=opts.LabelOpts(formatter='{b} {d}%'))
    funnel.set_global_opts(title_opts=opts.TitleOpts(title="转化漏斗模型(总体转化率)"))
    return funnel

# 和并图(自定义布局）
# Radar,Bar,Grid,Line,Timeline,HeatMap
# page = Page(layout=Page.DraggablePageLayout)
# page.add(bar(),randar(),line(),heat(),scatter(),funnel(),sunburst())
# page.render()
Page.save_resize_html("render.html", cfg_file=r"C:\Users\Hello\Downloads\chart_config (2).json", dest="my_new_charts.html")# 生成自定义布局


