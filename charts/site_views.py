from django.core.exceptions import ObjectDoesNotExist
from django_echarts.starter.sites import DJESite, SiteOpts
from pyecharts.charts import Bar, Line, Gauge, Bar3D, Map, Tree
from charts.models import Gini, RegionData, IncomeData
from pyecharts.charts import Timeline, Pie
from django_echarts.stores.entity_factory import factory
from pyecharts import options as opts
from django_echarts.entities import (
    Copyright, ValuesPanel, ValueItem, NamedCharts, WidgetCollection,
    bootstrap_table_class, RowContainer
)
from .description import *


site_obj = DJESite(
    site_title='国民人均可支配收入可视化',
    opts=SiteOpts(
        list_layout='grid',
        nav_shown_pages=[
            'home',
            'collection',
            'list',
            'chart_nav'
        ],
        paginate_by=10
    )
)

site_obj.add_widgets(
    copyright_=Copyright(start_year=2014, powered_by='Lc'),
    jumbotron_chart='Income_classify_pie',
    values_panel='home1_panel'
)


# Navigation Configuration
nav = {
    'nav_left': ['home', 'list', 'chart_nav'],
    'nav_right': ['settings'],
    'nav_footer': [
        {'text': '国家统计局', 'url': 'http://www.stats.gov.cn/sj/', 'new_page': True},
        {'text': '网站源码', 'url': 'https://github.com/kinegratii/zinc', 'new_page': True},
    ]
}


site_obj.config_nav(nav_config=nav)


