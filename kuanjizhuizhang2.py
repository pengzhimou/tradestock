# 克隆自聚宽文章：https://www.joinquant.com/post/32543
# 标题：【不含未来！】宽基etf轮动8年50倍年化60%
# 作者：将就

# 克隆自聚宽文章：https://www.joinquant.com/post/32543
# 标题：【不含未来！】宽基etf轮动8年50倍年化60%
# 作者：将就

# 克隆自聚宽文章：https://www.joinquant.com/post/10087
# 标题：短周期交易型阿尔法191因子 之 Alpha011
# 作者：JoinQuant-PM
"""
问题1：121行，否是有未来函数，include_now=True表示读取当天的日K线，但程序在11:15分执行
问题2：107行，BBI指标，include_now=True也是包含当天K线

程序运行原理：
1、给定大盘指数：上证，深成指，创业板指数，中证1000指数，红利指数
2、给定14只大盘指数基金
3、判断指数基金是否正常上市
4、判断5个大盘是否处于上涨趋势（获取大盘上涨最大的代码）
5、判断14只大盘指数基金的BBI指标（多空指标）
6、如果涨幅最好的股票5日，20日，60日移动指数空头排列，则不开仓（程序停止）**作用不明显
   如果涨幅最好的大盘指数是上涨的，则买入BBI指标中多头最强的指数基金（大概率也是指数对应的基金)

7、第二天重新进入1-5的判断，如果大盘都是下跌的，清仓
                            如果表现做好的大盘是上涨的，则买入BBI最小的基金，清空持有的基金
                            如果买入BBI最小的基金已经持仓，则不操作
如果大盘不好，清仓规避；
如果大盘上涨，则买入BBI指标中的多头最强的，第二天循环判断
程序实现了亏小，赢大的可能
牛市11：15开盘原因：各大机构收盘后制定第二套买卖计划，会在9点30到10点30之间完成，有买入的这段
时间都是上涨的，之后会有一段时间回落，在回落时间段内，我们买入。
每年根据上年的在各时间段的收益做微调，可适当提高收益率（经过测试无效）
短期大盘趋势向下的时候停止操作，启动update_niu_signal函数，趋势向上则屏蔽掉这个函数
BBI是多空指数，用于追涨。
ETF300的20日均线朝下表示：趋势向下,收益率不变的情况下，
测试区间：20-1-1~21-7-27 收益60.0%,  回撤10.54%， 没有均线判断：收益60.0%， 回撤18.11%
测试区间：18-1-1~20-1-1  收益25.96%，回撤20.88%， 没有均线判断：收益48.71%，回撤11.86%
测试区间：16-1-1~18-1-1  收益10.45%，回撤19.06%， 没有均线判断：收益5.02%， 回撤15.35%
测试区间：14-1-1~16-1-1  收益130.7%，回撤15.98%， 没有均线判断：收112.62%， 回撤40.7%
测试区间：12-1-1~14-1-1  收益38.58%，回撤14.90%， 没有均线判断：收57.14%，  回撤13.87%
趋势线改为ETF300基金当前价格在20日线上操作，20日线下暂停
测试区间：20-1-1~21-7-27 收益62.1%,  回撤10.54%， 没有均线判断：收益60.0%， 回撤18.11%
测试区间：18-1-1~20-1-1  收益25.96%，回撤20.88%， 没有均线判断：收益48.71%，回撤11.86%
测试区间：16-1-1~18-1-1  收益10.45%，回撤19.06%， 没有均线判断：收益5.02%， 回撤15.35%
测试区间：14-1-1~16-1-1  收益130.7%，回撤15.98%， 没有均线判断：收112.62%， 回撤40.71%
测试区间：12-1-1~14-1-1  收益59.44%，回撤12.04%， 没有均线判断：收57.14%，  回撤13.87%(ETF没上市）
测试区间：14-1-~21-7-29  收益416.29% 回撤22.10%
"""

# 导入聚宽函数库
import jqdata
# 导入alpha191 因子函数库
from jqlib.technical_analysis  import *
from jqdata import *#import *是另一种导入方法，不用加前缀，比如numpy.array(),用*导入后就可以写成array()

# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
   
    set_slippage(FixedSlippage(0.001))
    set_option("avoid_future_data", True)
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')


    set_benchmark('000300.XSHG')
    ### 股票相关设定 ###
    # ETF基金场内交易类每笔交易时的手续费是：买入时佣金万分之一点五，卖出时佣金万分之一点五，无印花税, 每笔交易佣金最低扣0块钱
    set_order_cost(OrderCost(close_tax=0.00, open_commission=0.00015, close_commission=0.00015, min_commission=0), type='fund')
    
    ## 运行函数（reference_security为运行时间的参考标的；传入的标的只做种类区分，因此传入'000300.XSHG'或'510300.XSHG'是一样的）
      # 开盘前运行
    # run_daily(market_open, time='9:34')
    #   # 开盘时运行
    run_daily(make_sure_etf_ipo, time='9:15')
    # run_weekly(market_buy, weekday=1,time='14:30')
    # run_weekly(market_buy, weekday=2,time='11:15')
    run_daily(market_buy, time='11:15')
    # run_daily(market_buy, time='14:45')

    # 最强指数涨了多少，可以开仓
    g.dapan_threshold =0#大盘阈值
    g.signal= 'BUY'
    g.niu_signal = 1 # 牛市就上午开仓，熊市就下午
    g.position = 1
    # 基金上市了多久可以买卖
    g.lag1 =20
    g.decrease_days = 0 #递减
    g.increase_days = 0 #递增
    # bbi动量的单位
    g.unit = '30m'
    # g.bond = '511880.XSHG'
    #python中的中括号[ ]，代表list列表数据类型
    g.zs_list = [
        '000001.XSHG', # 上证
        '399001.XSHE', # 深成指
        '399006.XSHE', # 创业板指数
        '000852.XSHG', # 中证1000指数
        '000015.XSHG'# 红利指数
        ]
    #python大括号{ }花括号：代表dict字典数据类型，字典是由键对值组组成。冒号':'分开键和值，逗号','隔开组
    # 指数、基金对, 所有想交易的etf都可以，会自动过滤掉交易时没有上市的
    #指数：指数对应的基金
    g.ETF_list =  {
      
        '399905.XSHE':'159902.XSHE',#中小板指
        '399632.XSHE':'159901.XSHE',#深100etf
        '000016.XSHG':'510050.XSHG',#上证50
        '000010.XSHG':'510180.XSHG',#上证180
        
        '000852.XSHG':'512100.XSHG',#中证1000etf
        '399295.XSHE':'159966.XSHE',# 创蓝筹
        '399958.XSHE':'159967.XSHE',# 创成长
        '000015.XSHG':'510880.XSHG',#红利ETF
        '399324.XSHE':'159905.XSHE',#深红利
        '399006.XSHE':'159915.XSHE',#创业板
        '000300.XSHG':'510300.XSHG',#沪深300
        '000905.XSHG':'510500.XSHG',#中证500
        '399673.XSHE':'159949.XSHE',#创业板50
        '000688.XSHG':'588000.XSHG'#科创50

    }
    #复制g.EFT_list到g.not_ipo_list
    #copy() 函数用于复制列表，类似于 a[:]
    g.not_ipo_list = g.ETF_list.copy()
    g.available_indexs = []
