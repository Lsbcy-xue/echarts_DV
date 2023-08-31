from django.core.exceptions import ObjectDoesNotExist
from django_echarts.starter.sites import DJESite, SiteOpts
from pyecharts.charts import Bar, Line, Gauge, Bar3D, Map, Tree, Sunburst, TreeMap
from charts.models import Gini, RegionData, IncomeData
from pyecharts.charts import Timeline, Pie
from django_echarts.stores.entity_factory import factory
from pyecharts import options as opts
from django_echarts.entities import (
    Copyright, ValuesPanel, ValueItem, NamedCharts, WidgetCollection,
    bootstrap_table_class, RowContainer
)
from .description import *

# 创建一个DJESite对象，用于网站的配置和管理
site_obj = DJESite(
    site_title='国民人均可支配收入可视化',  # 网站的标题
    opts=SiteOpts(
        list_layout='grid',  # 列表布局设置为网格形式
        nav_shown_pages=[  # 在导航栏显示的页面
            'home',
            'collection',
            'list',
            'chart_nav'
        ],
        paginate_by=10  # 每页显示10个项目
    )
)

# 添加一些小部件到网站
site_obj.add_widgets(
    copyright_=Copyright(start_year=2014, powered_by='Lc'),  # 版权信息
    jumbotron_chart='Income_classify_pie',  # 大背景图表设置为"Income_classify_pie"
    values_panel='home1_panel'  # 主页的值面板设置为"home1_panel"
)

# 导航栏配置
nav = {
    'nav_left': ['home', 'list', 'chart_nav'],  # 左侧导航栏包含的页面
    'nav_right': ['settings'],  # 右侧导航栏包含的页面
    'nav_footer': [  # 页脚导航栏
        {'text': '国家统计局', 'url': 'http://www.stats.gov.cn/sj/', 'new_page': True},  # 国家统计局的链接
        {'text': '网站源码', 'url': 'https://github.com/kinegratii/zinc', 'new_page': True}  # 网站源码的链接
    ]
}

# 使用config_nav方法来配置导航栏
site_obj.config_nav(nav_config=nav)

# 使用site_obj对象注册一个图表
@site_obj.register_chart(
    name="deposit_income_per_person",  # 定义图表的名称
    title="居民人均可支配收入",  # 定义图表的标题
    description=DEPOSIT_INCOME_PER_PERSON_DESCRIPTION,  # 定义图表的描述
    catalog="1",  # 定义图表的分类目录
    top=0,  # 定义图表的排序优先级
)
def bar01():  # 定义一个函数用于生成图表
    # 从Gini模型中获取所有对象，存储为查询集
    data = Gini.objects.all()

    # 检查查询集是否有数据
    if data.exists():
        # 从查询集中提取x轴数据（年-季度）
        x_data = [item.year_quarter for item in data]
        # 从查询集中提取各种y轴数据
        y1_data = [item.wage_income_growth for item in data]
        y2_data = [item.business_income_growth for item in data]
        y3_data = [item.property_income_growth for item in data]
        y4_data = [item.transfer_income_growth for item in data]
        y5_data = [item.disposable_income_growth for item in data]  # 假设Gini模型中该数据的字段名

        # 创建柱状图实例
        bar = (
            Bar()
            .add_xaxis(xaxis_data=x_data)  # 添加x轴数据
            .add_yaxis(series_name="居民人均可支配工资性收入_累计增长", y_axis=y1_data,
                       label_opts=opts.LabelOpts(is_show=False))  # 添加第一个y轴数据
            .add_yaxis(series_name="居民人均可支配经营净收入_累计增长", y_axis=y2_data,
                       label_opts=opts.LabelOpts(is_show=False))  # 添加第二个y轴数据
            .add_yaxis(series_name="居民人均可支配财产净收入_累计增长", y_axis=y3_data,
                       label_opts=opts.LabelOpts(is_show=False))  # 添加第三个y轴数据
            .add_yaxis(series_name="居民人均可支配转移净收入_累计增长", y_axis=y4_data,
                       label_opts=opts.LabelOpts(is_show=False))  # 添加第四个y轴数据
            .extend_axis(  # 扩展额外的y轴
                yaxis=opts.AxisOpts(
                    type_="value",  # 定义y轴类型
                    name="增长率",  # 定义y轴名称
                    min_=-10,  # 定义y轴最小值
                    max_=20,  # 定义y轴最大值
                    interval=1,  # 定义y轴间隔
                    position="right",  # 定义y轴位置
                    axislabel_opts=opts.LabelOpts(formatter="{value}%"),  # 定义y轴标签格式
                )
            )
            .set_global_opts(  # 设置全局选项
                title_opts=opts.TitleOpts(
                    title="Disposable income national",  # 主标题
                    subtitle="数据来自相关统计局",  # 副标题
                    pos_left="center"  # 标题位置
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),  # 提示框选项
                toolbox_opts=opts.ToolboxOpts(is_show=True, orient="vertical", pos_left="left", pos_top="center"),  # 工具箱选项
                legend_opts=opts.LegendOpts(pos_bottom="-1%")  # 图例选项
            )
        )

        # 创建折线图实例
        line = (
            Line()
            .add_xaxis(xaxis_data=x_data)  # 添加x轴数据
            .add_yaxis(
                series_name="居民人均可支配收入_累计增长",  # 系列名称
                yaxis_index=1,  # y轴索引
                y_axis=y5_data,  # y轴数据
                label_opts=opts.LabelOpts(is_show=False),  # 标签选项
            )
        )

        # 将柱状图和折线图结合在一起
        return bar.overlap(line)
    else:
        # 如果没有查询到数据，则打印消息
        print("没有查询到数据")


