from linebot.models import (
    FlexSendMessage, BubbleContainer, BoxComponent,
    ButtonComponent, TextComponent, MessageAction
)

# ✅ 星座按鈕選單

def build_star_menu():
    stars = [
        '牡羊座', '金牛座', '雙子座', '巨蟹座', '獅子座', '處女座',
        '天秤座', '天蠍座', '射手座', '摩羯座', '水瓶座', '雙魚座'
    ]

    rows = []
    for i in range(0, len(stars), 3):
        row = BoxComponent(
            layout='horizontal',
            contents=[
                ButtonComponent(
                    style='primary',
                    color='#C3B091',
                    height='sm',
                    action=MessageAction(label=star, text=star),
                    flex=1
                ) for star in stars[i:i+3]
            ],
            spacing='sm',
            margin='md'
        )
        rows.append(row)

    body = BoxComponent(
        layout='vertical',
        contents=[
            TextComponent(text='請選擇星座 👇', weight='bold', size='md', color='#AF6E4D')
        ] + rows
    )

    bubble = BubbleContainer(body=body)
    return FlexSendMessage(alt_text='星座選單', contents=bubble)

# ✅ 模式選單（配對／今日運勢）
def build_mode_menu():
    modes = ['配對', '今日運勢']
    row = BoxComponent(
        layout='horizontal',
        contents=[
            ButtonComponent(
                style='primary',
                color='#BFA779',
                height='sm',
                action=MessageAction(label=mode, text=mode),
                flex=1
            ) for mode in modes
        ],
        spacing='sm',
        margin='md'
    )
    body = BoxComponent(
        layout='vertical',
        contents=[TextComponent(text='請選擇查詢方式', weight='bold', size='md', color='#AF6E4D'), row]
    )
    bubble = BubbleContainer(body=body)
    return FlexSendMessage(alt_text='請選擇查詢方式', contents=bubble)

# ✅ 運勢結果卡片

def build_horoscope_card(sign, category, data):
    result = data.get("result", "無資料")
    daily_quote = data.get("daily_quote", "")

    body = BoxComponent(
        layout='vertical',
        contents=[
            TextComponent(text=f"{sign} - {category}運勢", weight='bold', size='lg', margin='md'),
            TextComponent(text=result, wrap=True, margin='md', size='md'),
            TextComponent(text=f"📣 今日星語：{daily_quote}", wrap=True, margin='md', size='sm', color='#888888')
        ]
    )
    bubble = BubbleContainer(body=body)
    return FlexSendMessage(alt_text=f"{sign}的{category}運勢", contents=bubble)
