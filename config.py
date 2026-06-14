'''
是否是国际服
'''
IS_INTERNATIONAL_VERSION = False

'''
鱼仓满时是否自动卖鱼，关闭此选项后，鱼仓满时会停止脚本
'''
SELL_FISH = True

'''
缺少鱼饵时是否自动购买鱼饵，关闭此选项后，缺少鱼饵时会停止脚本
'''
BUY_BAIT = True

'''
每次购买几组鱼饵（每组99个）
'''
BUY_BAIT_STACK_COUNT = 5

'''
钓鱼时绿条中间多少比例的范围内不移动黄色光标（范围0~1）
'''
GREEN_BAR_SAFE_PROPORTION = 0.4

'''
是否保存钓鱼条调试图片
'''
SAVE_FISH_BAR_DEBUG_IMAGE = False

'''
指定时间（分钟）后自动结束钓鱼，如为 False 或 0 则不结束
实际成功钓到一条鱼后才开始计时，持续时间并不严格为指定时间，每次成功钓鱼后才为时间检查节点
'''
TIMER_FINISHED_MINUTES=0
#可选择结束钓鱼后直接关机，有的程序可能会导致关机卡住，因此请保证没有其他程序影响关机
POWER_OFF=False