##  交易！
def market_buy(context):
    #log.info(context.current_dt.hour)#信息输出：当前时间的小时段
    
    # for etf in g.ETF_targets:
    #建立df_index表，字段为：指数代码，周期动量
    df_index = pd.DataFrame(columns=['指数代码', '周期动量'])
    # 判断四大指数是否值得开仓
    #建立df_incre表，字段为：大盘代码，周期涨幅，当前价格
    df_incre = pd.DataFrame(columns=['大盘代码','周期涨幅','当前价格'])
    """
    BBI2 = BBI(g.available_indexs, check_date=context.current_dt, timeperiod1=3, timeperiod2=6, timeperiod3=12, timeperiod4=24,unit=unit,include_now=True)
    BBI2 = BBI(股票列表, check_date=日期, timeperiod1=统计天数N1, timeperiod2=统计天数N2, timeperiod3=统计天数N3, timeperiod4=统计天数N4,unit=统计周期,include_now=是否包含当前周期)
    返回结果类型：字典(dict)：键(key)为股票代码，值(value)为数据。
    用法注释：1.股价位于BBI 上方，视为多头市场； 2.股价位于BBI 下方，视为空头市场。
    计算方法：BBI=(3日均价+6日均价+12日均价+24日均价)÷4
    判断指数的BBI，多空指数
    """
    unit =g.unit
    BBI2 = BBI(g.available_indexs, check_date=context.current_dt, timeperiod1=3, timeperiod2=6, timeperiod3=12, timeperiod4=24,unit=unit,include_now=True)
    #print("BBI:%s" %BBI2)
    for index in g.available_indexs:#运行中的指数
        df_close = get_bars(index, 1, unit, ['close'],  end_dt=context.current_dt,include_now=True,)['close']#读取index当天的收盘价
        val =   BBI2[index]/df_close[0]#BBI除以交易当天11:15分的价格，大于1表示空头，小于1表示多头
        df_index = df_index.append({'指数代码': index, '周期动量': val}, ignore_index=True)#将数据写入df_index表格，索引重置
    #按'周期动量'进行从大到小的排列。ascending=true表示降序排列,ascending=false表示升序排序，inplace = True：不创建新的对象，直接对原始对象进行修改
    df_index.sort_values(by='周期动量', ascending=False, inplace=True)
    log.info(df_index)
    
    target = df_index['指数代码'].iloc[-1]#读取最后一行的指数代码
    target_bbi = df_index['周期动量'].iloc[-1]#读取最后一行的周期动量

    for index in g.zs_list:#大的指数判断
        df_close = get_bars(index, 2, '1d', ['close'],  end_dt=context.current_dt,include_now=True,)['close']#读取当前日期的前2天日K线图，包括当天的收盘价格，今天的收盘价，这是不是未来指数
        #print(df_close)
        if len(df_close)>1:#表示取得了2天的数据
            
            increase = (df_close[1] - df_close[0]) / df_close[0]#今天的11.15分的收盘价-昨天的收盘价）/昨天的收盘价，大于1表示今天上涨，小于1表示今天下跌
            df_incre = df_incre.append({'大盘代码': index, '周期涨幅': increase,'当前价格':df_close[0]}, ignore_index=True)
    #大盘指数按大到小排列
    df_incre.sort_values(by='周期涨幅', ascending=False, inplace=True)
    print(df_incre)
    #读取最大的大盘代码
    today_increase = df_incre['周期涨幅'].iloc[0]
    today_index_code = df_incre['大盘代码'].iloc[0]
    today_index_close = df_incre['当前价格'].iloc[0]
    holdings = set(context.portfolio.positions.keys())  # 现在持仓的

    update_niu_signal(context,today_index_code)#将今天上涨最大的大盘代码带入函数计算
    if(context.current_dt.hour == 11 and g.niu_signal == 0 and g.signal == 'BUY')    or (context.current_dt.hour == 14 and g.niu_signal == 1):
       log.info('牛熊不匹配，这个时间点不能开仓，并清仓')
       for etf in holdings:
         order_target(etf, 0)#清仓
       return

    if(today_increase>g.dapan_threshold and target_bbi<1):#g.dapan_threshold=0,表示涨幅最好的大盘指数是上涨的，并且 只要BBI小于1，就购买最小的那个指数
        g.signal = 'BUY'
        g.increase_days+=1
        
    else:#否则就清盘卖出
        g.signal = 'CLEAR'
        g.decrease_days+=1
        
    log.info("-------------increase_days----------- %s" % (g.increase_days))
    log.info("-------------decrease_days----------- %s" % (g.decrease_days))
    target_etf = g.ETF_list[target]#读取指数对应的基金
    #cbj=context.portfolio.long_positions#仓位信息
    #for position in list(cbj.values()): 
    #  print("标的:{0},成本价:{1},标的价值:{2}, 建仓时间:{3}".format(position.security, position.acc_avg_cost, position.value, position.init_time))

    if(g.signal == 'CLEAR'):#清盘操作
        
        for etf in holdings:
            
            log.info("----~~~---指数集体下跌，卖出---~~~~~~-------- %s" % (etf))
              
            order_target(etf, 0)
            # order_value(g.bond,context.portfolio.available_cash)
            return
    else:
        for etf in holdings:
            
            if (etf == target_etf):#要买入的指数已经有仓位
                log.info('相同etf，不需要调仓！@')
                return 
            else:#将不是当天要买入的ETF的持仓全部卖掉
                order_target(etf, 0)
                log.info("------------------调仓卖出----------- %s" % (etf))
                
            
        
        log.info("------------------买入----------- %s" % (target))
        order_value(target_etf,context.portfolio.available_cash*g.position)#全部现金买入，g.position应该是仓位数量，这里默认开一个仓
    


def get_before_after_trade_days(date, count, is_before=True):
    """
    来自： https://www.joinquant.com/view/community/detail/c9827c6126003147912f1b47967052d9?type=1
    date :查询日期
    count : 前后追朔的数量
    is_before : True , 前count个交易日  ; False ,后count个交易日
    返回 : 基于date的日期, 向前或者向后count个交易日的日期 ,一个datetime.date 对象
    """
    all_date = pd.Series(get_all_trade_days())#get_all_trade_days() 获取所有交易日
    """
    isinstance() 函数来判断一个对象是否是一个已知的类型，类似 type()
    isinstance(object, classinfo)
    object -- 实例对象。
    classinfo -- 可以是直接或间接类名、基本类型或者由它们组成的元组。
    返回值：如果对象的类型与参数二的类型（classinfo）相同则返回 True，否则返回 False
    str是字符类型
    date:是函数带下来的日期
    datetime.datetime.strptime是日期格式转换函数
    x = datetime.now()#取得当前的时间，格式：2020-05-03 17:08:13.516192
    d = x.date() #格式化：2020-05-03
    """
    if isinstance(date, str):#如果date是字符类型，则修改成日期类型的
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    if isinstance(date, datetime.datetime):#如果date是日期时间类型（年-月-日 时：分：秒），则修改成日期类型的
        date = date.date()

    if is_before:#函数自带的变量
        return all_date[all_date <= date].tail(count).values[0]#tail():读取后几行
    else:
        return all_date[all_date >= date].head(count).values[-1]#head():读取前几行