# Chart
@site_obj.register_chart(
    name="deposit_income_per_person",
    title="居民人均可支配收入",
    description=DEPOSIT_INCOME_PER_PERSON_DESCRIPTION,
    catalog="1",
    top=0,
)
def bar01():
    # Assuming the Gini model is already populated and data is fetched as a queryset
    data = Gini.objects.all()

    if data.exists():
        x_data = [item.year_quarter for item in data]
        y1_data = [item.wage_income_growth for item in data]
        y2_data = [item.business_income_growth for item in data]
        y3_data = [item.property_income_growth for item in data]
        y4_data = [item.transfer_income_growth for item in data]
        y5_data = [item.disposable_income_growth for item in
                   data]  # Assuming the field name for this data in Gini model

        bar = (
            Bar()
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(series_name="居民人均可支配工资性收入_累计增长", y_axis=y1_data,
                       label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis(series_name="居民人均可支配经营净收入_累计增长", y_axis=y2_data,
                       label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis(series_name="居民人均可支配财产净收入_累计增长", y_axis=y3_data,
                       label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis(series_name="居民人均可支配转移净收入_累计增长", y_axis=y4_data,
                       label_opts=opts.LabelOpts(is_show=False))
            .extend_axis(
                yaxis=opts.AxisOpts(
                    type_="value",
                    name="增长率",
                    min_=-10,
                    max_=20,
                    interval=1,
                    position="right",
                    axislabel_opts=opts.LabelOpts(formatter="{value}%"),
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Disposable income national",
                    subtitle="数据来自相关统计局",
                    pos_left="center"
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                toolbox_opts=opts.ToolboxOpts(is_show=True, orient="vertical", pos_left="left", pos_top="center"),
                legend_opts=opts.LegendOpts(pos_bottom="-1%")  # 将图例放在图的最下方
            )
        )

        line = (
            Line()
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis(
                series_name="居民人均可支配收入_累计增长",
                yaxis_index=1,
                y_axis=y5_data,
                label_opts=opts.LabelOpts(is_show=False),
            )
        )

        return bar.overlap(line)
    else:
        print("没有查询到数据")


def create_gauge(year, gini_value):
    gauge = (
        Gauge()
        .set_global_opts(title_opts=opts.TitleOpts(title=f"{year}年居民人均可支配收入基尼系数"))
        .add(
            series_name="",
            data_pair=[("基尼系数", format(gini_value, '.3f'))],
            min_=0.46,
            max_=0.47,
            detail_label_opts=opts.GaugeDetailOpts(
                offset_center=[0, "10%"],
                font_size=16,
                color="#2ecc71"
            )
        )
        .set_series_opts(
            pointer_opts=opts.GaugePointerOpts(
                width=8,
            )
        )
    )
    return gauge


@site_obj.register_chart(
    name="gini",
    title="居民人均可支配收入基尼系数",
    description=GINI,
    catalog="1",
    top=1,
)
def create_gini_timeline():
    years = range(2014, 2022)  # Range of years
    timeline_gauge = Timeline(init_opts=opts.InitOpts(width="1000px", height="600px"))

    for year in years:
        # Fetch data for the current year
        data = Gini.objects.filter(year_quarter__startswith=f"{year}").values_list("year_quarter", "gini_coefficient")

        year_data = [item[1] for item in data if item[0].startswith(str(year))]
        if year_data:
            timeline_gauge.add(create_gauge(year, year_data[0]), time_point=str(year))

    timeline_gauge.add_schema(play_interval=1000)
    return timeline_gauge


@site_obj.register_chart(
    name="Income_classify_pie",
    title="居民人均可支配收入的分类收入情况（饼图）",
    description=INCOME_CLASSIFY_PIE_DESCRIPTION,
    catalog="2",
    top=2,
)
def generate_Chart2():
    def fetch_data_from_model():
        queryset = IncomeData.objects.values(
            'year_quarter',
            'total_income',
            'wage_income',
            'business_income',
            'property_income',
            'transfer_income'
        )

        data = {}
        for entry in queryset:
            year_quarter = entry['year_quarter']
            data[year_quarter] = [
                {"name": key, "value": value}
                for key, value in entry.items() if key != 'year_quarter'
            ]
        return data

    # Get pie chart for a specific year and quarter
    def get_year_quarter_pie_chart(year_quarter: str):
        year_quarter_data = total_data[year_quarter]
        names = [x["name"] for x in year_quarter_data]
        values = [x["value"] for x in year_quarter_data]

        pie = (
            Pie()
            .add(
                series_name="",
                data_pair=[list(z) for z in zip(names, values)],
                radius=["20%", "40%"],
                label_opts=opts.LabelOpts(
                    position="outside",
                    formatter="{b}: {c}"
                )
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(
                    title="Total residents' pension disposable income",
                    subtitle="数据来自相关统计局",
                    pos_left="center"
                ),
                legend_opts=opts.LegendOpts(
                    type_="scroll",
                    pos_left="75%",
                    orient="vertical",
                    pos_top="10%"
                )
            )
        )
        return pie

    # Fetch the data from the database model
    total_data = fetch_data_from_model()

    timeline_pie = Timeline(init_opts=opts.InitOpts(width="1000px", height="600px"))

    # Generate the pie chart for each year and quarter
    for year_quarter in sorted(total_data.keys()):
        pie = get_year_quarter_pie_chart(year_quarter)
        timeline_pie.add(pie, time_point=year_quarter)

    timeline_pie.add_schema(
        is_auto_play=True,
        play_interval=1000,
        orient="horizontal",
        pos_left="10",
        pos_right="10",
        pos_bottom="10",
    )

    return timeline_pie


# Fetch data from the Django model and format it
def fetch_data_from_model():
    queryset = IncomeData.objects.values(
        'year_quarter',
        'total_income',
        'wage_income',
        'business_income',
        'property_income',
        'transfer_income'
    )

    data = []
    for entry in queryset:
        row = [
            entry['year_quarter'],
            entry['total_income'],
            entry['wage_income'],
            entry['business_income'],
            entry['property_income'],
            entry['transfer_income']
        ]
        data.append(row)
    return data


@site_obj.register_chart(
    name="Income_classify",
    title="居民人均可支配收入的分类收入情况（柱状图，折线图）",
    description=INCOME_CLASSIFY,
    catalog="3",
    top=3,
)
def bar_01():
    data = fetch_data_from_model()
    if len(data) > 0:
        if len(data) > 0:
            x_data = [item[0] for item in data]  # Assuming the first column contains the x-axis labels
            y1_data = [float(item[2]) for item in data]  # Assuming the third column contains data for y1_axis
            y2_data = [float(item[3]) for item in data]  # Assuming the fourth column contains data for y2_axis
            y3_data = [float(item[4]) for item in data]  # Assuming the fifth column contains data for y3_axis
            y4_data = [float(item[5]) for item in data]  # Assuming the sixth column contains data for y4_axis

            bar = (
                Bar()
                .add_xaxis(xaxis_data=x_data)
                .add_yaxis(series_name="居民人均可支配工资性收入_累计值", y_axis=y1_data,
                           label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis(series_name="居民人均可支配经营净收入_累计值", y_axis=y2_data,
                           label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis(series_name="居民人均可支配财产净收入_累计值", y_axis=y3_data,
                           label_opts=opts.LabelOpts(is_show=False))
                .add_yaxis(series_name="居民人均可支配转移净收入_累计值", y_axis=y4_data,
                           label_opts=opts.LabelOpts(is_show=False))
                .extend_axis(
                    yaxis=opts.AxisOpts(
                        name="元",
                        type_="value",
                        min_=0,
                        max_=40000,
                        interval=5000,
                        axislabel_opts=opts.LabelOpts(formatter="{value}￥"),
                    )
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="Disposable income national", subtitle="数据来自相关统计局",
                                              pos_left="center"),
                    tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                    toolbox_opts=opts.ToolboxOpts(is_show=True, orient="vertical", pos_left="left",
                                                  pos_top="center"),
                    legend_opts=opts.LegendOpts(pos_bottom="-1%")  # 将图例放在图的最下方
                )

            )

            line = (
                Line()
                .add_xaxis(xaxis_data=x_data)
                .add_yaxis(
                    series_name="居民人均可支配收入_累计值",
                    yaxis_index=1,
                    y_axis=[float(item[1]) for item in data],  # Assuming the second column contains the data
                    label_opts=opts.LabelOpts(is_show=False),

                )
            )

            return bar.overlap(line)
        else:
            print("没有查询到数据")


@site_obj.register_chart(
    name="Income_classify_3D",
    title="居民人均可支配收入的分类收入情况（3D柱状图）",
    description=INCOME_CLASSIFY_3D,
    catalog="2",
    top=2,
)
def generate_Chart4():
    try:
        # Fetching data using Django QuerySet API
        income_data_objects = IncomeData.objects.all().order_by('year_quarter')

        years_quarters = [obj.year_quarter for obj in income_data_objects]
        income_wage = [obj.wage_income for obj in income_data_objects]
        income_business = [obj.business_income for obj in income_data_objects]
        income_property = [obj.property_income for obj in income_data_objects]
        income_transfer = [obj.transfer_income for obj in income_data_objects]

        def generate_data():
            data = []
            for i, yq in enumerate(years_quarters):
                stack_value = 0
                for j, income_type in enumerate([income_wage, income_business, income_property, income_transfer]):
                    stack_value += income_type[i]
                    data.append([i, j, stack_value])
                # Adding total income item
                data.append([i, 4, stack_value])  # 4 is the y-axis index for the new "Total Income" item
            return data

        bar3d = Bar3D()
        bar3d.add(
            "",
            generate_data(),
            shading="lambert",
            xaxis3d_opts=opts.Axis3DOpts(data=years_quarters, type_="category"),
            yaxis3d_opts=opts.Axis3DOpts(data=["工资收入", "经营收入", "财产收入", "转移收入", "总收入"],
                                         type_="category"),
            zaxis3d_opts=opts.Axis3DOpts(type_="value"),
        )
        bar3d.set_global_opts(title_opts=opts.TitleOpts(title="居民人均可支配收入3D柱状图", pos_left="center"))
        bar3d.set_series_opts(**{"stack": "stack"})
        return bar3d

    except ObjectDoesNotExist:
        raise Exception("No data found for one or more quarters")  # You could use a custom exception here


@site_obj.register_chart(
    name="Income_quarter",
    title="居民人均可支配收入（按季节）",
    description=INCOME_QUARTER_DESCRIPTION,
    catalog="2",
)
def generate_chart3():
    try:
        # Fetch data from the IncomeData model
        income_data_objects = IncomeData.objects.all().order_by('year_quarter')

        x_data = [obj.year_quarter for obj in income_data_objects]
        y1_data = [obj.wage_income for obj in income_data_objects]
        y2_data = [obj.business_income for obj in income_data_objects]
        y3_data = [obj.property_income for obj in income_data_objects]
        y4_data = [obj.transfer_income for obj in income_data_objects]
        y_total_data = [obj.total_income for obj in income_data_objects]

        bar = (
            Bar()
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis("Wage Income", y1_data, label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("Business Income", y2_data, label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("Property Income", y3_data, label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("Transfer Income", y4_data, label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="Disposable Income National",
                                          subtitle="Data sourced from relevant statistical bureau"),
                tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
                toolbox_opts=opts.ToolboxOpts(is_show=True),
                legend_opts=opts.LegendOpts(pos_bottom="0%"),
            )
        )

        line = (
            Line()
            .add_xaxis(xaxis_data=x_data)
            .add_yaxis("Total Income", y_total_data, label_opts=opts.LabelOpts(is_show=False))
        )

        return bar.overlap(line)

    except ObjectDoesNotExist:
        print("No data found for one or more quarters")


@site_obj.register_chart(
    name="Income_province",
    title="居民人均可支配收入（按省份）",
    description=INCOME_PROVENCE_DESCRIPTION,
    catalog="2",
    top=0,
)
def generate_income_timeline():
    # Fetch data from the database and format
    def fetch_data_from_db():
        data = {}
        for year in range(2014, 2022):  # Change the range according to your database data
            queryset = RegionData.objects.filter(year=year)
            data[year] = [{"name": obj.region, "value": obj.metric_value} for obj in queryset]
        return data

    # Total data
    total_data = {}
    total_data["dataIncome"] = fetch_data_from_db()

    # Create timeline object
    timeline = Timeline(init_opts=opts.InitOpts(width="1000px", height="600px"))

    # Add maps to timeline
    for y in range(2014, 2022):  # Adjust the range based on your data
        sorted_year_data = total_data["dataIncome"][y]
        names = [x["name"] for x in sorted_year_data]
        values = [x["value"] for x in sorted_year_data]

        map_ = (
            Map()
            .add(
                series_name="",
                data_pair=[list(z) for z in zip(names, values)],
                maptype="china",
                is_map_symbol_show=False,
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="{}年全国各省份居民人均可支配收入".format(y),
                                          subtitle="数据来自相关统计局"),
                visualmap_opts=opts.VisualMapOpts(
                    max_=100000,
                    is_piecewise=True,
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
        timeline.add(map_, "{}年".format(y))
    return timeline


@site_obj.register_chart(
    name="Income_province_tree",
    title="居民人均可支配收入（按省份，树形图）",
    description=INCOME_PROVENCE_TREE_DESCRIPTION,
    catalog="2",
    top=1,
)
def generate_tree_timeline():
    # Function to fetch data from a database using the RegionData model
    def fetch_data_from_database(year):
        queryset = RegionData.objects.filter(year=year)
        return [
            {"name": obj.region, "value": obj.metric_value} for obj in queryset
        ]

    # Convert data to tree structure
    def convert_to_tree_structure(year_data, area_dict):
        tree_data = []
        for area, provinces in area_dict.items():
            children = []
            for item in year_data:
                if item["name"][:-1] in provinces:
                    children.append({"name": f"{item['name']} ({item['value']})"})
            tree_data.append({"name": area, "children": children})
        return [{"name": "全国", "children": tree_data}]

    # Area dictionary (as per original code)
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

    # Create timeline object
    timeline = Timeline(init_opts=opts.InitOpts(width="1200px", height="800px"))

    # Generate tree and add to timeline
    for y in range(2014, 2022):
        year_data = fetch_data_from_database(y)
        tree_data = convert_to_tree_structure(year_data, area_dict)

        tree = (
            Tree()
            .add("", tree_data, collapse_interval=2)
            .set_global_opts(title_opts=opts.TitleOpts(title=f"Tree for Year {y}"))
        )
        timeline.add(tree, f"{y}年")

    return timeline


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