# 定义一个函数用于创建仪表盘图表
def create_gauge(year, gini_value):
    # 创建仪表盘图表实例
    gauge = (
        Gauge()  # 初始化仪表盘图表
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{year}年居民人均可支配收入基尼系数"))  # 设置全局标题选项
        .add(
            series_name="",  # 系列名称为空
            data_pair=[("基尼系数", format(gini_value, '.3f'))],  # 添加数据对
            min_=0.46,  # 设置最小值
            max_=0.47,  # 设置最大值
            detail_label_opts=opts.GaugeDetailOpts(  # 设置详细标签选项
                offset_center=[0, "10%"],  # 设置标签的位置
                font_size=16,  # 设置字体大小
                color="#2ecc71"  # 设置字体颜色
            )
        )
        .set_series_opts(
            pointer_opts=opts.GaugePointerOpts(  # 设置指针选项
                width=8,  # 设置指针宽度
            )
        )
    )
    return gauge  # 返回创建好的仪表盘图表实例


# 使用装饰器注册图表，设置图表的基本属性
@site_obj.register_chart(
    name="gini",  # 图表名称
    title="居民人均可支配收入基尼系数",  # 图表标题
    description=GINI,  # 图表描述
    catalog="1",  # 图表分类
    top=1,  # 图表排名
)
# 定义一个函数用于创建时间轴仪表盘图表
def create_gini_timeline():
    years = range(2014, 2022)  # 设置年份范围
    # 初始化时间轴图表，设置图表尺寸
    timeline_gauge = Timeline(init_opts=opts.InitOpts(width="1000px", height="600px"))

    # 遍历每一个年份
    for year in years:
        # 从Gini模型中获取当前年份的数据
        data = Gini.objects.filter(year_quarter__startswith=f"{year}").values_list("year_quarter", "gini_coefficient")

        # 提取基尼系数数据
        year_data = [item[1] for item in data if item[0].startswith(str(year))]

        # 如果有数据，则添加到时间轴图表中
        if year_data:
            timeline_gauge.add(create_gauge(year, year_data[0]), time_point=str(year))

    # 设置时间轴播放间隔
    timeline_gauge.add_schema(play_interval=1000)

    return timeline_gauge  # 返回创建好的时间轴图表实例

# 使用装饰器注册图表，设置图表的基本属性
@site_obj.register_chart(
    name="Income_classify_pie",  # 图表名称
    title="居民人均可支配收入的分类收入情况（饼图）",  # 图表标题
    description=INCOME_CLASSIFY_PIE_DESCRIPTION,  # 图表描述
    catalog="2",  # 图表分类
    top=2,  # 图表排名
)
def generate_Chart2():  # 定义一个函数用于生成饼图
    def fetch_data_from_model():  # 内部函数，用于从IncomeData模型中获取数据
        queryset = IncomeData.objects.values(  # 查询数据库
            'year_quarter',  # 年和季度
            'total_income',  # 总收入
            'wage_income',  # 工资收入
            'business_income',  # 经营收入
            'property_income',  # 财产收入
            'transfer_income'  # 转移收入
        )
        data = {}  # 初始化一个空字典用于存储数据
        for entry in queryset:  # 遍历查询结果
            year_quarter = entry['year_quarter']  # 获取年和季度
            # 整理数据并存储到字典中
            data[year_quarter] = [
                {"name": key, "value": value}
                for key, value in entry.items() if key != 'year_quarter'
            ]
        return data  # 返回整理好的数据

    def get_year_quarter_pie_chart(year_quarter: str):  # 内部函数，用于生成特定年份和季度的饼图
        year_quarter_data = total_data[year_quarter]  # 获取特定年份和季度的数据
        names = [x["name"] for x in year_quarter_data]  # 提取名称
        values = [x["value"] for x in year_quarter_data]  # 提取值

        # 创建饼图
        pie = (
            Pie()
            .add(
                series_name="",  # 系列名称
                data_pair=[list(z) for z in zip(names, values)],  # 数据对
                radius=["20%", "40%"],  # 饼图半径
                label_opts=opts.LabelOpts(  # 标签选项
                    position="outside",  # 标签位置
                    formatter="{b}: {c}"  # 标签格式
                )
            )
            .set_global_opts(  # 设置全局选项
                title_opts=opts.TitleOpts(  # 标题选项
                    title="Total residents' pension disposable income",  # 主标题
                    subtitle="数据来自相关统计局",  # 副标题
                    pos_left="center"  # 标题位置
                ),
                legend_opts=opts.LegendOpts(  # 图例选项
                    type_="scroll",  # 图例类型
                    pos_left="75%",  # 图例位置
                    orient="vertical",  # 图例方向
                    pos_top="10%"  # 图例顶部位置
                )
            )
        )
        return pie  # 返回创建好的饼图实例

    # 从数据库模型中获取数据
    total_data = fetch_data_from_model()

    # 创建一个时间轴实例，设置其宽度和高度
    timeline_pie = Timeline(init_opts=opts.InitOpts(width="1000px", height="600px"))

    # 遍历所有年份和季度，为每一个生成一个饼图
    for year_quarter in sorted(total_data.keys()):
        # 调用函数生成特定年季度的饼图
        pie = get_year_quarter_pie_chart(year_quarter)
        # 将生成的饼图添加到时间轴中
        timeline_pie.add(pie, time_point=year_quarter)

    # 设置时间轴的属性
    timeline_pie.add_schema(
        is_auto_play=True,  # 是否自动播放
        play_interval=1000,  # 播放间隔（毫秒）
        orient="horizontal",  # 时间轴方向
        pos_left="10",  # 左侧位置
        pos_right="10",  # 右侧位置
        pos_bottom="10",  # 底部位置
    )

    # 返回完成的时间轴饼图实例
    return timeline_pie