def make_sure_etf_ipo(context):
    if len(g.not_ipo_list) == 0:#如果列表没有数据，程序结束
        return 
    idxs = []#设置idxs列表变量
    # 确保交易标的已经上市g.lag1个交易日以上
    yesterday = context.previous_date#取得前一交易日的日期
    list_date = get_before_after_trade_days(yesterday, g.lag1)  # 今天的前g.lag1个交易日的日期（注意不是前几个日期，双休日，停牌日不交易）
    all_funds = get_all_securities(types='fund', date=yesterday)  # 上个交易日之前上市的所有基金
    all_idxes = get_all_securities(types='index', date=yesterday)  # 上个交易日之前就已经存在的指数
    for idx in g.not_ipo_list:#按指数做for循环,g.not_ipo_list的键做循环（键=指数，值=基金）
        #print("指数基金：%s" %g.not_ipo_list)
        #print("基金:%s" %g.not_ipo_list[idx])
        #print("指数:%s" %idx)
        if idx in all_idxes.index:#all_idxes.index是指数名称
            #读取all_idxes表中，index为idx的记录，并读取start_date字段的内容（index为序号)
            if all_idxes.loc[idx].start_date <= list_date:  # 指数已经在要求的日期前上市
                #将指数对应的基金赋值给symbol
                symbol = g.not_ipo_list[idx]#g.not_ipo_list[idx]是指数对应的基金，指数用index读取，基金用idx读取
                if symbol in all_funds.index:
                    if all_funds.loc[symbol].start_date <= list_date:  # 对应的基金也已经在要求的日期前上市
                        g.available_indexs.append(idx)  # 则列入可交易对象中(指数）
                        idxs.append(idx) #后面删掉这一条，下次就不用折腾了
    for idx in idxs:#将已经上止的指数删除，剩下的就是没有开盘的指数了
        del g.not_ipo_list[idx]
    #log.info(g.not_ipo_list)
    return

# 短均线金叉，强势期，上午交易
def update_niu_signal(context,index):
    include_now = True#表示读取当天的日K线
    unit='1d'
    
    df_close = get_bars(index, 1, '1d', ['close'],  end_dt=context.current_dt,include_now=include_now,)['close']
    #index是当天涨幅最大的指数
    #5天的指数移动平均线
    ema_short = EMA(index,context.current_dt, timeperiod=2, unit = unit, include_now =include_now, fq_ref_date = None)[index]
    #20天的指数移动平均线
    ema_middle = EMA(index,context.current_dt, timeperiod=3, unit = unit, include_now =include_now, fq_ref_date = None)[index]
    #60天的指数移动平均线
    ema_long = EMA(index,context.current_dt, timeperiod=5, unit = unit, include_now =include_now, fq_ref_date = None)[index]
    """
    #该程序剔除掉了指数空头的时候的操作，当大行情都不好的时候，会处于空仓状态。
    if ema_short> ema_middle>ema_long:#如果5天大于10天大于60天，表示多头排列
        g.position = 1#开仓数量
        
    elif ema_short< ema_middle<ema_long:#5天小10天小60天，表示空头排列    
        
        g.niu_signal = 0#开仓数量=0
    else:
        
        g.niu_signal = 1#应该是常规的震荡排列。
    """
    #-------------------标的指数的60日均线，如果均线朝下表示趋势向下，暂停交易---------------
    ind='510300.XSHG'
    ema_close = get_bars(ind, 1, '1d', ['close'],  end_dt=context.current_dt,include_now=include_now,)['close']
    #当天获取60日均线
    ema_60 = EMA(ind,context.current_dt, timeperiod=20, unit = unit, include_now =include_now, fq_ref_date = None)[ind]
    #前一天的60日均线
    ema_60q = EMA(ind,context.previous_date, timeperiod=20, unit=unit, fq_ref_date = None)[ind]
    if ema_close<ema_60:#当价格低于均线的时候暂停交易
    #if ema_60<ema_60q:#当天均线小于前一天的均线值表示均线往下走，趋势向下
     g.niu_signal = 0#开仓数量=0
     print("ETF300的价格在20日线下，停止开单")
    else:
     g.niu_signal = 1#开仓数量=1
     
    print("20日线：%s" %ema_60)
    print("当日价格：%s" %ema_close)
    #按60天，2015-2021-7-27日，收益率182.29%，最大回撤11.28%
    #按30天，2015-2021-7-27日
    #---------------------结束------------------------------------------------