# 从Django模型中获取数据并进行格式化
def fetch_data_from_model():
    # 使用Django的ORM从IncomeData模型中获取所需字段的值
    queryset = IncomeData.objects.values(
        'year_quarter',
        'total_income',
        'wage_income',
        'business_income',
        'property_income',
        'transfer_income'
    )

    # 初始化一个空列表用于存储格式化后的数据
    data = []
    # 遍历查询集中的每一个条目
    for entry in queryset:
        # 创建一个列表，包含该条目的所有字段值
        row = [
            entry['year_quarter'],  # 年份和季度
            entry['total_income'],  # 总收入
            entry['wage_income'],  # 工资收入
            entry['business_income'],  # 经营收入
            entry['property_income'],  # 财产收入
            entry['transfer_income']  # 转移收入
        ]
        # 将这一行数据添加到总数据列表中
        data.append(row)
    # 返回格式化后的数据列表
    return data


# 使用site_obj注册一个名为"Income_classify"的图表
@site_obj.register_chart(
    name="Income_classify",  # 图表名称
    title="居民人均可支配收入的分类收入情况（柱状图，折线图）",  # 图表标题
    description=INCOME_CLASSIFY,  # 图表描述
    catalog="3",  # 分类编号
    top=3,  # 优先级
)
def bar_01():  # 定义图表函数
    data = fetch_data_from_model()  # 从模型中获取数据
    if len(data) > 0:  # 检查是否有数据
        x_data = [item[0] for item in data]  # 获取x轴数据
        y1_data = [float(item[2]) for item in data]  # 获取y1轴数据
        y2_data = [float(item[3]) for item in data]  # 获取y2轴数据
        y3_data = [float(item[4]) for item in data]  # 获取y3轴数据
        y4_data = [float(item[5]) for item in data]  # 获取y4轴数据

        # 创建柱状图
        bar = (
            Bar()  # 初始化柱状图
            .add_xaxis(xaxis_data=x_data)  # 添加x轴数据
            .add_yaxis(series_name="居民人均可支配工资性收入_累计值", y_axis=y1_data,  # 添加y1轴数据
                       label_opts=opts.LabelOpts(is_show=False))  # 设置标签选项
            .add_yaxis(series_name="居民人均可支配经营净收入_累计值", y_axis=y2_data,  # 添加y2轴数据
                       label_opts=opts.LabelOpts(is_show=False))  # 设置标签选项
            .add_yaxis(series_name="居民人均可支配财产净收入_累计值", y_axis=y3_data,  # 添加y3轴数据
                       label_opts=opts.LabelOpts(is_show=False))  # 设置标签选项
            .add_yaxis(series_name="居民人均可支配转移净收入_累计值", y_axis=y4_data,  # 添加y4轴数据
                       label_opts=opts.LabelOpts(is_show=False))  # 设置标签选项
            .extend_axis(  # 扩展轴选项
                yaxis=opts.AxisOpts(  # y轴选项
                    name="元",  # 单位名称
                    type_="value",  # 类型为数值
                    min_=0,  # 最小值
                    max_=40000,  # 最大值
                    interval=5000,  # 间隔
                    axislabel_opts=opts.LabelOpts(formatter="{value}￥"),  # 标签格式
                )
            )
            .set_global_opts(  # 设置全局选项
                title_opts=opts.TitleOpts(title="Disposable income national", subtitle="数据来自相关统计局",  # 标题和副标题
                                          pos_left="center"),  # 标题位置
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),  # 提示框选项
                toolbox_opts=opts.ToolboxOpts(is_show=True, orient="vertical", pos_left="left",  # 工具箱选项
                                              pos_top="center"),
                legend_opts=opts.LegendOpts(pos_bottom="-1%")  # 图例选项
            )
        )

        # 创建折线图
        line = (
            Line()  # 初始化折线图
            .add_xaxis(xaxis_data=x_data)  # 添加x轴数据
            .add_yaxis(  # 添加y轴数据
                series_name="居民人均可支配收入_累计值",  # 系列名称
                yaxis_index=1,  # y轴索引
                y_axis=[float(item[1]) for item in data],  # y轴数据
                label_opts=opts.LabelOpts(is_show=False),  # 标签选项
            )
        )

        return bar.overlap(line)  # 将柱状图和折线图合并
    else:
        print("没有查询到数据")  # 如果没有数据，则打印此消息


# 使用site_obj注册一个名为"Income_classify_3D"的图表
@site_obj.register_chart(
    name="Income_classify_3D",  # 图表名称
    title="居民人均可支配收入的分类收入情况（3D柱状图）",  # 图表标题
    description=INCOME_CLASSIFY_3D,  # 图表描述
    catalog="2",  # 分类编号
    top=2  # 优先级
)
def generate_Chart4():  # 定义图表函数
    try:  # 尝试执行以下代码
        # 使用Django QuerySet API获取数据，并按年季度排序
        income_data_objects = IncomeData.objects.all().order_by('year_quarter')

        # 提取各个字段的数据
        years_quarters = [obj.year_quarter for obj in income_data_objects]  # 年和季度
        income_wage = [obj.wage_income for obj in income_data_objects]  # 工资收入
        income_business = [obj.business_income for obj in income_data_objects]  # 经营收入
        income_property = [obj.property_income for obj in income_data_objects]  # 财产收入
        income_transfer = [obj.transfer_income for obj in income_data_objects]  # 转移收入

        # 生成3D柱状图所需的数据
        def generate_data():  # 定义数据生成函数
            data = []  # 初始化数据列表
            for i, yq in enumerate(years_quarters):  # 遍历年和季度
                stack_value = 0  # 初始化堆叠值
                for j, income_type in enumerate([income_wage, income_business, income_property, income_transfer]):  # 遍历各类型收入
                    stack_value += income_type[i]  # 累加收入
                    data.append([i, j, stack_value])  # 添加数据点
                # 添加总收入项
                data.append([i, 4, stack_value])  # 4是新的“总收入”项的y轴索引
            return data  # 返回生成的数据

        # 初始化3D柱状图
        bar3d = Bar3D()

        # 添加数据和设置选项
        bar3d.add(
            "",  # 系列名称（空）
            generate_data(),  # 生成的数据
            shading="lambert",  # 阴影效果
            xaxis3d_opts=opts.Axis3DOpts(data=years_quarters, type_="category"),  # x轴选项
            yaxis3d_opts=opts.Axis3DOpts(data=["工资收入", "经营收入", "财产收入", "转移收入", "总收入"], type_="category"),  # y轴选项
            zaxis3d_opts=opts.Axis3DOpts(type_="value")  # z轴选项
        )

        # 设置全局选项
        bar3d.set_global_opts(title_opts=opts.TitleOpts(title="居民人均可支配收入3D柱状图", pos_left="center"))

        # 设置系列选项
        bar3d.set_series_opts(**{"stack": "stack"})  # 设置堆叠选项

        return bar3d  # 返回3D柱状图对象

    except ObjectDoesNotExist:  # 如果没有找到数据
        raise Exception("No data found for one or more quarters")  # 抛出异常


# 使用site_obj注册一个名为"Income_quarter"的图表
@site_obj.register_chart(
    name="Income_quarter",  # 图表名称
    title="居民人均可支配收入（按季节）",  # 图表标题
    description=INCOME_QUARTER_DESCRIPTION,  # 图表描述
    catalog="2",  # 分类编号
)
def generate_chart3():  # 定义图表函数
    try:  # 尝试执行以下代码
        # 使用Django QuerySet API获取数据，并按年季度排序
        income_data_objects = IncomeData.objects.all().order_by('year_quarter')

        # 提取各个字段的数据
        x_data = [obj.year_quarter for obj in income_data_objects]  # 年和季度
        y1_data = [obj.wage_income for obj in income_data_objects]  # 工资收入
        y2_data = [obj.business_income for obj in income_data_objects]  # 经营收入
        y3_data = [obj.property_income for obj in income_data_objects]  # 财产收入
        y4_data = [obj.transfer_income for obj in income_data_objects]  # 转移收入
        y_total_data = [obj.total_income for obj in income_data_objects]  # 总收入

        # 初始化柱状图
        bar = (
            Bar()
            .add_xaxis(xaxis_data=x_data)  # 添加x轴数据
            .add_yaxis("Wage Income", y1_data, label_opts=opts.LabelOpts(is_show=False))  # 添加工资收入数据
            .add_yaxis("Business Income", y2_data, label_opts=opts.LabelOpts(is_show=False))  # 添加经营收入数据
            .add_yaxis("Property Income", y3_data, label_opts=opts.LabelOpts(is_show=False))  # 添加财产收入数据
            .add_yaxis("Transfer Income", y4_data, label_opts=opts.LabelOpts(is_show=False))  # 添加转移收入数据
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Disposable Income National",  # 设置标题
                                          subtitle="Data sourced from relevant statistical bureau"),  # 设置副标题
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),  # 设置工具提示
                toolbox_opts=opts.ToolboxOpts(is_show=True),  # 显示工具箱
                legend_opts=opts.LegendOpts(pos_bottom="0%"),  # 设置图例位置
            )
        )

        # 初始化折线图
        line = (
            Line()
            .add_xaxis(xaxis_data=x_data)  # 添加x轴数据
            .add_yaxis("Total Income", y_total_data, label_opts=opts.LabelOpts(is_show=False))  # 添加总收入数据
        )

        return bar.overlap(line)  # 返回柱状图和折线图的重叠

    except ObjectDoesNotExist:  # 如果没有找到数据
        print("No data found for one or more quarters")  # 打印错误信息

# 使用site_obj注册一个名为"Income_province"的图表
@site_obj.register_chart(
    name="Income_province",  # 图表名称
    title="居民人均可支配收入（按省份）",  # 图表标题
    description=INCOME_PROVENCE_DESCRIPTION,  # 图表描述
    catalog="2",  # 分类编号
    top=0,  # 顶部位置
)
def generate_income_timeline():  # 定义图表生成函数
    # 从数据库获取数据并进行格式化
    def fetch_data_from_db():
        data = {}  # 初始化数据字典
        # 遍历年份范围（根据数据库数据进行调整）
        for year in range(2014, 2022):
            queryset = RegionData.objects.filter(year=year)  # 使用Django QuerySet API获取数据
            # 将数据存储为字典列表
            data[year] = [{"name": obj.region, "value": obj.metric_value} for obj in queryset]
        return data  # 返回数据

    # 总数据
    total_data = {}  # 初始化总数据字典
    total_data["dataIncome"] = fetch_data_from_db()  # 获取并存储收入数据

    # 创建时间轴对象
    timeline = Timeline(init_opts=opts.InitOpts(width="1000px", height="600px"))

    # 将地图添加到时间轴
    for y in range(2014, 2022):  # 调整年份范围以匹配数据
        sorted_year_data = total_data["dataIncome"][y]  # 获取排序后的年度数据
        names = [x["name"] for x in sorted_year_data]  # 获取地区名称
        values = [x["value"] for x in sorted_year_data]  # 获取地区值

        # 初始化地图对象
        map_ = (
            Map()
            .add(
                series_name="",  # 系列名称
                data_pair=[list(z) for z in zip(names, values)],  # 数据对
                maptype="china",  # 地图类型
                is_map_symbol_show=False,  # 是否显示地图标记
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="{}年全国各省份居民人均可支配收入".format(y),  # 设置标题
                                          subtitle="数据来自相关统计局"),  # 设置副标题
                visualmap_opts=opts.VisualMapOpts(
                    max_=100000,  # 最大值
                    is_piecewise=True,  # 是否分段显示
                    pieces=[
                        # 5000一个区间
                        {"min": 100000, "max": 1000000, "label": "100,000-1,000,000"},
                        {"min": 80000, "max": 100000, "label": "80,000-100,000"},
                        {"min": 75000, "max": 79999, "label": "75,000-79,999"},
                        {"min": 70000, "max": 74999, "label": "70,000-74,999"},
                        {"min": 65000, "max": 69999, "label": "65,000-69,999"},
                        {"min": 60000, "max": 64999, "label": "60,000-64,999"},
                        {"min": 55000, "max": 59999, "label": "55,000-59,999"},
                        {"min": 50000, "max": 54999, "label": "50,000-54,999"},
                        {"min": 45000, "max": 49999, "label": "45,000-49,999"},
                        {"min": 40000, "max": 44999, "label": "40,000-44,999"},
                        {"min": 35000, "max": 39999, "label": "35,000-39,999"},
                        {"min": 30000, "max": 34999, "label": "30,000-34,999"},
                        {"min": 25000, "max": 29999, "label": "25,000-29,999"},
                        {"min": 20000, "max": 24999, "label": "20,000-24,999"},
                        {"min": 15000, "max": 19999, "label": "15，000-19,999"},
                        {"min": 10000, "max": 14999, "label": "10,000-14,999"},
                        {"min": 5000, "max": 9999, "label": "5,000-9,999"},
                        {"min": 0, "max": 4999, "label": "0-4,999"}
                    ]
                ),
            )
        )
        timeline.add(map_, "{}年".format(y))  # 将地图添加到时间轴

    return timeline  # 返回时间轴对象

# 使用site_obj注册一个名为"Income_province_tree"的图表
@site_obj.register_chart(
    name="Income_province_tree",  # 图表名称
    title="居民人均可支配收入（按省份，树形图）",  # 图表标题
    description=INCOME_PROVENCE_TREE_DESCRIPTION,  # 图表描述
    catalog="2",  # 分类编号
    top=1,  # 顶部位置
)
def generate_tree_timeline():  # 定义生成树形时间轴的函数
    # 从数据库中使用RegionData模型获取数据
    def fetch_data_from_database(year):
        queryset = RegionData.objects.filter(year=year)
        return [
            {"name": obj.region, "value": obj.metric_value} for obj in queryset
        ]

    # 将数据转换为树形结构
    def convert_to_tree_structure(year_data, area_dict):
        tree_data = []
        for area, provinces in area_dict.items():
            children = []
            for item in year_data:
                # 去掉省份名称最后的“省”、“市”、“自治区”等
                short_name = (item["name"].replace("省", "").replace("市", "").replace("自治区", "")
                              .replace("壮族", "").replace("维吾尔", "").replace("回族", ""))
                if short_name in provinces:
                    children.append({"name": f"{item['name']} ({item['value']})"})
            tree_data.append({"name": area, "children": children})
        return [{"name": "全国", "children": tree_data}]

    # 大区字典（按照原代码）
    area_dict = {
        "华东": ["江苏", "浙江", "山东", "安徽", "江西", "福建", "上海"],
        "华南": ["广东", "广西", "海南"],
        "华中": ["湖北", "湖南", "河南"],
        "华北": ["山西", "河北", "内蒙古", "北京", "天津"],
        "东北": ["吉林", "辽宁", "黑龙江"],
        "西北": ["新疆", "陕西", "甘肃", "宁夏", "青海"],
        "西南": ["四川", "西藏", "贵州", "云南", "重庆"]
        # ...（其他大区）
    }

    # 创建时间轴对象
    timeline = Timeline(init_opts=opts.InitOpts(width="1200px", height="800px"))

    # 生成树并添加到时间轴
    for y in range(2014, 2022):  # 调整年份范围以匹配数据
        year_data = fetch_data_from_database(y)  # 获取该年的数据
        tree_data = convert_to_tree_structure(year_data, area_dict)  # 转换为树形结构

        # 初始化树形图
        tree = (
            Tree()
            .add("", tree_data, collapse_interval=2)  # 添加数据
            .set_global_opts(title_opts=opts.TitleOpts(title=f"Tree for Year {y}"))  # 设置标题
        )
        timeline.add(tree, f"{y}年")  # 将树形图添加到时间轴

    return timeline  # 返回时间轴对象


# 使用site_obj注册一个名为"Income_province_bar"的图表
@site_obj.register_chart(
    name="Income_province_bar",  # 图表名称
    title="居民人均可支配收入（按省份，柱形图）",  # 图表标题
    description=INCOME_PROVENCE_BAR_DESCRIPTION,  # 图表描述
    catalog="2",  # 分类编号
    top=1,  # 顶部位置
)
def generate_province_bar():  # 定义生成省份柱形图的函数
    # 从RegionData模型中获取数据并进行格式化
    def get_data_from_region_data():
        data = {}
        for year in range(2014, 2022):  # 根据你的数据调整年份范围
            year_data = RegionData.objects.filter(year=year)
            data[year] = [{"name": obj.region, "value": obj.metric_value} for obj in year_data]
        return data

    # 数据排序函数
    def format_year_data(year_data):
        sorted_data = sorted(year_data, key=lambda x: x['value'], reverse=True)
        return sorted_data

    # 主要代码部分
    total_data = {}  # 创建一个字典来存储数据
    total_data["dataIncome"] = get_data_from_region_data()  # 使用获取数据的函数获取并存储数据

    # 创建时间轴柱形图对象
    timeline_bar = Timeline(init_opts=opts.InitOpts(width="1000px", height="600px"))

    # 遍历年份生成柱形图
    for y in range(2014, 2022):  # 根据你的数据调整年份范围
        sorted_year_data = format_year_data(total_data["dataIncome"][y])  # 对数据进行排序
        names = [x["name"] for x in sorted_year_data]  # 获取省份名称
        values = [x["value"] for x in sorted_year_data]  # 获取人均可支配收入数据

        # 初始化柱形图对象
        bar = (
            Bar(init_opts=opts.InitOpts(width="1000px", height="600px"))  # 设置柱形图的初始化选项
            .add_xaxis(xaxis_data=names)  # 添加x轴数据
            .add_yaxis(
                series_name="人均可支配收入",
                y_axis=values,  # 添加y轴数据
                label_opts=opts.LabelOpts(is_show=False),  # 设置标签选项
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="{}全国及各省份居民人均可支配收入".format(y), subtitle="数据来自相关统计局"),  # 设置标题选项
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),  # 设置工具提示选项
                toolbox_opts=opts.ToolboxOpts(is_show=True, orient="vertical", pos_left="left", pos_top="center")  # 设置工具箱选项
            )
        )
        timeline_bar.add(bar, time_point=str(y))  # 将柱形图添加到时间轴

    return timeline_bar  # 返回时间轴柱形图对象


# 使用site_obj注册一个名为"Income_province_pie"的图表
@site_obj.register_chart(
    name="Income_province_pie",  # 图表名称
    title="居民人均可支配收入（按省份，饼图）",  # 图表标题
    description=INCOME_PROVENCE_PIE_DESCRIPTION,  # 图表描述
    catalog="2",  # 分类编号
    top=1,  # 顶部位置
)
def generate_province_pie():  # 定义生成省份饼图的函数
    def get_data_from_region_data():  # 从RegionData模型中获取数据并进行格式化的函数
        data = {}
        for year in range(2014, 2022):  # 根据你的数据调整年份范围
            year_data = RegionData.objects.filter(year=year)
            data[year] = [{"name": obj.region, "value": obj.metric_value} for obj in year_data]
        return data

    # 按地区汇总数据的函数
    def get_area_data(year_data):
        area_values = {key: 0 for key in area_dict.keys()}
        for item in year_data:
            for area, provinces in area_dict.items():
                if item["name"][:-1] in provinces:
                    area_values[area] += item["value"]
        return [{"name": area, "value": value} for area, value in area_values.items()]

    # 地区和省份的定义
    area_dict = {
        "华东": ["江苏", "浙江", "山东", "安徽", "江西", "福建", "上海"],
        "华南": ["广东", "广西", "海南"],
        "华中": ["湖北", "湖南", "河南"],
        "华北": ["山西", "河北", "内蒙古", "北京", "天津"],
        "东北": ["吉林", "辽宁", "黑龙江"],
        "西北": ["新疆", "陕西", "甘肃", "宁夏", "青海"],
        "西南": ["四川", "西藏", "贵州", "云南", "重庆"]
        # ...（其他大区）
    }

    # 主要代码部分
    total_data = {}  # 创建一个字典来存储数据
    total_data["dataIncome"] = get_data_from_region_data()  # 使用获取数据的函数获取并存储数据

    # 创建时间轴饼图对象
    timeline_pie = Timeline(init_opts=opts.InitOpts(width="1000px", height="600px"))

    # 遍历年份生成饼图
    for y in range(2014, 2022):
        sorted_year_data = get_area_data(total_data["dataIncome"][y])  # 获取按地区汇总的数据
        names = [x["name"] for x in sorted_year_data]  # 获取地区名称
        values = [x["value"] for x in sorted_year_data]  # 获取对应地区的收入数据

        # 创建饼图对象
        pie = (
            Pie()
            .add(
                series_name="",
                data_pair=[list(z) for z in zip(names, values)],
                radius=["20%", "40%"],  # 设置饼图半径范围
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="{}年按大区分类的收入分布".format(y)),  # 设置标题选项
            )
        )

        timeline_pie.add(pie, time_point=str(y))  # 将饼图添加到时间轴

    return timeline_pie  # 返回时间轴饼图对象


# 使用site_obj注册一个名为"Income_province_sunburst"的图表
@site_obj.register_chart(
    name="Income_province_sunburst",  # 图表名称
    title="居民人均可支配收入（按省份，旭日图）",  # 图表标题
    description=INCOME_PROVENCE_SUNBURST_DESCRIPTION,  # 图表描述
    catalog="2",  # 分类编号
    top=1,  # 顶部位置
)
def generate_province_sunburst():  # 定义生成省份旭日图的函数
    # 从 RegionData 模型中检索并格式化数据的函数
    def get_data_from_region_data():
        data = {}
        for year in range(2014, 2022):  # 根据你的数据范围调整年份
            year_data = RegionData.objects.filter(year=year)
            data[year] = [{"name": obj.region, "value": obj.metric_value} for obj in year_data]
        return data

    # 将数据转换为旭日图结构的函数
    def convert_to_sunburst_structure(year_data, area_dict):
        sunburst_data = []
        for area, provinces in area_dict.items():
            children = []
            for item in year_data:
                # 去掉省份名称最后的“省”、“市”、“自治区”等
                short_name = (item["name"].replace("省", "").replace("市", "").replace("自治区", "")
                              .replace("壮族", "").replace("维吾尔", "").replace("回族", ""))
                if short_name in provinces:
                    children.append({"name": f"{item['name']} ({item['value']})", "value": item['value']})
            sunburst_data.append({"name": area, "children": children})
        return sunburst_data

    # 地区和大区定义（与你的代码相同）
    area_dict = {
        "华东": ["江苏", "浙江", "山东", "安徽", "江西", "福建", "上海"],
        "华南": ["广东", "广西", "海南"],
        "华中": ["湖北", "湖南", "河南"],
        "华北": ["山西", "河北", "内蒙古", "北京", "天津"],
        "东北": ["吉林", "辽宁", "黑龙江"],
        "西北": ["新疆", "陕西", "甘肃", "宁夏", "青海"],
        "西南": ["四川", "西藏", "贵州", "云南", "重庆"]
    }

    # 主要代码部分
    total_data = get_data_from_region_data()  # 获取数据

    timeline = Timeline(init_opts=opts.InitOpts(width="1200px", height="800px"))  # 创建时间轴对象

    # 生成旭日图并添加到时间轴
    for y in range(2014, 2022):  # 根据你的数据范围调整年份
        year_data = total_data[y]  # 获取特定年份的数据
        sunburst_data = convert_to_sunburst_structure(year_data, area_dict)  # 转换为旭日图数据结构

        sunburst = (
            Sunburst(init_opts=opts.InitOpts(width="1000px", height="600px"))  # 创建旭日图对象
            .add(
                "",
                data_pair=sunburst_data,
                highlight_policy="ancestor",
                radius=[0, "95%"],
                sort_="null",
                levels=[
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
                ],
            )
            .set_global_opts(title_opts=opts.TitleOpts(title=f"Sunburst for Year {y}"))  # 设置标题选项
        )
        timeline.add(sunburst, f"{y}年")  # 将旭日图添加到时间轴

    return timeline  # 返回时间轴对象


# 使用site_obj注册一个名为"Income_province_treemap"的图表
@site_obj.register_chart(
    name="Income_province_treemap",  # 图表名称
    title="居民人均可支配收入（按省份，矩形树图）",  # 图表标题
    description=INCOME_PROVENCE_TREEMAP_DESCRIPTION,  # 图表描述
    catalog="2",  # 分类编号
    top=1,  # 顶部位置
)
def generate_province_treemap():  # 定义生成省份矩形树图的函数
    # 从 RegionData 模型中检索并格式化数据的函数
    def get_data_from_region_data():
        data = {}
        for year in range(2014, 2022):  # 根据你的数据范围调整年份
            year_data = RegionData.objects.filter(year=year)  # 从数据库获取特定年份的数据
            data[year] = [{"name": obj.region, "value": obj.metric_value} for obj in year_data]  # 格式化数据
        return data

    # 将数据转换为树状图结构的函数
    def convert_to_tree_map_structure(year_data, area_dict):
        tree_map_data = {"children": []}  # 创建树状图数据的字典
        for area, provinces in area_dict.items():
            children = []
            for item in year_data:
                # 去掉省份名称最后的“省”、“市”、“自治区”等
                short_name = (item["name"].replace("省", "").replace("市", "").replace("自治区", "")
                              .replace("壮族", "").replace("维吾尔", "").replace("回族", ""))
                if short_name in provinces:
                    children.append({"name": f"{item['name']} ({item['value']})", "value": item['value']})
            tree_map_data["children"].append({"name": area, "children": children})
        return tree_map_data

    # 地区和大区定义（与你的代码相同）
    area_dict = {
        "华东": ["江苏", "浙江", "山东", "安徽", "江西", "福建", "上海"],
        "华南": ["广东", "广西", "海南"],
        "华中": ["湖北", "湖南", "河南"],
        "华北": ["山西", "河北", "内蒙古", "北京", "天津"],
        "东北": ["吉林", "辽宁", "黑龙江"],
        "西北": ["新疆", "陕西", "甘肃", "宁夏", "青海"],
        "西南": ["四川", "西藏", "贵州", "云南", "重庆"]
    }

    # 主要代码部分
    total_data = get_data_from_region_data()  # 获取数据

    timeline = Timeline(init_opts=opts.InitOpts(width="1200px", height="800px"))  # 创建时间轴对象
    timeline.add_schema(pos_bottom="3%")  # 添加时间轴底部位置

    # 生成树状图并添加到时间轴
    for y in range(2014, 2022):  # 根据你的数据范围调整年份
        year_data = total_data[y]  # 获取特定年份的数据
        tree_map_data = convert_to_tree_map_structure(year_data, area_dict)  # 转换为树状图数据结构

        tree_map = (
            TreeMap(init_opts=opts.InitOpts(width="1200px", height="720px"))  # 创建矩形树图对象
            .add(
                series_name="全国",
                data=tree_map_data["children"],  # 设置数据
                visual_min=300,  # 设置可视化的最小值
                leaf_depth=1,  # 设置叶子节点的深度
                label_opts=opts.LabelOpts(position="inside"),  # 设置标签的位置
            )
            .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=False),  # 隐藏图例
                title_opts=opts.TitleOpts(
                    title=f"TreeMap for Year {y}",  # 设置标题
                    pos_top="5%",  # 设置标题位置
                    pos_left="center"
                )
            )
        )
        timeline.add(tree_map, f"{y}年")  # 将矩形树图添加到时间轴

    return timeline  # 返回时间轴对象



# Widget
# @site_obj.register_html_widget
# def this_month_panel():
#     today = date.today()
#     number_p = ValuesPanel()
#     access_total = models.AccessRecord.objects.filter(
#         create_time__year=today.year, create_time__month=today.month
#     ).count()
#     item = ValueItem(access_total, f'{today.year}年{today.month}月访问量', '人次')
#     number_p.add_widget(item)
#     return number_p


@site_obj.register_html_widget
def home1_panel():
    number_p = ValuesPanel()
    number_p.add(str(factory.chart_info_manager.count()), '图表总数', '个', catalog='danger')
    # number_p.add('42142', '网站访问量', '人次')
    number_p.add_widget(ValueItem('114514', '网站访问量', '人次'))
    number_p.add('78895', '国民人均可支配收入中位数', '元', catalog='info')
    number_p.add('5.5', 'GDP增速', '%', catalog='success')
    number_p.set_spans(6)
    return number_p





